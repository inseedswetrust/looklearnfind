<?php
// Usage: LLF_DATA=/path/to/data php api/tools/seed_demo.php [/path/to/docroot]   (add --clear to remove sample data)
define('LLF', 1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
$_SERVER['DOCUMENT_ROOT'] = $argv[1] ?? realpath(__DIR__ . '/../..');
mb_internal_encoding('UTF-8');
require __DIR__ . '/../lib/core.php';
require __DIR__ . '/../lib/ledger.php';
require __DIR__ . '/../lib/demo.php';
echo json_encode(in_array('--clear', $argv, true) ? demo_clear() : demo_seed()), "\n";
