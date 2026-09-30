<?php
if (!defined('LLF')) { http_response_code(403); exit; }

// ---------------------------------------------------------------- auth
function me_payload($u) {
    if (!$u) return ['user' => null, 'csrf' => null];
    return ['user' => [
        'id' => (int)$u['id'], 'email' => $u['email'], 'handle' => $u['handle'], 'display_name' => $u['display_name'], 'role' => $u['role'],
        'bio' => $u['bio'], 'looks_for' => $u['looks_for'], 'interests' => jdec($u['interests']), 'profile_public' => (bool)$u['profile_public'],
        'is_editor' => is_editor($u),
        'collections' => array_map(function ($c) { return ['id' => (int)$c['id'], 'title' => $c['title'], 'visibility' => $c['visibility']]; },
                                   qall('SELECT id,title,visibility FROM collections WHERE user_id=? ORDER BY id', [$u['id']])),
    ], 'csrf' => csrf_token()];
}

function auth_signup($b) {
    if (!cfg('allow_signup')) fail('Sign-ups are closed right now.', 403);
    rate_limit('signup', 10, 3600);
    $email = strtolower(s($b['email'] ?? '', 200)); $pw = (string)($b['password'] ?? '');
    $handle = strtolower(s($b['handle'] ?? '', 30)); $name = s($b['display_name'] ?? '', 60);
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Enter a valid email.');
    if (strlen($pw) < 8) fail('Use a password of at least 8 characters.');
    if (!preg_match('/^[a-z0-9_]{3,24}$/', $handle)) fail('Handles are 3 to 24 letters, numbers, or underscores.');
    if (in_array($handle, ['admin', 'editor', 'looklearnfind', 'api', 'me', 'support', 'root', 'system'], true)) fail('That handle is reserved.');
    if ($name === '') $name = $handle;
    if (q1('SELECT 1 FROM users WHERE email=?', [$email])) fail('That email already has an account. Try signing in.', 409);
    if (q1('SELECT 1 FROM users WHERE handle=?', [$handle])) fail('That handle is taken.', 409);
    $role = in_array($email, array_map('strtolower', cfg('admin_emails', [])), true) ? 'admin' : 'member';
    q('INSERT INTO users(email,handle,display_name,password_hash,role,created_at) VALUES(?,?,?,?,?,?)', [$email, $handle, $name, password_hash($pw, PASSWORD_DEFAULT), $role, now()]);
    $id = last_id();
    login_user($id);
    $GLOBALS['LLF_USER'] = false;
    return me_payload(me());
}

function auth_login($b) {
    rate_limit('login', 15, 900);
    $email = strtolower(s($b['email'] ?? '', 200)); $pw = (string)($b['password'] ?? '');
    $u = q1('SELECT * FROM users WHERE email=? AND disabled=0', [$email]);
    if (!$u || !password_verify($pw, $u['password_hash'])) fail('That email and password do not match.', 401);
    if (in_array($email, array_map('strtolower', cfg('admin_emails', [])), true) && $u['role'] !== 'admin') q("UPDATE users SET role='admin' WHERE id=?", [$u['id']]);
    login_user($u['id']);
    $GLOBALS['LLF_USER'] = false;
    return me_payload(me());
}

function auth_reset_request($b) {
    rate_limit('reset', 5, 3600);
    $email = strtolower(s($b['email'] ?? '', 200));
    $u = q1('SELECT * FROM users WHERE email=? AND disabled=0', [$email]);
    if ($u) {
        $tok = bin2hex(random_bytes(24));
        q('DELETE FROM resets WHERE user_id=?', [$u['id']]);
        q('INSERT INTO resets(token_hash,user_id,expires) VALUES(?,?,?)', [hash('sha256', $tok), $u['id'], time() + 3600]);
        $base = cfg('site_url') ?: ((is_https() ? 'https://' : 'http://') . ($_SERVER['HTTP_HOST'] ?? 'looklearnfind.com'));
        $link = $base . '/account/?reset=' . $tok;
        $from = cfg('mail_from');
        @mail($u['email'], 'Reset your LookLearnFind password', "Use this link within an hour to choose a new password:\n\n$link\n\nIf you did not ask for this, you can ignore it.", "From: LookLearnFind <$from>\r\n");
        if (getenv('LLF_DEV')) return ['ok' => true, 'dev_link' => $link];
    }
    return ['ok' => true];   // same answer whether or not the account exists
}

