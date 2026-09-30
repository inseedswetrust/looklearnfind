<?php
if (!defined('LLF')) { http_response_code(403); exit; }
require_once __DIR__ . '/providers.php';
require_once __DIR__ . '/threads.php';

function site_data() {
    static $d = null;
    if ($d !== null) return $d;
    $f = docroot() . '/site-data.json';
    $d = is_file($f) ? (json_decode(file_get_contents($f), true) ?: []) : [];
    $d += ['categories' => [], 'topics' => [], 'kinds' => [], 'platforms' => []];
    return $d;
}
function topic_info($slug) { foreach (site_data()['topics'] as $t) if ($t['slug'] === $slug) return $t; return null; }
function category_ok($slug) { foreach (site_data()['categories'] as $c) if ($c['slug'] === $slug) return true; return false; }

// ---------------------------------------------------------------- hydration
function save_threads_public($save_id) {
    return qall("SELECT t.slug, t.title FROM save_threads st JOIN threads t ON t.slug=st.thread WHERE st.save_id=? AND t.status='approved' ORDER BY t.title COLLATE NOCASE", [$save_id]);
}

function links_for($video_id) {
    $idx = content_index(); $out = ['learn' => [], 'find' => []];
    foreach (qall('SELECT type, slug FROM video_links WHERE video_id=? ORDER BY slug', [$video_id]) as $l) {
        $k = ($l['type'] === 'learn' ? 'story' : 'find') . ':' . $l['slug'];
        if (isset($idx[$k])) $out[$l['type']][] = ['slug' => $l['slug'], 'title' => $idx[$k]['title'], 'url' => $idx[$k]['url']];
    }
    return $out;
}

function video_public($v) {
    $fmt = (strpos($v['canonical_url'], '/shorts/') !== false || strpos($v['canonical_url'], '/reel/') !== false || $v['provider'] === 'tiktok') ? ($v['provider'] === 'instagram' ? 'reel' : 'short') : '';
    return [
        'id' => (int)$v['id'], 'ledger_no' => $v['ledger_no'] ? (int)$v['ledger_no'] : null,
        'ledger' => $v['ledger_no'] ? 'L / ' . str_pad($v['ledger_no'], 3, '0', STR_PAD_LEFT) : null,
        'provider' => $v['provider'], 'platform' => platform_label($v['provider'], $fmt), 'url' => $v['canonical_url'],
        'title' => $v['title'], 'caption' => $v['caption'], 'creator_handle' => $v['creator_handle'], 'creator_name' => $v['creator_name'],
        'creator_url' => $v['creator_url'], 'thumb' => $v['thumb_url'], 'orientation' => $v['orientation'],
        'duration' => $v['duration_sec'] === null ? null : (int)$v['duration_sec'], 'published_at' => $v['published_at'], 'language' => $v['language'],
        'availability' => $v['availability'], 'last_checked' => $v['last_checked'], 'illustrative' => (bool)$v['illustrative'],
        'field_src' => jdec($v['field_src']),
    ];
}

