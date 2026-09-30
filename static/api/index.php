<?php
// LookLearnFind API router. All requests to /api/* land here (see .htaccess).
define('LLF', 1);
mb_internal_encoding('UTF-8');
require __DIR__ . '/lib/core.php';
require __DIR__ . '/lib/ledger.php';
require __DIR__ . '/lib/social.php';
require __DIR__ . '/lib/admin.php';
require __DIR__ . '/lib/demo.php';

try {
    $path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
    $route = trim(preg_replace('#^.*?/api/#', '', $path), '/');
    if ($route === 'index.php' || $route === '') $route = trim($_GET['r'] ?? '', '/');
    $method = $_SERVER['REQUEST_METHOD'];
    if ($method === 'OPTIONS') { http_response_code(204); exit; }
    $post = $method === 'POST';
    if ($post) {
        same_origin_or_fail();
        if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') === false) fail('Expected JSON', 415);
    } elseif ($method !== 'GET') fail('Method not allowed', 405);
    $b = $post ? body() : [];
    $me = me();
    $size = (int)cfg('page_size', 20);

    switch ($route) {
        // ---- session
        case 'me': out(me_payload($me));
        case 'auth/signup': $post || fail('POST only', 405); out(auth_signup($b));
        case 'auth/login': $post || fail('POST only', 405); out(auth_login($b));
        case 'auth/logout': $post || fail('POST only', 405); if ($me) csrf_check(); logout_user(); out(['ok' => true]);
        case 'auth/reset-request': $post || fail('POST only', 405); out(auth_reset_request($b));
        case 'auth/reset': $post || fail('POST only', 405); out(auth_reset($b));

        // ---- ledger (public reads)
        case 'ledger/list':
            $mode = in_array($_GET['mode'] ?? 'explore', ['explore', 'following', 'mine'], true) ? ($_GET['mode'] ?? 'explore') : 'explore';
            if ($mode !== 'explore' && !$me) fail('Please sign in.', 401);
            out(ledger_list($mode, filters_from($_GET), $me, $_GET['limit'] ?? $size, $_GET['offset'] ?? 0, ($_GET['facets'] ?? '1') !== '0'));
        case 'ledger/shuffle': out(ledger_shuffle(filters_from($_GET), $me));
        case 'ledger/entry': out(ledger_entry(s($_GET['ref'] ?? '', 20), $me));
        case 'ledger/notes': out(['notes' => ledger_notes((int)($_GET['video'] ?? 0))]);
        case 'ledger/desk': out(['desk' => ledger_desk($me)]);
        case 'ledger/suggest': out(['profiles' => profile_suggestions($me)]);

        // ---- ledger (writes)
        case 'ledger/preview': $post || fail('POST only', 405); $u = require_login(); rate_limit('preview', 60, 3600); out(ledger_preview($b['url'] ?? '', $u));
        case 'ledger/save': $post || fail('POST only', 405); $u = require_login(); rate_limit('save', 60, 3600); out(ledger_save($u, $b));
        case 'ledger/visibility':
            $post || fail('POST only', 405); $u = require_login();
            out(['status' => ledger_set_visibility($u, (int)($b['save_id'] ?? 0), ($b['to'] ?? '') === 'public' ? 'public' : 'private', !empty($b['make_profile_public']))]);
        case 'ledger/delete': $post || fail('POST only', 405); $u = require_login(); ledger_delete_save($u, (int)($b['save_id'] ?? 0)); out(['ok' => true]);
        case 'report': $post || fail('POST only', 405); if ($me) csrf_check(); out(report_create($me, $b));

        // ---- threads
        case 'threads':
            $t = threads_approved();
            if (!empty($_GET['q'])) { $needle = mb_strtolower(s($_GET['q'], 60)); $t = array_values(array_filter($t, function ($x) use ($needle) { return mb_strpos(mb_strtolower($x['title'] . ' ' . implode(' ', $x['aliases'])), $needle) !== false; })); }
            out(['threads' => $t]);
        case 'threads/get':
            $t = thread_resolve(s($_GET['slug'] ?? '', 80));
            if (!$t || $t['status'] !== 'approved') fail('Thread not found.', 404);
            out(['thread' => thread_public($t)]);
        case 'threads/propose': $post || fail('POST only', 405); out(threads_propose(require_login(), $b));

        // ---- profiles, follows, collections
        case 'profile': out(profile_get(s($_GET['handle'] ?? '', 30), $me, filters_from($_GET), (int)($_GET['offset'] ?? 0)));
        case 'profile/update': $post || fail('POST only', 405); out(profile_update(require_login(), $b));
        case 'follow': $post || fail('POST only', 405); out(follow_set(require_login(), s($b['handle'] ?? '', 30), true));
        case 'unfollow': $post || fail('POST only', 405); out(follow_set(require_login(), s($b['handle'] ?? '', 30), false));
        case 'mute': $post || fail('POST only', 405); out(follow_mute(require_login(), s($b['handle'] ?? '', 30), !empty($b['muted'])));
        case 'following': $u = me(); $u || fail('Please sign in.', 401); out(['following' => following_list($u)]);
        case 'collection': out(collection_get((int)($_GET['id'] ?? 0), $me));
        case 'collections/create': $post || fail('POST only', 405); out(collection_create(require_login(), $b));
        case 'collections/update': $post || fail('POST only', 405); out(collection_update(require_login(), $b));
        case 'collections/delete': $post || fail('POST only', 405); collection_delete(require_login(), (int)($b['id'] ?? 0)); out(['ok' => true]);
        case 'collections/add': $post || fail('POST only', 405); collection_add(require_login(), (int)($b['id'] ?? 0), (int)($b['save_id'] ?? 0)); out(['ok' => true]);
        case 'collections/remove': $post || fail('POST only', 405); collection_remove(require_login(), (int)($b['id'] ?? 0), (int)($b['save_id'] ?? 0)); out(['ok' => true]);
        case 'export': $u = me(); $u || fail('Please sign in.', 401); export_saves($u, ($_GET['format'] ?? 'json') === 'csv' ? 'csv' : 'json');

        // ---- forms
        case 'newsletter': $post || fail('POST only', 405); out(newsletter_join($b));
        case 'contact': $post || fail('POST only', 405); out(contact_send($b));

        // ---- editors
        case 'admin/summary': require_role(['editor', 'admin']); out(admin_summary());
        case 'admin/queue': $u = require_role(['editor', 'admin']); out(['items' => admin_queue($u)]);
        case 'admin/reports': require_role(['editor', 'admin']); out(['reports' => admin_reports()]);
        case 'admin/threads': require_role(['editor', 'admin']); out(['threads' => admin_threads()]);
        case 'admin/entries': require_role(['editor', 'admin']); out(['entries' => admin_entries(s($_GET['q'] ?? '', 80))]);
        case 'admin/people': require_role(['admin']); out(['people' => admin_people()]);
        case 'admin/audit': require_role(['editor', 'admin']); out(['audit' => admin_audit()]);
        case 'admin/review': $post || fail('POST only', 405); out(admin_review(require_role(['editor', 'admin']), $b));
        case 'admin/entry': $post || fail('POST only', 405); out(admin_entry(require_role(['editor', 'admin']), $b));
        case 'admin/report': $post || fail('POST only', 405); out(admin_report_resolve(require_role(['editor', 'admin']), $b));
        case 'admin/thread': $post || fail('POST only', 405); out(admin_thread(require_role(['editor', 'admin']), $b));
        case 'admin/desk': $post || fail('POST only', 405); out(admin_desk(require_role(['editor', 'admin']), $b));
        case 'admin/user': $post || fail('POST only', 405); out(admin_users(require_role(['admin']), $b));

        case 'admin/demo': $post || fail('POST only', 405); require_role(['admin']); out(($b['action'] ?? '') === 'clear' ? demo_clear() : demo_seed());

        default: fail('Not found', 404);
    }
} catch (ApiError $e) {
    out(['error' => $e->getMessage()], $e->status);
} catch (Throwable $e) {
    error_log('[llf] ' . $e->getMessage() . ' @ ' . $e->getFile() . ':' . $e->getLine());
    out(['error' => getenv('LLF_DEV') ? $e->getMessage() : 'Something went wrong on our side. Please try again.'], 500);
}