function auth_reset($b) {
    rate_limit('reset2', 10, 3600);
    $pw = (string)($b['password'] ?? '');
    if (strlen($pw) < 8) fail('Use a password of at least 8 characters.');
    $r = q1('SELECT * FROM resets WHERE token_hash=? AND expires>?', [hash('sha256', (string)($b['token'] ?? '')), time()]);
    if (!$r) fail('That reset link has expired. Request a new one.', 400);
    q('UPDATE users SET password_hash=? WHERE id=?', [password_hash($pw, PASSWORD_DEFAULT), $r['user_id']]);
    q('DELETE FROM resets WHERE user_id=?', [$r['user_id']]);
    q('DELETE FROM sessions WHERE user_id=?', [$r['user_id']]);
    login_user($r['user_id']);
    $GLOBALS['LLF_USER'] = false;
    return me_payload(me());
}

// ---------------------------------------------------------------- profile + follow
function profile_update($u, $b) {
    $name = s($b['display_name'] ?? $u['display_name'], 60) ?: $u['display_name'];
    $bio = st($b['bio'] ?? $u['bio'], 400); $looks = st($b['looks_for'] ?? $u['looks_for'], 240);
    $int = array_values(array_filter(array_map(function ($x) { $x = s($x, 40); return topic_info($x) ? $x : null; }, arr($b['interests'] ?? jdec($u['interests']), 12))));
    $pub = array_key_exists('profile_public', $b) ? (empty($b['profile_public']) ? 0 : 1) : (int)$u['profile_public'];
    q('UPDATE users SET display_name=?, bio=?, looks_for=?, interests=?, profile_public=? WHERE id=?', [$name, $bio, $looks, json_encode($int), $pub, $u['id']]);
    if ($pub === 0) {
        // a private profile keeps everything private: pull public saves out of the index
        $vids = qall("SELECT DISTINCT video_id FROM saves WHERE user_id=? AND status IN ('approved','pending')", [$u['id']]);
        q("UPDATE saves SET visibility='private', status='private', approved_at=NULL WHERE user_id=? AND status IN ('approved','pending')", [$u['id']]);
        foreach ($vids as $r) repair_primary($r['video_id']);
    }
    return me_payload(q1('SELECT * FROM users WHERE id=?', [$u['id']]));
}

