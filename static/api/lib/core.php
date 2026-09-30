<?php
// LookLearnFind API core: config, database, sessions, helpers. PHP 7.4+ with pdo_sqlite.
if (!defined('LLF')) { http_response_code(403); exit; }

function cfg($key = null, $default = null) {
    static $c = null;
    if ($c === null) {
        $c = ['admin_emails' => [], 'youtube_api_key' => '', 'mail_from' => 'hello@looklearnfind.com',
              'site_url' => '', 'allow_signup' => true, 'page_size' => 20, 'review_required' => true];
        $f = data_dir() . '/config.php';
        if (is_file($f)) { $x = include $f; if (is_array($x)) $c = array_merge($c, $x); }
    }
    return $key === null ? $c : (array_key_exists($key, $c) ? $c[$key] : $default);
}

function data_dir() {
    static $d = null;
    if ($d) return $d;
    $env = getenv('LLF_DATA');
    if ($env) { @mkdir($env, 0700, true); return $d = rtrim($env, '/'); }
    $root = rtrim($_SERVER['DOCUMENT_ROOT'] ?? __DIR__ . '/../..', '/');
    $up = dirname($root) . '/llf-data';        // outside the web root when possible (like the seeds site)
    if ((is_dir($up) && is_writable($up)) || (!file_exists($up) && is_writable(dirname($up)))) {
        @mkdir($up, 0700, true);
        if (is_dir($up)) return $d = $up;
    }
    $fb = __DIR__ . '/../_data';                // fallback inside api/, denied by .htaccess
    @mkdir($fb, 0700, true);
    return $d = $fb;
}

function docroot() { return rtrim($_SERVER['DOCUMENT_ROOT'] ?? __DIR__ . '/../..', '/'); }

function db() {
    static $pdo = null;
    if ($pdo) return $pdo;
    $path = data_dir() . '/ledger.sqlite';
    $new = !is_file($path);
    $pdo = new PDO('sqlite:' . $path, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);
    $pdo->exec('PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;');
    require_once __DIR__ . '/schema.php';
    schema_migrate($pdo);
    if ($new) @chmod($path, 0600);
    return $pdo;
}

function q($sql, $args = []) { $s = db()->prepare($sql); $s->execute($args); return $s; }
function q1($sql, $args = []) { $r = q($sql, $args)->fetch(); return $r === false ? null : $r; }
function qall($sql, $args = []) { return q($sql, $args)->fetchAll(); }
function qval($sql, $args = []) { $r = q($sql, $args)->fetchColumn(); return $r === false ? null : $r; }
function last_id() { return (int)db()->lastInsertId(); }
function now() { return gmdate('Y-m-d H:i:s'); }

// ---------------------------------------------------------------- responses
class ApiError extends Exception {
    public $status;
    function __construct($msg, $status = 400) { parent::__construct($msg); $this->status = $status; }
}
function fail($msg, $status = 400) { throw new ApiError($msg, $status); }
function out($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PARTIAL_OUTPUT_ON_ERROR);
    exit;
}
function body() {
    static $b = null;
    if ($b !== null) return $b;
    $raw = file_get_contents('php://input');
    $b = [];
    if ($raw !== '' && $raw !== false) {
        $j = json_decode($raw, true);
        if (!is_array($j)) fail('Invalid JSON body');
        $b = $j;
    }
    return $b;
}
function s($v, $max = 500) {           // clean single-line string
    if (!is_string($v) && !is_numeric($v)) return '';
    $v = trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/u', '', (string)$v));
    return mb_substr($v, 0, $max);
}
function st($v, $max = 2000) {         // multi-line text
    return s($v, $max);
}
function arr($v, $max = 20) { return is_array($v) ? array_slice(array_values($v), 0, $max) : []; }
function slugify($t) {
    $t = strtolower(iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $t) ?: $t);
    return trim(preg_replace('/[^a-z0-9]+/', '-', $t), '-');
}
function jdec($s, $d = []) { $x = json_decode((string)$s, true); return is_array($x) ? $x : $d; }

