<?php
// Dev-only router for `php -S`, mirroring the rewrite rules in static/.htaccess.
$root = $_SERVER['DOCUMENT_ROOT'];
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$serve = function ($f) { header('Content-Type: text/html; charset=utf-8'); readfile($f); return true; };
if (preg_match('#^/api/#', $uri)) { chdir($root . '/api'); require $root . '/api/index.php'; return true; }
if (preg_match('#^/look/(L-?\d+)/?$#', $uri)) return $serve($root . '/look/entry/index.html');
if (preg_match('#^/u/([A-Za-z0-9_]+)/?$#', $uri)) return $serve($root . '/u/index.html');
if (preg_match('#^/threads/([a-z0-9-]+)/?$#', $uri, $m) && !is_file($root . "/threads/{$m[1]}/index.html")) return $serve($root . '/threads/t/index.html');
return false;