function profile_get($handle, $me, $f, $offset) {
    $u = q1('SELECT * FROM users WHERE handle=? AND disabled=0', [strtolower($handle)]);
    if (!$u) fail('Profile not found.', 404);
    $isme = $me && (int)$me['id'] === (int)$u['id'];
    $base = ['handle' => $u['handle'], 'display_name' => $u['display_name'], 'is_editor' => $u['role'] !== 'member', 'joined' => substr($u['created_at'], 0, 10)];
    if (!$u['profile_public'] && !$isme) return $base + ['private' => true];
    $following = $me && !$isme ? q1('SELECT muted FROM follows WHERE follower_id=? AND followee_id=?', [$me['id'], $u['id']]) : null;
    $f['by'] = null;
    $args = []; $w = ledger_where('profile', $f, $me, $args);
    $args2 = array_merge([$u['id']], $args);
    $from = ledger_from('profile');
    $rows = qall("SELECT v.id AS vid, p.id AS pid $from WHERE p.user_id=? AND $w ORDER BY COALESCE(p.approved_at,p.created_at) DESC, p.id DESC LIMIT 20 OFFSET " . (int)$offset, $args2);
    $total = (int)qval("SELECT COUNT(*) $from WHERE p.user_id=? AND $w", $args2);
    $items = []; foreach ($rows as $r) { $h = hydrate($r['vid'], $r['pid'], $me); if ($h) $items[] = $h; }
    $cols = qall("SELECT c.* FROM collections c WHERE c.user_id=? AND c.visibility='public' ORDER BY c.id", [$u['id']]);
    $collections = array_map(function ($c) {
        return ['id' => (int)$c['id'], 'title' => $c['title'], 'premise' => $c['premise'],
                'count' => (int)qval("SELECT COUNT(*) FROM collection_items ci JOIN saves s ON s.id=ci.save_id JOIN videos v ON v.id=s.video_id WHERE ci.collection_id=? AND s.status='approved' AND v.status='active'", [$c['id']])];
    }, $cols);
    return $base + ['private' => false, 'bio' => $u['bio'], 'looks_for' => $u['looks_for'], 'interests' => jdec($u['interests']), 'is_me' => $isme,
                    'profile_public' => (bool)$u['profile_public'], 'following' => $following ? true : false, 'muted' => $following ? (bool)$following['muted'] : false,
                    'total' => $total, 'items' => $items, 'collections' => $collections, 'offset' => (int)$offset];
}