// ---------------------------------------------------------------- request guards
function is_https() { return (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https'); }
function client_ip() { return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0'; }

function same_origin_or_fail() {
    $o = $_SERVER['HTTP_ORIGIN'] ?? '';
    if ($o !== '') {
        $h = parse_url($o, PHP_URL_HOST); $p = parse_url($o, PHP_URL_PORT);
        $host = $_SERVER['HTTP_HOST'] ?? '';
        $oh = $h . ($p ? ':' . $p : '');
        if (strcasecmp($oh, $host) !== 0) fail('Cross-origin request blocked', 403);
    }
}

function rate_limit($key, $max, $window = 3600) {
    $k = $key . '|' . client_ip();
    $t = time() - $window;
    q('DELETE FROM rate WHERE ts < ?', [time() - 86400]);
    $n = (int)qval('SELECT COUNT(*) FROM rate WHERE k=? AND ts>?', [$k, $t]);
    if ($n >= $max) fail('Too many attempts. Please try again later.', 429);
    q('INSERT INTO rate(k, ts) VALUES(?,?)', [$k, time()]);
}

// ---------------------------------------------------------------- sessions
$GLOBALS['LLF_USER'] = false; $GLOBALS['LLF_SESSION'] = null;

function session_start_llf() {
    if ($GLOBALS['LLF_USER'] !== false) return $GLOBALS['LLF_USER'];
    $GLOBALS['LLF_USER'] = null;
    $tok = $_COOKIE['llf'] ?? '';
    if ($tok && preg_match('/^[a-f0-9]{64}$/', $tok)) {
        $row = q1('SELECT s.*, u.id AS uid FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?', [hash('sha256', $tok), time()]);
        if ($row) {
            $GLOBALS['LLF_SESSION'] = $row;
            $GLOBALS['LLF_USER'] = q1('SELECT * FROM users WHERE id=? AND disabled=0', [$row['uid']]);
        }
    }
    return $GLOBALS['LLF_USER'];
}
function me() { return session_start_llf(); }
function require_login() {
    $u = me();
    if (!$u) fail('Please sign in.', 401);
    csrf_check();
    return $u;
}
function require_role($roles) {
    $u = require_login();
    if (!in_array($u['role'], (array)$roles, true)) fail('Editors only.', 403);
    return $u;
}
function is_editor($u) { return $u && in_array($u['role'], ['editor', 'admin'], true); }
function csrf_token() { session_start_llf(); return $GLOBALS['LLF_SESSION']['csrf'] ?? null; }
function csrf_check() {
    $t = $GLOBALS['LLF_SESSION']['csrf'] ?? '';
    $h = $_SERVER['HTTP_X_CSRF'] ?? '';
    if (!$t || !hash_equals($t, $h)) fail('Session expired. Refresh and try again.', 403);
}
function login_user($uid) {
    $tok = bin2hex(random_bytes(32));
    $csrf = bin2hex(random_bytes(16));
    $exp = time() + 60 * 60 * 24 * 30;
    q('INSERT INTO sessions(token_hash,user_id,csrf,expires,created_at) VALUES(?,?,?,?,?)', [hash('sha256', $tok), $uid, $csrf, $exp, now()]);
    $_COOKIE['llf'] = $tok;   // visible to the rest of this request
    setcookie('llf', $tok, ['expires' => $exp, 'path' => '/', 'secure' => is_https(), 'httponly' => true, 'samesite' => 'Lax']);
    q('DELETE FROM sessions WHERE expires<?', [time()]);
}
function logout_user() {
    $tok = $_COOKIE['llf'] ?? '';
    if ($tok) q('DELETE FROM sessions WHERE token_hash=?', [hash('sha256', $tok)]);
    setcookie('llf', '', ['expires' => 1, 'path' => '/', 'secure' => is_https(), 'httponly' => true, 'samesite' => 'Lax']);
}

function audit($action, $target = '', $detail = null) {
    $u = me();
    q('INSERT INTO audit(actor_id, action, target, detail, created_at) VALUES(?,?,?,?,?)',
      [$u ? $u['id'] : null, $action, $target, $detail === null ? null : json_encode($detail, JSON_UNESCAPED_UNICODE), now()]);
}

function public_user($u, $extra = []) {
    return array_merge(['handle' => $u['handle'], 'display_name' => $u['display_name'], 'is_editor' => in_array($u['role'], ['editor', 'admin'], true)], $extra);
}