function hydrate($vid, $sid, $me = null) {
    $v = q1('SELECT * FROM videos WHERE id=?', [$vid]);
    $s = q1('SELECT s.*, u.handle, u.display_name, u.role, u.profile_public FROM saves s JOIN users u ON u.id=s.user_id WHERE s.id=?', [$sid]);
    if (!$v || !$s) return null;
    $mine = $me ? q1('SELECT id, visibility, status FROM saves WHERE user_id=? AND video_id=?', [$me['id'], $vid]) : null;
    $owner = $me && (int)$me['id'] === (int)$s['user_id'];
    $others = (int)qval("SELECT COUNT(*) FROM saves WHERE video_id=? AND status='approved' AND id<>? AND note<>''", [$vid, $sid]);
    $links = links_for($vid);
    $topic = topic_info($s['topic']);
    return [
        'video' => video_public($v),
        'save' => [
            'id' => (int)$s['id'], 'note' => $s['note'], 'category' => $s['category'], 'topic' => $s['topic'], 'topic_label' => $topic ? $topic['label'] : '',
            'kind' => $s['kind'], 'threads' => save_threads_public($sid),
            'saver' => ['handle' => $s['handle'], 'display_name' => $s['display_name'], 'is_editor' => $s['role'] !== 'member', 'profile_public' => (bool)$s['profile_public']],
            'label' => $s['editor_added'] ? 'Editor-added' : 'Reader-added',
            'added_at' => $s['approved_at'] ?: $s['created_at'],
            'visibility' => $owner ? $s['visibility'] : 'public', 'status' => $owner ? $s['status'] : 'approved', 'reject_reason' => $owner ? $s['reject_reason'] : '',
            'mine' => $owner,
        ],
        'links' => $links, 'deep_dive' => count($links['learn']) > 0, 'find_link' => count($links['find']) > 0,
        'other_notes' => $others,
        'my_save' => $mine ? ['id' => (int)$mine['id'], 'visibility' => $mine['visibility'], 'status' => $mine['status']] : null,
    ];
}

// ---------------------------------------------------------------- list / filter
function filters_from($src) {
    $f = [];
    foreach (['q', 'category', 'topic', 'kind', 'length', 'platform', 'lang', 'by', 'thread', 'since', 'sort', 'collection'] as $k) {
        if (isset($src[$k]) && $src[$k] !== '') $f[$k] = s($src[$k], 120);
    }
    foreach (['deep', 'find'] as $k) if (!empty($src[$k])) $f[$k] = 1;
    return $f;
}

