<?php
if (!defined('LLF')) { http_response_code(403); exit; }

/** Normalize a pasted URL to [provider, provider_id, canonical_url, format]. Throws ApiError for unsupported links. */
function normalize_video_url($raw) {
    $raw = trim((string)$raw);
    if ($raw === '') fail('Paste a link to a short video.');
    if (!preg_match('#^https?://#i', $raw)) $raw = 'https://' . $raw;
    $p = parse_url($raw);
    if (!$p || empty($p['host'])) fail('That does not look like a link.');
    $host = strtolower(preg_replace('/^(www\.|m\.)/', '', $p['host']));
    $path = $p['path'] ?? '/';
    parse_str($p['query'] ?? '', $qs);

    if ($host === 'youtu.be' && preg_match('#^/([A-Za-z0-9_-]{11})#', $path, $m)) {
        return ['youtube', $m[1], 'https://www.youtube.com/watch?v=' . $m[1], 'video'];
    }
    if (in_array($host, ['youtube.com', 'music.youtube.com'], true)) {
        if (preg_match('#^/shorts/([A-Za-z0-9_-]{11})#', $path, $m)) return ['youtube', $m[1], 'https://www.youtube.com/shorts/' . $m[1], 'short'];
        if ($path === '/watch' && !empty($qs['v']) && preg_match('/^[A-Za-z0-9_-]{11}$/', $qs['v'])) return ['youtube', $qs['v'], 'https://www.youtube.com/watch?v=' . $qs['v'], 'video'];
        if (preg_match('#^/(?:live|embed)/([A-Za-z0-9_-]{11})#', $path, $m)) return ['youtube', $m[1], 'https://www.youtube.com/watch?v=' . $m[1], 'video'];
    }
    if ($host === 'instagram.com') {
        if (preg_match('#^/(?:[A-Za-z0-9._]+/)?(reels?|p|tv)/([A-Za-z0-9_-]{5,20})#', $path, $m)) {
            $kind = $m[1] === 'p' ? 'p' : ($m[1] === 'tv' ? 'tv' : 'reel');
            return ['instagram', $m[2], 'https://www.instagram.com/' . $kind . '/' . $m[2] . '/', $kind === 'reel' ? 'reel' : 'video'];
        }
    }
    if ($host === 'tiktok.com' || substr($host, -11) === '.tiktok.com') {
        if (preg_match('#^/@([A-Za-z0-9._]+)/video/(\d{8,25})#', $path, $m)) {
            return ['tiktok', $m[2], 'https://www.tiktok.com/@' . $m[1] . '/video/' . $m[2], 'short'];
        }
        if (in_array($host, ['vm.tiktok.com', 'vt.tiktok.com'], true) || preg_match('#^/t/#', $path)) {
            $loc = tiktok_resolve($raw);
            if ($loc) return normalize_video_url($loc);
            fail('Could not open that TikTok short link. Paste the full video link instead.');
        }
    }
    fail('That link is not from a supported platform yet. Supported: YouTube Shorts and videos, Instagram Reels, TikTok.');
}

function tiktok_resolve($url) {
    $r = http_fetch($url, ['follow' => false, 'method' => 'HEAD', 'hosts' => ['vm.tiktok.com', 'vt.tiktok.com', 'www.tiktok.com', 'tiktok.com']]);
    if ($r && !empty($r['location'])) return $r['location'];
    return null;
}

/** Minimal, host-allowlisted HTTP fetch with short timeouts. Returns ['code','body','location'] or null. */
function http_fetch($url, $opt = []) {
    $hosts = $opt['hosts'] ?? [];
    $h = strtolower(parse_url($url, PHP_URL_HOST) ?: '');
    if (!$hosts || !in_array($h, $hosts, true)) return null;
    if (!function_exists('curl_init')) return null;
    $ch = curl_init($url);
    $loc = null;
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 6, CURLOPT_CONNECTTIMEOUT => 4,
        CURLOPT_FOLLOWLOCATION => !empty($opt['follow']), CURLOPT_MAXREDIRS => 2,
        CURLOPT_USERAGENT => 'LookLearnFindBot/1.0 (+https://looklearnfind.com)',
        CURLOPT_PROTOCOLS => CURLPROTO_HTTPS | CURLPROTO_HTTP, CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTPS,
        CURLOPT_HEADERFUNCTION => function ($c, $line) use (&$loc) { if (stripos($line, 'location:') === 0) $loc = trim(substr($line, 9)); return strlen($line); },
    ]);
    if (($opt['method'] ?? '') === 'HEAD') curl_setopt($ch, CURLOPT_NOBODY, true);
    if ($ca = getenv('CURL_CA_BUNDLE')) curl_setopt($ch, CURLOPT_CAINFO, $ca);
    if ($px = getenv('HTTPS_PROXY')) curl_setopt($ch, CURLOPT_PROXY, $px);
    $body = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($body === false && $code === 0) return null;
    return ['code' => $code, 'body' => is_string($body) ? $body : '', 'location' => $loc];
}