function follow_set($u, $handle, $on) {
    $t = q1('SELECT * FROM users WHERE handle=? AND disabled=0', [strtolower($handle)]);
    if (!$t) fail('Profile not found.', 404);
    if ((int)$t['id'] === (int)$u['id']) fail('You cannot follow yourself.');
    if ($on) {
        if (!$t['profile_public']) fail('That profile is private.', 403);
        q('INSERT OR IGNORE INTO follows(follower_id,followee_id,created_at) VALUES(?,?,?)', [$u['id'], $t['id'], now()]);
    } else q('DELETE FROM follows WHERE follower_id=? AND followee_id=?', [$u['id'], $t['id']]);
    return ['following' => (bool)$on];
}
function follow_mute($u, $handle, $muted) {
    $t = q1('SELECT id FROM users WHERE handle=?', [strtolower($handle)]);
    if (!$t) fail('Profile not found.', 404);
    q('UPDATE follows SET muted=? WHERE follower_id=? AND followee_id=?', [$muted ? 1 : 0, $u['id'], $t['id']]);
    return ['muted' => (bool)$muted];
}
function following_list($u) {
    return array_map(function ($r) { return ['handle' => $r['handle'], 'display_name' => $r['display_name'], 'muted' => (bool)$r['muted']]; },
        qall('SELECT u.handle,u.display_name,f.muted FROM follows f JOIN users u ON u.id=f.followee_id WHERE f.follower_id=? ORDER BY f.created_at DESC', [$u['id']]));
}
/** Profiles worth following: public profiles with approved saves. No follower counts, no ranking: alphabetical. */
function profile_suggestions($me) {
    $rows = qall("SELECT u.handle,u.display_name,u.looks_for,u.interests,u.role,COUNT(s.id) AS n FROM users u JOIN saves s ON s.user_id=u.id AND s.status='approved'
                  WHERE u.profile_public=1 AND u.disabled=0 GROUP BY u.id ORDER BY u.display_name COLLATE NOCASE LIMIT 12");
    return array_map(function ($r) { return ['handle' => $r['handle'], 'display_name' => $r['display_name'], 'looks_for' => $r['looks_for'], 'interests' => jdec($r['interests']), 'is_editor' => $r['role'] !== 'member', 'public_saves' => (int)$r['n']]; }, $rows);
}

// ---------------------------------------------------------------- collections
function collection_add($u, $cid, $sid) {
    $c = q1('SELECT * FROM collections WHERE id=? AND user_id=?', [$cid, $u['id']]);
    $s = q1('SELECT id FROM saves WHERE id=? AND user_id=?', [$sid, $u['id']]);
    if (!$c || !$s) fail('Collection or save not found.', 404);
    $pos = (int)qval('SELECT COALESCE(MAX(position),0)+1 FROM collection_items WHERE collection_id=?', [$cid]);
    q('INSERT OR IGNORE INTO collection_items(collection_id,save_id,position) VALUES(?,?,?)', [$cid, $sid, $pos]);
}
function collection_create($u, $b) {
    $t = s($b['title'] ?? '', 80);
    if (mb_strlen($t) < 2) fail('Give the collection a title.');
    $vis = ($b['visibility'] ?? 'private') === 'public' ? 'public' : 'private';
    if ($vis === 'public' && !$u['profile_public']) fail('Public collections appear on your profile. Turn on your public profile first.', 409);
    q('INSERT INTO collections(user_id,title,premise,visibility,created_at) VALUES(?,?,?,?,?)', [$u['id'], $t, st($b['premise'] ?? '', 240), $vis, now()]);
    return ['id' => last_id()];
}
function collection_update($u, $b) {
    $c = q1('SELECT * FROM collections WHERE id=? AND user_id=?', [(int)($b['id'] ?? 0), $u['id']]);
    if (!$c) fail('Collection not found.', 404);
    $vis = isset($b['visibility']) ? ($b['visibility'] === 'public' ? 'public' : 'private') : $c['visibility'];
    if ($vis === 'public' && !$u['profile_public']) fail('Public collections appear on your profile. Turn on your public profile first.', 409);
    q('UPDATE collections SET title=?, premise=?, visibility=? WHERE id=?', [s($b['title'] ?? $c['title'], 80) ?: $c['title'], st($b['premise'] ?? $c['premise'], 240), $vis, $c['id']]);
    return ['ok' => true];
}
function collection_get($id, $me) {
    $c = q1('SELECT c.*, u.handle, u.display_name, u.profile_public FROM collections c JOIN users u ON u.id=c.user_id WHERE c.id=?', [(int)$id]);
    if (!$c) fail('Collection not found.', 404);
    $own = $me && (int)$me['id'] === (int)$c['user_id'];
    if (!$own && ($c['visibility'] !== 'public' || !$c['profile_public'])) fail('Collection not found.', 404);
    $rows = qall("SELECT v.id AS vid, s.id AS sid FROM collection_items ci JOIN saves s ON s.id=ci.save_id JOIN videos v ON v.id=s.video_id
                  WHERE ci.collection_id=? AND v.status='active'" . ($own ? '' : " AND s.status='approved'") . ' ORDER BY ci.position', [$c['id']]);
    $items = []; foreach ($rows as $r) { $h = hydrate($r['vid'], $r['sid'], $me); if ($h) $items[] = $h; }
    return ['id' => (int)$c['id'], 'title' => $c['title'], 'premise' => $c['premise'], 'visibility' => $c['visibility'], 'curator' => ['handle' => $c['handle'], 'display_name' => $c['display_name']], 'mine' => $own, 'items' => $items];
}
function collection_remove($u, $cid, $sid) {
    $c = q1('SELECT id FROM collections WHERE id=? AND user_id=?', [$cid, $u['id']]);
    if (!$c) fail('Collection not found.', 404);
    q('DELETE FROM collection_items WHERE collection_id=? AND save_id=?', [$cid, $sid]);
}
function collection_delete($u, $cid) { q('DELETE FROM collections WHERE id=? AND user_id=?', [$cid, $u['id']]); }

// ---------------------------------------------------------------- export, reports, forms
function export_saves($u, $format) {
    $rows = qall("SELECT s.*, v.canonical_url, v.provider, v.title AS vtitle, v.creator_handle, v.duration_sec, v.published_at, v.ledger_no FROM saves s JOIN videos v ON v.id=s.video_id WHERE s.user_id=? ORDER BY s.created_at", [$u['id']]);
    $data = array_map(function ($r) {
        return ['url' => $r['canonical_url'], 'platform' => $r['provider'], 'title' => $r['vtitle'], 'original_creator' => $r['creator_handle'], 'note' => $r['note'],
                'topic' => $r['topic'], 'subject' => $r['category'], 'kind' => $r['kind'], 'visibility' => $r['visibility'], 'status' => $r['status'],
                'threads' => implode(';', array_map(function ($t) { return $t['slug']; }, save_threads_public($r['id']))), 'saved_at' => $r['created_at'], 'ledger' => $r['ledger_no'] ? 'L-' . $r['ledger_no'] : ''];
    }, $rows);
    if ($format === 'csv') {
        header('Content-Type: text/csv; charset=utf-8'); header('Content-Disposition: attachment; filename="my-ledger.csv"');
        $o = fopen('php://output', 'w'); fputcsv($o, $data ? array_keys($data[0]) : ['url']);
        foreach ($data as $d) fputcsv($o, $d); fclose($o); exit;
    }
    header('Content-Type: application/json; charset=utf-8'); header('Content-Disposition: attachment; filename="my-ledger.json"');
    echo json_encode(['exported_at' => now(), 'saves' => $data], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES); exit;
}

function report_create($me, $b) {
    rate_limit('report', 20, 3600);
    $v = q1('SELECT id FROM videos WHERE id=?', [(int)($b['video_id'] ?? 0)]);
    if (!$v) fail('Entry not found.', 404);
    $reason = s($b['reason'] ?? '', 30);
    if (!in_array($reason, ['broken_link', 'wrong_attribution', 'spam', 'needs_context', 'other'], true)) fail('Choose a reason.');
    q('INSERT INTO reports(video_id,user_id,reason,detail,created_at) VALUES(?,?,?,?,?)', [$v['id'], $me ? $me['id'] : null, $reason, st($b['detail'] ?? '', 500), now()]);
    return ['ok' => true];
}

function newsletter_join($b) {
    rate_limit('news', 8, 3600);
    if (!empty($b['website'])) return ['ok' => true];           // honeypot
    $e = strtolower(s($b['email'] ?? '', 200));
    if (!filter_var($e, FILTER_VALIDATE_EMAIL)) fail('Enter a valid email.');
    q('INSERT OR IGNORE INTO newsletter(email,created_at) VALUES(?,?)', [$e, now()]);
    return ['ok' => true];
}

function contact_send($b) {
    rate_limit('contact', 6, 3600);
    if (!empty($b['website'])) return ['ok' => true];
    $kind = ($b['kind'] ?? 'contact') === 'contribution' ? 'contribution' : 'contact';
    $e = strtolower(s($b['email'] ?? '', 200)); $m = st($b['message'] ?? '', 4000);
    if (!filter_var($e, FILTER_VALIDATE_EMAIL)) fail('Enter a valid email.');
    if (mb_strlen($m) < 3) fail('Add a message.');
    q('INSERT INTO messages(kind,type,name,email,message,created_at) VALUES(?,?,?,?,?,?)', [$kind, s($b['type'] ?? '', 60), s($b['name'] ?? '', 80), $e, $m, now()]);
    return ['ok' => true];
}

function threads_propose($u, $b) {
    $title = s($b['title'] ?? '', 80);
    if (mb_strlen($title) < 3) fail('Give the thread a name.');
    $slug = slugify($title);
    if (thread_row($slug)) fail('A thread with that name already exists or is waiting for review.', 409);
    $aliases = array_values(array_filter(array_map(function ($x) { return s($x, 60); }, arr($b['aliases'] ?? [], 8))));
    $cat = s($b['category'] ?? '', 40); if ($cat !== '' && !category_ok($cat)) $cat = '';
    q("INSERT INTO threads(slug,title,summary,aliases,category,status,source,proposed_by,created_at) VALUES(?,?,?,?,?, 'proposed','db',?,?)",
      [$slug, $title, st($b['summary'] ?? '', 280), json_encode($aliases), $cat, $u['id'], now()]);
    return ['slug' => $slug, 'status' => 'proposed'];
}