function ledger_where($mode, $f, $me, &$args) {
    $w = [];
    if ($mode === 'explore') {
        $w[] = "v.status='active' AND v.availability='ok' AND v.ledger_no IS NOT NULL AND p.status='approved'";
    } elseif ($mode === 'following') {
        $w[] = "v.status='active' AND v.availability='ok' AND p.status='approved' AND u.profile_public=1";
        $w[] = 'p.user_id IN (SELECT followee_id FROM follows WHERE follower_id=? AND muted=0)'; $args[] = $me['id'];
    } elseif ($mode === 'mine') {
        $w[] = "v.status='active' AND p.user_id=?"; $args[] = $me['id'];
    } elseif ($mode === 'profile') {
        $w[] = "v.status='active' AND p.status='approved' AND u.profile_public=1";
    }
    if (!empty($f['category'])) { $w[] = 'p.category=?'; $args[] = $f['category']; }
    if (!empty($f['topic'])) { $w[] = 'p.topic=?'; $args[] = $f['topic']; }
    if (!empty($f['kind'])) { $w[] = 'p.kind=?'; $args[] = $f['kind']; }
    if (!empty($f['platform'])) { $w[] = 'v.provider=?'; $args[] = $f['platform']; }
    if (!empty($f['lang'])) { $w[] = 'v.language=?'; $args[] = $f['lang']; }
    if (!empty($f['by'])) { $w[] = 'EXISTS(SELECT 1 FROM saves sb JOIN users ub ON ub.id=sb.user_id WHERE sb.video_id=v.id AND sb.status=\'approved\' AND ub.handle=?)'; $args[] = strtolower($f['by']); }
    if (!empty($f['since'])) { $w[] = 'COALESCE(p.approved_at,p.created_at)>=?'; $args[] = $f['since']; }
    if (!empty($f['length'])) {
        $map = ['lt1' => 'v.duration_sec<60', 'm1_3' => 'v.duration_sec>=60 AND v.duration_sec<180', 'm3_10' => 'v.duration_sec>=180 AND v.duration_sec<600',
                'gt10' => 'v.duration_sec>=600', 'unknown' => 'v.duration_sec IS NULL'];
        if (isset($map[$f['length']])) $w[] = '(' . $map[$f['length']] . ')';
    }
    if (!empty($f['thread'])) {
        $t = thread_resolve($f['thread']);
        $slugs = [$f['thread']];
        if ($t) { $slugs = [$t['slug']]; foreach (qall("SELECT slug FROM threads WHERE merged_into=?", [$t['slug']]) as $m) $slugs[] = $m['slug']; }
        $in = implode(',', array_fill(0, count($slugs), '?'));
        $w[] = "EXISTS(SELECT 1 FROM save_threads st JOIN saves ss ON ss.id=st.save_id WHERE ss.video_id=v.id AND ss.status='approved' AND st.thread IN ($in))";
        foreach ($slugs as $x) $args[] = $x;
    }
    if (!empty($f['deep'])) $w[] = "EXISTS(SELECT 1 FROM video_links vl WHERE vl.video_id=v.id AND vl.type='learn')";
    if (!empty($f['find'])) $w[] = "EXISTS(SELECT 1 FROM video_links vl WHERE vl.video_id=v.id AND vl.type='find')";
    if (!empty($f['collection'])) { $w[] = 'p.id IN (SELECT save_id FROM collection_items WHERE collection_id=?)'; $args[] = (int)$f['collection']; }
    if (!empty($f['q'])) {
        $terms = preg_split('/\s+/u', mb_strtolower($f['q']), -1, PREG_SPLIT_NO_EMPTY);
        $terms = array_slice($terms, 0, 6);
        $textc = []; $targs = [];
        foreach ($terms as $t) {
            $like = '%' . str_replace(['%', '_'], ['\\%', '\\_'], $t) . '%';
            $textc[] = "(LOWER(v.title) LIKE ? ESCAPE '\\' OR LOWER(v.caption) LIKE ? ESCAPE '\\' OR LOWER(v.creator_handle) LIKE ? ESCAPE '\\' OR LOWER(v.creator_name) LIKE ? ESCAPE '\\' OR LOWER(p.note) LIKE ? ESCAPE '\\' OR LOWER(u.display_name) LIKE ? ESCAPE '\\' OR u.handle LIKE ? ESCAPE '\\')";
            for ($i = 0; $i < 7; $i++) $targs[] = $like;
        }
        $cond = '(' . implode(' AND ', $textc) . ')';
        $th = threads_matching($f['q']);
        if ($th) {
            $in = implode(',', array_fill(0, count($th), '?'));
            $cond = "($cond OR EXISTS(SELECT 1 FROM save_threads st JOIN saves ss ON ss.id=st.save_id WHERE ss.video_id=v.id AND ss.status='approved' AND st.thread IN ($in)))";
            $targs = array_merge($targs, $th);
        }
        $w[] = $cond; $args = array_merge($args, $targs);
    }
    return implode(' AND ', $w);
}

function ledger_from($mode) {
    if ($mode === 'explore') return 'FROM videos v JOIN saves p ON p.id=v.primary_save_id JOIN users u ON u.id=p.user_id';
    return 'FROM saves p JOIN videos v ON v.id=p.video_id JOIN users u ON u.id=p.user_id';
}

function ledger_list($mode, $f, $me, $limit = 20, $offset = 0, $facets = true) {
    $args = []; $where = ledger_where($mode, $f, $me, $args); $from = ledger_from($mode);
    $limit = max(1, min(50, (int)$limit)); $offset = max(0, (int)$offset);
    $sort = $f['sort'] ?? 'added';
    if ($mode === 'explore') $order = $sort === 'posted' ? '(v.published_at IS NULL), v.published_at DESC, v.approved_at DESC, v.id DESC' : 'v.approved_at DESC, v.id DESC';
    else $order = $sort === 'posted' ? '(v.published_at IS NULL), v.published_at DESC, p.id DESC' : 'COALESCE(p.approved_at,p.created_at) DESC, p.id DESC';
    $total = (int)qval("SELECT COUNT(*) $from WHERE $where", $args);
    $rows = qall("SELECT v.id AS vid, p.id AS pid $from WHERE $where ORDER BY $order LIMIT $limit OFFSET $offset", $args);
    $items = [];
    foreach ($rows as $r) { $h = hydrate($r['vid'], $r['pid'], $me); if ($h) $items[] = $h; }
    $res = ['total' => $total, 'items' => $items, 'offset' => $offset, 'limit' => $limit, 'sort' => $sort === 'posted' ? 'posted' : 'added'];
    if ($facets) $res['facets'] = ledger_facets($mode, $f, $me, $from, $where, $args);
    return $res;
}