/**
 * Fetch whatever descriptive metadata the provider exposes without credentials.
 * Returns ['fields' => [...], 'available' => true|false|null]. Every field is provider-sourced.
 * Instagram exposes nothing without an app token, so it returns no fields: the entry falls back to URL + note.
 */
function fetch_video_metadata($provider, $id, $canonical) {
    $f = []; $avail = null;
    if ($provider === 'youtube') {
        $r = http_fetch('https://www.youtube.com/oembed?format=json&url=' . rawurlencode($canonical), ['hosts' => ['www.youtube.com']]);
        if ($r) {
            if ($r['code'] === 200) {
                $j = json_decode($r['body'], true) ?: [];
                $avail = true;
                $f['title'] = $j['title'] ?? ''; $f['creator_name'] = $j['author_name'] ?? ''; $f['creator_url'] = $j['author_url'] ?? '';
                if (!empty($j['author_url']) && preg_match('#/(@[^/?]+)#', $j['author_url'], $m)) $f['creator_handle'] = $m[1];
                $f['thumb_url'] = $j['thumbnail_url'] ?? '';
            } elseif (in_array($r['code'], [401, 403, 404], true)) $avail = false;
        }
        $key = cfg('youtube_api_key');
        if ($key) {
            $r = http_fetch('https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id=' . rawurlencode($id) . '&key=' . rawurlencode($key), ['hosts' => ['www.googleapis.com']]);
            if ($r && $r['code'] === 200) {
                $j = json_decode($r['body'], true) ?: [];
                if (empty($j['items'])) $avail = false;
                else {
                    $it = $j['items'][0]; $avail = true;
                    $f['published_at'] = $it['snippet']['publishedAt'] ?? null;
                    $f['language'] = $it['snippet']['defaultAudioLanguage'] ?? ($it['snippet']['defaultLanguage'] ?? '');
                    $f['caption'] = mb_substr($it['snippet']['description'] ?? '', 0, 500);
                    if (!empty($it['contentDetails']['duration'])) $f['duration_sec'] = iso_duration($it['contentDetails']['duration']);
                }
            }
        }
    } elseif ($provider === 'tiktok') {
        $r = http_fetch('https://www.tiktok.com/oembed?url=' . rawurlencode($canonical), ['hosts' => ['www.tiktok.com']]);
        if ($r) {
            if ($r['code'] === 200) {
                $j = json_decode($r['body'], true) ?: [];
                $avail = true;
                $f['title'] = mb_substr($j['title'] ?? '', 0, 200); $f['creator_name'] = $j['author_name'] ?? '';
                if (!empty($j['author_unique_id'])) $f['creator_handle'] = '@' . $j['author_unique_id'];
                $f['creator_url'] = $j['author_url'] ?? ''; $f['thumb_url'] = $j['thumbnail_url'] ?? '';
            } elseif (in_array($r['code'], [400, 404], true)) $avail = false;
        }
    }
    foreach ($f as $k => $v) if ($v === '' || $v === null) unset($f[$k]);
    return ['fields' => $f, 'available' => $avail];
}

function iso_duration($d) {
    if (!preg_match('/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/', $d, $m)) return null;
    return ((int)($m[1] ?? 0)) * 3600 + ((int)($m[2] ?? 0)) * 60 + (int)($m[3] ?? 0);
}

function orientation_for($provider, $format) {
    if ($provider === 'instagram' && $format === 'reel') return 'portrait';
    if ($provider === 'tiktok') return 'portrait';
    if ($provider === 'youtube' && $format === 'short') return 'portrait';
    return 'unknown';
}

function platform_label($provider, $format = '') {
    if ($provider === 'youtube') return $format === 'short' ? 'YouTube Shorts' : 'YouTube';
    if ($provider === 'instagram') return $format === 'reel' ? 'Instagram Reels' : 'Instagram';
    if ($provider === 'tiktok') return 'TikTok';
    return ucfirst($provider);
}
