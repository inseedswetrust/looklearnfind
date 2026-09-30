<?php
if (!defined('LLF')) { http_response_code(403); exit; }

/** Mirror data/threads.json (shipped as /threads.json) into the threads table. File threads are always approved. */
function threads_sync() {
    static $done = false;
    if ($done) return; $done = true;
    $f = docroot() . '/threads.json';
    if (!is_file($f)) return;
    $mt = (string)filemtime($f);
    if (qval("SELECT v FROM meta WHERE k='threads_mtime'") === $mt) return;
    $list = json_decode(file_get_contents($f), true) ?: [];
    foreach ($list as $t) {
        q("INSERT INTO threads(slug,title,summary,aliases,category,topics,status,source,created_at) VALUES(?,?,?,?,?,?, 'approved','file',?)
           ON CONFLICT(slug) DO UPDATE SET title=excluded.title, summary=excluded.summary, aliases=excluded.aliases, category=excluded.category, topics=excluded.topics, source='file', status='approved'",
          [$t['slug'], $t['title'], $t['summary'] ?? '', json_encode($t['aliases'] ?? []), $t['category'] ?? '', json_encode($t['topics'] ?? []), now()]);
    }
    q("INSERT OR REPLACE INTO meta(k,v) VALUES('threads_mtime',?)", [$mt]);
}

function thread_row($slug) { threads_sync(); return q1('SELECT * FROM threads WHERE slug=?', [$slug]); }
function thread_public($t) {
    return ['slug' => $t['slug'], 'title' => $t['title'], 'summary' => $t['summary'], 'aliases' => jdec($t['aliases']),
            'category' => $t['category'], 'topics' => jdec($t['topics']), 'status' => $t['status'], 'source' => $t['source']];
}
function threads_approved() {
    threads_sync();
    return array_map('thread_public', qall("SELECT * FROM threads WHERE status='approved' ORDER BY title COLLATE NOCASE"));
}
/** Slugs whose title/aliases match a free-text query (so "mud flood" finds Tartaria). */
function threads_matching($text) {
    $text = mb_strtolower(trim($text));
    if (mb_strlen($text) < 3) return [];
    $hits = [];
    foreach (threads_approved() as $t) {
        foreach (array_merge([$t['title']], $t['aliases']) as $h) {
            $h = mb_strtolower($h);
            if ($h !== '' && (mb_strpos($h, $text) !== false || mb_strpos($text, $h) !== false)) { $hits[] = $t['slug']; break; }
        }
    }
    return $hits;
}

/** Resolve a slug that may have been merged into another. */
function thread_resolve($slug) {
    for ($i = 0; $i < 5; $i++) {
        $t = thread_row($slug);
        if (!$t) return null;
        if ($t['status'] === 'merged' && $t['merged_into']) { $slug = $t['merged_into']; continue; }
        return $t;
    }
    return null;
}

/** Story/Find titles for video_links, from the built search index. */
function content_index() {
    static $idx = null;
    if ($idx !== null) return $idx;
    $idx = [];
    $f = docroot() . '/search-index.json';
    if (is_file($f)) foreach (json_decode(file_get_contents($f), true) ?: [] as $it) {
        if (in_array($it['t'], ['story', 'find'], true)) $idx[$it['t'] . ':' . basename(rtrim($it['url'], '/'))] = ['title' => $it['title'], 'url' => $it['url'], 'type' => $it['t']];
    }
    return $idx;
}
