<?php
if (!defined('LLF')) { http_response_code(403); exit; }

function admin_summary() {
    return [
        'pending' => (int)qval("SELECT COUNT(*) FROM saves WHERE status='pending'"),
        'reports' => (int)qval("SELECT COUNT(*) FROM reports WHERE status='open'"),
        'thread_proposals' => (int)qval("SELECT COUNT(*) FROM threads WHERE status='proposed'"),
        'entries' => (int)qval("SELECT COUNT(*) FROM videos WHERE ledger_no IS NOT NULL AND primary_save_id IS NOT NULL AND status='active'"),
        'unavailable' => (int)qval("SELECT COUNT(*) FROM videos WHERE availability='unavailable' AND status='active'"),
    ];
}

function admin_queue($me) {
    $rows = qall("SELECT s.id AS sid, s.video_id AS vid FROM saves s WHERE s.status='pending' ORDER BY s.updated_at ASC LIMIT 100");
    $items = [];
    foreach ($rows as $r) {
        $h = hydrate($r['vid'], $r['sid'], $me); if (!$h) continue;
        $prop = array_map(function ($t) { return ['slug' => $t['thread'], 'title' => $t['title']]; },
            qall("SELECT st.thread, t.title FROM save_threads st JOIN threads t ON t.slug=st.thread WHERE st.save_id=? AND t.status='proposed'", [$r['sid']]));
        $h['proposed_threads'] = $prop;
        $h['all_threads'] = array_map(function ($t) { return $t['thread']; }, qall('SELECT thread FROM save_threads WHERE save_id=?', [$r['sid']]));
        $h['already_in_index'] = (bool)q1('SELECT 1 FROM videos WHERE id=? AND primary_save_id IS NOT NULL', [$r['vid']]);
        $h['contributor'] = q1('SELECT handle, display_name, email, created_at FROM users WHERE id=(SELECT user_id FROM saves WHERE id=?)', [$r['sid']]);
        $items[] = $h;
    }
    return $items;
}

function admin_review($actor, $b) {
    $sid = (int)($b['save_id'] ?? 0);
    $s = q1('SELECT * FROM saves WHERE id=?', [$sid]);
    if (!$s) fail('Save not found.', 404);
    $action = $b['action'] ?? '';
    // optional edits made during review (correct tags without touching the original post)
    if (!empty($b['edits']) && is_array($b['edits'])) {
        $e = $b['edits']; $set = [];
        if (isset($e['topic'])) { if ($e['topic'] !== '' && !topic_info($e['topic'])) fail('Unknown topic.'); $set['topic'] = s($e['topic'], 40); if ($e['topic'] !== '' && empty($e['category'])) $set['category'] = topic_info($e['topic'])['category']; }
        if (isset($e['category'])) { if ($e['category'] !== '' && !category_ok($e['category'])) fail('Unknown subject.'); $set['category'] = s($e['category'], 40); }
        if (isset($e['kind'])) { if ($e['kind'] !== '' && !in_array($e['kind'], site_data()['kinds'], true)) fail('Unknown kind.'); $set['kind'] = s($e['kind'], 40); }
        if (isset($e['note'])) $set['note'] = st($e['note'], 600);
        if ($set) {
            q('UPDATE saves SET ' . implode(',', array_map(function ($k) { return "$k=?"; }, array_keys($set))) . ', updated_at=? WHERE id=?', array_merge(array_values($set), [now(), $sid]));
            audit('review.edit', 'save:' . $sid, $set);
        }
        if (isset($e['threads']) && is_array($e['threads'])) {
            threads_sync();
            q('DELETE FROM save_threads WHERE save_id=?', [$sid]);
            foreach (arr($e['threads'], 8) as $t) { $r = thread_resolve(s($t, 80)); if ($r && in_array($r['status'], ['approved', 'proposed'], true)) q('INSERT OR IGNORE INTO save_threads(save_id,thread) VALUES(?,?)', [$sid, $r['slug']]); }
            audit('review.threads', 'save:' . $sid);
        }
    }
    if ($action === 'approve') {
        approve_save($sid);
        q('UPDATE saves SET editor_added=editor_added WHERE id=?', [$sid]);
        audit('review.approve', 'save:' . $sid);
    } elseif ($action === 'reject') {
        $why = st($b['reason'] ?? '', 300);
        q("UPDATE saves SET status='rejected', visibility='private', reject_reason=?, updated_at=? WHERE id=?", [$why, now(), $sid]);
        repair_primary($s['video_id']);
        audit('review.reject', 'save:' . $sid, ['reason' => $why]);
    } elseif ($action !== 'edit') fail('Unknown action.');
    return ['ok' => true];
}