function ledger_facets($mode, $f, $me, $from, $where, $args) {
    $g = function ($expr, $limit = 40) use ($from, $where, $args) {
        return qall("SELECT $expr AS value, COUNT(*) AS n $from WHERE $where AND $expr IS NOT NULL AND $expr<>'' GROUP BY $expr ORDER BY n DESC, value LIMIT $limit", $args);
    };
    $len = qall("SELECT CASE WHEN v.duration_sec IS NULL THEN 'unknown' WHEN v.duration_sec<60 THEN 'lt1' WHEN v.duration_sec<180 THEN 'm1_3' WHEN v.duration_sec<600 THEN 'm3_10' ELSE 'gt10' END AS value, COUNT(*) AS n $from WHERE $where GROUP BY value", $args);
    $by = qall("SELECT u.handle AS value, u.display_name AS label, COUNT(*) AS n $from WHERE $where AND u.profile_public=1 GROUP BY u.handle ORDER BY n DESC, u.display_name LIMIT 30", $args);
    return ['category' => $g('p.category'), 'topic' => $g('p.topic'), 'kind' => $g('p.kind'), 'platform' => $g('v.provider'), 'lang' => $g('v.language'), 'length' => $len, 'by' => $by];
}

function ledger_shuffle($f, $me) {
    $args = []; $where = ledger_where('explore', $f, $me, $args); $from = ledger_from('explore');
    $total = (int)qval("SELECT COUNT(*) $from WHERE $where", $args);
    if (!$total) return ['total' => 0, 'item' => null];
    $r = q1("SELECT v.id AS vid, p.id AS pid $from WHERE $where ORDER BY RANDOM() LIMIT 1", $args);
    return ['total' => $total, 'item' => hydrate($r['vid'], $r['pid'], $me)];
}

function ledger_entry($ref, $me) {
    if (preg_match('/^L-?(\d+)$/i', $ref, $m)) $v = q1('SELECT * FROM videos WHERE ledger_no=?', [(int)$m[1]]);
    else $v = q1('SELECT * FROM videos WHERE id=?', [(int)$ref]);
    if (!$v || $v['status'] !== 'active') fail('Entry not found.', 404);
    $p = $v['primary_save_id'] ? (int)$v['primary_save_id'] : 0;
    if (!$p) {
        // not in the public index: only the person who saved it (or an editor) can see it
        $mine = $me ? q1('SELECT id FROM saves WHERE user_id=? AND video_id=?', [$me['id'], $v['id']]) : null;
        if ($mine) $p = (int)$mine['id'];
        elseif (is_editor($me)) { $x = q1('SELECT id FROM saves WHERE video_id=? ORDER BY id LIMIT 1', [$v['id']]); $p = $x ? (int)$x['id'] : 0; }
        if (!$p) fail('Entry not found.', 404);
    }
    $h = hydrate($v['id'], $p, $me);
    $h['notes'] = ledger_notes($v['id'], $p);
    return $h;
}