function admin_entry($actor, $b) {
    $vid = (int)($b['video_id'] ?? 0);
    $v = q1('SELECT * FROM videos WHERE id=?', [$vid]);
    if (!$v) fail('Entry not found.', 404);
    $a = $b['action'] ?? '';
    switch ($a) {
        case 'remove':
            q("UPDATE videos SET status='removed' WHERE id=?", [$vid]); break;
        case 'restore':
            q("UPDATE videos SET status='active' WHERE id=?", [$vid]); break;
        case 'unavailable':
            q("UPDATE videos SET availability='unavailable', last_checked=? WHERE id=?", [now(), $vid]); break;
        case 'available':
            q("UPDATE videos SET availability='ok', last_checked=? WHERE id=?", [now(), $vid]); break;
        case 'recheck':
            $m = fetch_video_metadata($v['provider'], $v['provider_id'], $v['canonical_url']);
            if ($m['available'] !== null) q('UPDATE videos SET availability=?, last_checked=? WHERE id=?', [$m['available'] ? 'ok' : 'unavailable', now(), $vid]);
            else q('UPDATE videos SET last_checked=? WHERE id=?', [now(), $vid]);
            $res = ['availability' => $m['available'] === null ? 'unknown' : ($m['available'] ? 'ok' : 'unavailable')];
            audit('entry.recheck', 'video:' . $vid, $res); return $res + ['ok' => true];
        case 'edit':
            $src = jdec($v['field_src']); $set = [];
            foreach (['title' => 200, 'creator_handle' => 60, 'creator_name' => 80, 'language' => 10] as $k => $max) if (isset($b[$k])) { $set[$k] = s($b[$k], $max); $src[$k] = 'human'; }
            if (array_key_exists('duration', $b)) { $set['duration_sec'] = parse_duration($b['duration']); $src['duration_sec'] = 'human'; }
            if (!empty($b['published_at'])) { $set['published_at'] = s($b['published_at'], 30); $src['published_at'] = 'human'; }
            if ($set) q('UPDATE videos SET ' . implode(',', array_map(function ($k) { return "$k=?"; }, array_keys($set))) . ', field_src=? WHERE id=?', array_merge(array_values($set), [json_encode($src), $vid]));
            break;
        case 'set_primary':
            $s = q1("SELECT id FROM saves WHERE id=? AND video_id=? AND status='approved'", [(int)($b['save_id'] ?? 0), $vid]);
            if (!$s) fail('That save is not an approved public save of this video.');
            q('UPDATE videos SET primary_save_id=? WHERE id=?', [$s['id'], $vid]); break;
        case 'set_links':
            q('DELETE FROM video_links WHERE video_id=?', [$vid]);
            $idx = content_index();
            foreach (['learn' => 'story', 'find' => 'find'] as $type => $k) foreach (arr($b[$type] ?? [], 10) as $slug) {
                $slug = s($slug, 120);
                if (isset($idx[$k . ':' . $slug])) q('INSERT OR IGNORE INTO video_links(video_id,type,slug) VALUES(?,?,?)', [$vid, $type, $slug]);
            }
            break;
        case 'merge':
            $into = q1('SELECT * FROM videos WHERE id=?', [(int)($b['into'] ?? 0)]);
            if (!$into || (int)$into['id'] === $vid) fail('Pick a different entry to merge into.');
            foreach (qall('SELECT * FROM saves WHERE video_id=?', [$vid]) as $s) {
                $dup = q1('SELECT id FROM saves WHERE user_id=? AND video_id=?', [$s['user_id'], $into['id']]);
                if ($dup) q('DELETE FROM saves WHERE id=?', [$s['id']]); else q('UPDATE saves SET video_id=? WHERE id=?', [$into['id'], $s['id']]);
            }
            q('INSERT OR IGNORE INTO video_links(video_id,type,slug) SELECT ?,type,slug FROM video_links WHERE video_id=?', [$into['id'], $vid]);
            q("UPDATE videos SET status='removed', merged_into=?, primary_save_id=NULL WHERE id=?", [$into['id'], $vid]);
            repair_primary($into['id']);
            if (!q1('SELECT ledger_no FROM videos WHERE id=? AND ledger_no IS NOT NULL', [$into['id']]) && ($p = q1("SELECT primary_save_id FROM videos WHERE id=?", [$into['id']])) && $p['primary_save_id']) assign_primary($into['id'], $p['primary_save_id']);
            break;
        default: fail('Unknown action.');
    }
    audit('entry.' . $a, 'video:' . $vid, array_diff_key($b, ['action' => 1]));
    return ['ok' => true];
}

function admin_reports() {
    return array_map(function ($r) {
        $v = q1('SELECT * FROM videos WHERE id=?', [$r['video_id']]);
        return ['id' => (int)$r['id'], 'reason' => $r['reason'], 'detail' => $r['detail'], 'status' => $r['status'], 'created_at' => $r['created_at'], 'resolution' => $r['resolution'],
                'video' => $v ? video_public($v) : null,
                'reporter' => $r['user_id'] ? (q1('SELECT handle FROM users WHERE id=?', [$r['user_id']])['handle'] ?? null) : null];
    }, qall("SELECT * FROM reports WHERE status='open' ORDER BY id ASC LIMIT 100"));
}
function admin_report_resolve($actor, $b) {
    $r = q1('SELECT * FROM reports WHERE id=?', [(int)($b['report_id'] ?? 0)]);
    if (!$r) fail('Report not found.', 404);
    $st = ($b['action'] ?? '') === 'dismiss' ? 'dismissed' : 'resolved';
    q('UPDATE reports SET status=?, resolution=? WHERE id=?', [$st, st($b['note'] ?? '', 300), $r['id']]);
    audit('report.' . $st, 'report:' . $r['id']);
    return ['ok' => true];
}

function admin_threads() {
    threads_sync();
    return array_map(function ($t) {
        $x = thread_public($t); $x['proposed_by'] = $t['proposed_by'] ? (q1('SELECT handle FROM users WHERE id=?', [$t['proposed_by']])['handle'] ?? null) : null;
        $x['uses'] = (int)qval('SELECT COUNT(*) FROM save_threads WHERE thread=?', [$t['slug']]);
        return $x;
    }, qall("SELECT * FROM threads WHERE status IN ('proposed') ORDER BY created_at"));
}
function admin_thread($actor, $b) {
    threads_sync();
    $a = $b['action'] ?? ''; $slug = s($b['slug'] ?? '', 80);
    if ($a === 'create') {
        $title = s($b['title'] ?? '', 80); if (mb_strlen($title) < 3) fail('Give the thread a name.');
        $slug = slugify($title); if (thread_row($slug)) fail('That thread already exists.', 409);
        q("INSERT INTO threads(slug,title,summary,aliases,category,topics,status,source,created_at) VALUES(?,?,?,?,?,?, 'approved','db',?)",
          [$slug, $title, st($b['summary'] ?? '', 280), json_encode(array_values(array_filter(array_map(function ($x) { return s($x, 60); }, arr($b['aliases'] ?? [], 10))))), s($b['category'] ?? '', 40), json_encode(arr($b['topics'] ?? [], 6)), now()]);
        audit('thread.create', 'thread:' . $slug); return ['ok' => true, 'slug' => $slug];
    }
    $t = thread_row($slug);
    if (!$t) fail('Thread not found.', 404);
    if ($a === 'approve') {
        $title = s($b['title'] ?? $t['title'], 80) ?: $t['title'];
        q("UPDATE threads SET status='approved', title=?, summary=?, aliases=?, category=?, topics=? WHERE slug=?",
          [$title, st($b['summary'] ?? $t['summary'], 280), json_encode(isset($b['aliases']) ? array_values(array_filter(array_map(function ($x) { return s($x, 60); }, arr($b['aliases'], 10)))) : jdec($t['aliases'])),
           isset($b['category']) ? s($b['category'], 40) : $t['category'], json_encode(isset($b['topics']) ? arr($b['topics'], 6) : jdec($t['topics'])), $slug]);
    } elseif ($a === 'reject') {
        q("UPDATE threads SET status='rejected' WHERE slug=?", [$slug]);
        q('DELETE FROM save_threads WHERE thread=?', [$slug]);
    } elseif ($a === 'merge') {
        $into = thread_resolve(s($b['into'] ?? '', 80));
        if (!$into || $into['slug'] === $slug || $into['status'] !== 'approved') fail('Pick an approved thread to merge into.');
        $al = array_values(array_unique(array_merge(jdec($into['aliases']), [$t['title']], jdec($t['aliases']))));
        q('UPDATE threads SET aliases=? WHERE slug=?', [json_encode($al), $into['slug']]);
        q('INSERT OR IGNORE INTO save_threads(save_id,thread) SELECT save_id, ? FROM save_threads WHERE thread=?', [$into['slug'], $slug]);
        q('DELETE FROM save_threads WHERE thread=?', [$slug]);
        q("UPDATE threads SET status='merged', merged_into=? WHERE slug=?", [$into['slug'], $slug]);
    } else fail('Unknown action.');
    audit('thread.' . $a, 'thread:' . $slug);
    return ['ok' => true];
}