function ledger_notes($vid, $exclude = 0) {
    $rows = qall("SELECT s.id, s.note, s.topic, s.kind, s.editor_added, s.approved_at, s.created_at, u.handle, u.display_name, u.role, u.profile_public
                  FROM saves s JOIN users u ON u.id=s.user_id WHERE s.video_id=? AND s.status='approved' AND s.note<>'' ORDER BY COALESCE(s.approved_at,s.created_at) ASC", [$vid]);
    return array_map(function ($r) use ($exclude) {
        return ['save_id' => (int)$r['id'], 'note' => $r['note'], 'label' => $r['editor_added'] ? 'Editor-added' : 'Reader-added',
                'saver' => ['handle' => $r['handle'], 'display_name' => $r['display_name'], 'is_editor' => $r['role'] !== 'member', 'profile_public' => (bool)$r['profile_public']],
                'added_at' => $r['approved_at'] ?: $r['created_at'], 'primary' => (int)$r['id'] === (int)$exclude];
    }, $rows);
}

function ledger_desk($me) {
    $d = q1('SELECT d.*, u.display_name AS curator FROM desk d LEFT JOIN users u ON u.id=d.curator_id WHERE d.active=1 ORDER BY d.id DESC LIMIT 1');
    if (!$d) return null;
    $items = [];
    foreach (qall("SELECT di.video_id, v.primary_save_id FROM desk_items di JOIN videos v ON v.id=di.video_id
                   WHERE di.desk_id=? AND v.status='active' AND v.availability='ok' AND v.primary_save_id IS NOT NULL ORDER BY di.position", [$d['id']]) as $r) {
        $h = hydrate($r['video_id'], $r['primary_save_id'], $me); if ($h) $items[] = $h;
    }
    return ['id' => (int)$d['id'], 'title' => $d['title'], 'note' => $d['note'], 'curator' => $d['curator'] ?: 'LookLearnFind', 'items' => $items];
}

// ---------------------------------------------------------------- preview + save
function video_row_by($provider, $pid) { return q1('SELECT * FROM videos WHERE provider=? AND provider_id=?', [$provider, $pid]); }

function ledger_preview($url, $me) {
    list($prov, $pid, $canon, $fmt) = normalize_video_url($url);
    $ex = video_row_by($prov, $pid);
    if ($ex && $ex['status'] === 'removed') fail('This link was removed from the Ledger by an editor.');
    if ($ex) {
        $mine = $me ? q1('SELECT id, visibility, status FROM saves WHERE user_id=? AND video_id=?', [$me['id'], $ex['id']]) : null;
        return ['duplicate' => true, 'video' => video_public($ex), 'in_index' => (bool)$ex['primary_save_id'], 'my_save' => $mine ?: null,
                'missing' => ledger_missing_fields($ex)];
    }
    $meta = fetch_video_metadata($prov, $pid, $canon);
    $v = ['id' => 0, 'ledger_no' => null, 'provider' => $prov, 'canonical_url' => $canon, 'title' => '', 'caption' => '', 'creator_handle' => '', 'creator_name' => '',
          'creator_url' => '', 'thumb_url' => '', 'orientation' => orientation_for($prov, $fmt), 'duration_sec' => null, 'published_at' => null, 'language' => '',
          'availability' => $meta['available'] === false ? 'unavailable' : 'ok', 'last_checked' => now(), 'illustrative' => 0, 'field_src' => '{}'];
    foreach ($meta['fields'] as $k => $val) if (array_key_exists($k, $v) || $k === 'duration_sec') $v[$k] = $val;
    $v['field_src'] = json_encode(array_fill_keys(array_keys($meta['fields']), 'provider'));
    return ['duplicate' => false, 'video' => video_public($v), 'missing' => ledger_missing_fields($v), 'metadata_found' => count($meta['fields']) > 0,
            'unavailable' => $meta['available'] === false];
}

function ledger_missing_fields($v) {
    $m = [];
    foreach (['title' => 'title', 'creator_handle' => 'creator_handle'] as $k => $_) if (($v[$k] ?? '') === '') $m[] = $k;
    if (($v['duration_sec'] ?? null) === null) $m[] = 'duration';
    return $m;
}

function parse_duration($v) {
    if ($v === null || $v === '') return null;
    if (is_numeric($v)) return max(0, min(86400, (int)$v));
    if (preg_match('/^(?:(\d+):)?(\d{1,2}):(\d{2})$/', trim((string)$v), $m)) return ((int)$m[1]) * 3600 + ((int)$m[2]) * 60 + (int)$m[3];
    if (preg_match('/^(\d{1,3}):(\d{2})$/', trim((string)$v), $m)) return ((int)$m[1]) * 60 + (int)$m[2];
    return null;
}

function validate_threads($slugs, $proposals, $user) {
    threads_sync();
    $ok = [];
    foreach (arr($slugs, 6) as $sl) {
        $t = thread_resolve(s($sl, 80));
        if ($t && $t['status'] === 'approved') $ok[$t['slug']] = 1;
    }
    foreach (arr($proposals, 3) as $title) {
        $title = s($title, 80);
        if (mb_strlen($title) < 3) continue;
        $slug = slugify($title);
        if (!$slug) continue;
        $ex = thread_row($slug);
        if ($ex) { $t = thread_resolve($slug); if ($t && $t['status'] !== 'rejected') $ok[$t['slug']] = 1; continue; }
        q("INSERT INTO threads(slug,title,status,source,proposed_by,created_at) VALUES(?,?, 'proposed','db',?,?)", [$slug, $title, $user['id'], now()]);
        $ok[$slug] = 1;
    }
    return array_keys($ok);
}

function assign_primary($vid, $sid) {
    $v = q1('SELECT * FROM videos WHERE id=?', [$vid]);
    $no = $v['ledger_no'] ?: ((int)qval('SELECT COALESCE(MAX(ledger_no),0) FROM videos') + 1);
    q('UPDATE videos SET primary_save_id=?, ledger_no=?, approved_at=COALESCE(approved_at,?) WHERE id=?', [$sid, $no, now(), $vid]);
    if (!$v['approved_at']) q('UPDATE videos SET approved_at=? WHERE id=?', [now(), $vid]);
}

function approve_save($sid) {
    $s = q1('SELECT * FROM saves WHERE id=?', [$sid]);
    q("UPDATE saves SET status='approved', visibility='public', approved_at=?, reject_reason='', updated_at=? WHERE id=?", [now(), now(), $sid]);
    $v = q1('SELECT * FROM videos WHERE id=?', [$s['video_id']]);
    if (!$v['primary_save_id']) assign_primary($v['id'], $sid);
}

/** After a save stops being public, repair the video's primary save (or drop it out of the index). */
function repair_primary($vid) {
    $v = q1('SELECT * FROM videos WHERE id=?', [$vid]);
    if (!$v) return;
    $p = $v['primary_save_id'] ? q1("SELECT * FROM saves WHERE id=? AND status='approved'", [$v['primary_save_id']]) : null;
    if ($p) return;
    $n = q1("SELECT id FROM saves WHERE video_id=? AND status='approved' ORDER BY approved_at, id LIMIT 1", [$vid]);
    if ($n) q('UPDATE videos SET primary_save_id=? WHERE id=?', [$n['id'], $vid]);
    else q('UPDATE videos SET primary_save_id=NULL, approved_at=NULL WHERE id=?', [$vid]);
}

function ledger_save($u, $b) {
    $vis = ($b['visibility'] ?? 'private') === 'public' ? 'public' : 'private';
    if (!empty($b['video_id'])) {
        $v = q1('SELECT * FROM videos WHERE id=?', [(int)$b['video_id']]);
        if (!$v || $v['status'] !== 'active') fail('That video is not available.', 404);
    } else {
        list($prov, $pid, $canon, $fmt) = normalize_video_url($b['url'] ?? '');
        $v = video_row_by($prov, $pid);
        if ($v && $v['status'] === 'removed') fail('This link was removed from the Ledger by an editor.');
        if (!$v) {
            $meta = fetch_video_metadata($prov, $pid, $canon);
            $f = $meta['fields']; $src = array_fill_keys(array_keys($f), 'provider');
            $hum = function ($k, $val) use (&$f, &$src) { if (($f[$k] ?? '') === '' && $val !== '' && $val !== null) { $f[$k] = $val; $src[$k] = 'human'; } };
            $hum('title', s($b['title'] ?? '', 200));
            $h = s($b['creator_handle'] ?? '', 60); if ($h !== '' && $h[0] !== '@') $h = '@' . $h;
            $hum('creator_handle', $h);
            $hum('creator_name', s($b['creator_name'] ?? '', 80));
            $hum('language', s($b['language'] ?? '', 10));
            $hum('duration_sec', parse_duration($b['duration'] ?? null));
            q('INSERT INTO videos(provider,provider_id,canonical_url,title,caption,creator_handle,creator_name,creator_url,thumb_url,orientation,duration_sec,published_at,language,field_src,availability,last_checked,meta_fetched,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
              [$prov, $pid, $canon, $f['title'] ?? '', $f['caption'] ?? '', $f['creator_handle'] ?? '', $f['creator_name'] ?? '', $f['creator_url'] ?? '', $f['thumb_url'] ?? '',
               orientation_for($prov, $fmt), $f['duration_sec'] ?? null, $f['published_at'] ?? null, $f['language'] ?? '', json_encode($src),
               $meta['available'] === false ? 'unavailable' : 'ok', now(), $meta['fields'] ? 1 : 0, now()]);
            $v = q1('SELECT * FROM videos WHERE id=?', [last_id()]);
        } else {
            // fill only what is still empty; human corrections to existing records go through editors
            $src = jdec($v['field_src']); $set = [];
            foreach (['title' => s($b['title'] ?? '', 200), 'creator_handle' => ($h = s($b['creator_handle'] ?? '', 60)) !== '' && $h[0] !== '@' ? '@' . $h : $h,
                      'creator_name' => s($b['creator_name'] ?? '', 80), 'language' => s($b['language'] ?? '', 10)] as $k => $val) {
                if ($v[$k] === '' && $val !== '') { $set[$k] = $val; $src[$k] = 'human'; }
            }
            if ($v['duration_sec'] === null && ($d = parse_duration($b['duration'] ?? null)) !== null) { $set['duration_sec'] = $d; $src['duration_sec'] = 'human'; }
            if ($set) {
                $sql = 'UPDATE videos SET ' . implode(',', array_map(function ($k) { return "$k=?"; }, array_keys($set))) . ', field_src=? WHERE id=?';
                q($sql, array_merge(array_values($set), [json_encode($src), $v['id']]));
                $v = q1('SELECT * FROM videos WHERE id=?', [$v['id']]);
            }
        }
    }

    $note = st($b['note'] ?? '', 600);
    $topic = s($b['topic'] ?? '', 40); $kind = s($b['kind'] ?? '', 40); $cat = s($b['category'] ?? '', 40);
    if ($topic !== '' && !topic_info($topic)) fail('Choose a topic from the list.');
    if ($kind !== '' && !in_array($kind, site_data()['kinds'], true)) fail('Choose a kind of post from the list.');
    if ($topic !== '' && $cat === '') { $t = topic_info($topic); $cat = $t['category']; }
    if ($cat !== '' && !category_ok($cat)) fail('Choose a subject from the list.');
    if ($vis === 'public') {
        if (mb_strlen($note) < 8) fail('Tell us why this was worth keeping. One sentence is enough.');
        if ($topic === '' && $cat === '') fail('Choose a subject or topic so people can find it.');
        if ($kind === '') fail('Choose the kind of post.');
        if (!$u['profile_public']) {
            if (empty($b['make_profile_public']) && !is_editor($u)) fail('Public saves appear with your profile. Turn on your public profile to continue.', 409);
            q('UPDATE users SET profile_public=1 WHERE id=?', [$u['id']]);
        }
    }
    $threads = validate_threads($b['threads'] ?? [], $b['propose_threads'] ?? [], $u);

    $ex = q1('SELECT * FROM saves WHERE user_id=? AND video_id=?', [$u['id'], $v['id']]);
    $editor = is_editor($u);
    $status = $vis === 'private' ? 'private' : ($editor ? 'approved' : 'pending');
    $fields_changed = !$ex || $ex['note'] !== $note || $ex['topic'] !== $topic || $ex['kind'] !== $kind || $ex['category'] !== $cat;
    if ($ex) {
        if ($vis === 'public' && $ex['status'] === 'approved' && !$fields_changed) $status = 'approved';
        elseif ($vis === 'public' && $ex['status'] === 'approved' && !$editor) $status = 'pending';   // edits to an approved public save are re-reviewed
        q('UPDATE saves SET note=?, category=?, topic=?, kind=?, visibility=?, status=?, editor_added=?, reject_reason=?, updated_at=? WHERE id=?',
          [$note, $cat, $topic, $kind, $vis, $status, $editor ? 1 : 0, '', now(), $ex['id']]);
        $sid = (int)$ex['id'];
    } else {
        q('INSERT INTO saves(user_id,video_id,note,category,topic,kind,visibility,status,editor_added,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
          [$u['id'], $v['id'], $note, $cat, $topic, $kind, $vis, $status, $editor ? 1 : 0, now(), now()]);
        $sid = last_id();
    }
    q('DELETE FROM save_threads WHERE save_id=?', [$sid]);
    foreach ($threads as $t) q('INSERT INTO save_threads(save_id, thread) VALUES(?,?)', [$sid, $t]);
    if ($status === 'approved') approve_save($sid);
    if ($ex && $status !== 'approved' && $ex['status'] === 'approved') repair_primary($v['id']);
    if (!empty($b['collection_id'])) collection_add($u, (int)$b['collection_id'], $sid);
    if ($editor && $status === 'approved') audit('entry.add', 'save:' . $sid, ['video' => $v['id']]);
    return ['save_id' => $sid, 'video_id' => (int)$v['id'], 'status' => $status, 'duplicate' => (bool)$ex, 'entry' => hydrate($v['id'], $sid, $u)];
}

function ledger_set_visibility($u, $sid, $to, $make_public = false) {
    $s = q1('SELECT * FROM saves WHERE id=? AND user_id=?', [$sid, $u['id']]);
    if (!$s) fail('Save not found.', 404);
    if ($to === 'public') {
        if (mb_strlen($s['note']) < 8 || !$s['kind'] || (!$s['topic'] && !$s['category'])) fail('Add a note, a subject or topic, and the kind of post first. Edit this save, then publish.', 422);
        if (!$u['profile_public']) { if (!$make_public && !is_editor($u)) fail('Public saves appear with your profile. Turn on your public profile to continue.', 409); q('UPDATE users SET profile_public=1 WHERE id=?', [$u['id']]); }
        $st = is_editor($u) ? 'approved' : 'pending';
        q("UPDATE saves SET visibility='public', status=?, updated_at=? WHERE id=?", [$st, now(), $sid]);
        if ($st === 'approved') approve_save($sid);
        return $st;
    }
    q("UPDATE saves SET visibility='private', status='private', approved_at=NULL, updated_at=? WHERE id=?", [now(), $sid]);
    repair_primary($s['video_id']);
    return 'private';
}

function ledger_delete_save($u, $sid) {
    $s = q1('SELECT * FROM saves WHERE id=? AND user_id=?', [$sid, $u['id']]);
    if (!$s) fail('Save not found.', 404);
    q('DELETE FROM saves WHERE id=?', [$sid]);
    repair_primary($s['video_id']);
}