function admin_desk($actor, $b) {
    $ids = array_values(array_unique(array_map('intval', arr($b['video_ids'] ?? [], 12))));
    $title = s($b['title'] ?? '', 80); if (mb_strlen($title) < 3) fail('Give the shelf a title.');
    q('UPDATE desk SET active=0');
    q('INSERT INTO desk(title,note,curator_id,active,created_at) VALUES(?,?,?,1,?)', [$title, st($b['note'] ?? '', 240), $actor['id'], now()]);
    $did = last_id(); $pos = 0;
    foreach ($ids as $id) if (q1("SELECT 1 FROM videos WHERE id=? AND primary_save_id IS NOT NULL", [$id])) q('INSERT INTO desk_items(desk_id,video_id,position) VALUES(?,?,?)', [$did, $id, $pos++]);
    audit('desk.set', 'desk:' . $did);
    return ['ok' => true, 'id' => $did];
}

function admin_users($actor, $b) {
    if ($actor['role'] !== 'admin') fail('Admins only.', 403);
    $u = q1('SELECT * FROM users WHERE handle=?', [strtolower(s($b['handle'] ?? '', 30))]);
    if (!$u) fail('User not found.', 404);
    $role = $b['role'] ?? '';
    if (!in_array($role, ['member', 'editor', 'admin'], true)) fail('Unknown role.');
    q('UPDATE users SET role=? WHERE id=?', [$role, $u['id']]);
    if (isset($b['disabled'])) q('UPDATE users SET disabled=? WHERE id=?', [$b['disabled'] ? 1 : 0, $u['id']]);
    audit('user.role', 'user:' . $u['handle'], ['role' => $role]);
    return ['ok' => true];
}
function admin_people() {
    return array_map(function ($u) { return ['handle' => $u['handle'], 'display_name' => $u['display_name'], 'role' => $u['role'], 'email' => $u['email'], 'disabled' => (bool)$u['disabled'], 'profile_public' => (bool)$u['profile_public']]; },
        qall('SELECT * FROM users ORDER BY created_at DESC LIMIT 200'));
}
function admin_audit() {
    return qall('SELECT a.id, a.action, a.target, a.detail, a.created_at, u.handle AS actor FROM audit a LEFT JOIN users u ON u.id=a.actor_id ORDER BY a.id DESC LIMIT 100');
}
function admin_entries($q) {
    $like = '%' . str_replace(['%', '_'], ['\\%', '\\_'], mb_strtolower($q)) . '%';
    $rows = qall("SELECT id FROM videos WHERE (LOWER(title) LIKE ? ESCAPE '\\' OR LOWER(creator_handle) LIKE ? ESCAPE '\\' OR canonical_url LIKE ? ESCAPE '\\' OR ledger_no=?) ORDER BY id DESC LIMIT 30", [$like, $like, $like, (int)preg_replace('/\D/', '', $q)]);
    return array_map(function ($r) { $v = q1('SELECT * FROM videos WHERE id=?', [$r['id']]); $x = video_public($v); $x['status'] = $v['status']; $x['in_index'] = (bool)$v['primary_save_id']; $x['links'] = links_for($v['id']); return $x; }, $rows);
}
