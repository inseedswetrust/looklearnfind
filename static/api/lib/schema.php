<?php
if (!defined('LLF')) { http_response_code(403); exit; }

function schema_migrate(PDO $pdo) {
    $pdo->exec('CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)');
    $v = (int)($pdo->query("SELECT v FROM meta WHERE k='schema'")->fetchColumn() ?: 0);
    if ($v >= 1) return;
    $pdo->exec(<<<'SQL'
CREATE TABLE users(
  id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, handle TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'member',            -- member | editor | admin
  bio TEXT NOT NULL DEFAULT '', looks_for TEXT NOT NULL DEFAULT '', interests TEXT NOT NULL DEFAULT '[]',
  profile_public INTEGER NOT NULL DEFAULT 0, disabled INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE sessions(token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, csrf TEXT NOT NULL, expires INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE resets(token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires INTEGER NOT NULL);
CREATE TABLE rate(k TEXT NOT NULL, ts INTEGER NOT NULL);
CREATE INDEX rate_k ON rate(k, ts);

-- the canonical external video: one row per provider post, regardless of how many people save it
CREATE TABLE videos(
  id INTEGER PRIMARY KEY, provider TEXT NOT NULL, provider_id TEXT NOT NULL, canonical_url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '', caption TEXT NOT NULL DEFAULT '',
  creator_handle TEXT NOT NULL DEFAULT '', creator_name TEXT NOT NULL DEFAULT '', creator_url TEXT NOT NULL DEFAULT '',
  thumb_url TEXT NOT NULL DEFAULT '', orientation TEXT NOT NULL DEFAULT 'unknown',   -- portrait | landscape | unknown
  duration_sec INTEGER, published_at TEXT, language TEXT NOT NULL DEFAULT '',
  field_src TEXT NOT NULL DEFAULT '{}',                  -- field -> provider | human   (imported vs human-entered)
  availability TEXT NOT NULL DEFAULT 'ok',               -- ok | unavailable
  last_checked TEXT, meta_fetched INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active',                 -- active | removed
  ledger_no INTEGER UNIQUE, primary_save_id INTEGER, approved_at TEXT,
  illustrative INTEGER NOT NULL DEFAULT 0, merged_into INTEGER, created_at TEXT NOT NULL,
  UNIQUE(provider, provider_id));
CREATE INDEX videos_active ON videos(status, availability, approved_at);

-- a person's save + note of a video (the human layer)
CREATE TABLE saves(
  id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  note TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT '', topic TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT '',
  visibility TEXT NOT NULL DEFAULT 'private',            -- private | public
  status TEXT NOT NULL DEFAULT 'private',                -- private | pending | approved | rejected | removed
  editor_added INTEGER NOT NULL DEFAULT 0, reject_reason TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, approved_at TEXT,
  UNIQUE(user_id, video_id));
CREATE INDEX saves_video ON saves(video_id, status);
CREATE INDEX saves_user ON saves(user_id, created_at);
CREATE INDEX saves_pub ON saves(status, approved_at);
CREATE TABLE save_threads(save_id INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE, thread TEXT NOT NULL, PRIMARY KEY(save_id, thread));
CREATE INDEX save_threads_t ON save_threads(thread);

-- editors attach a reported story ("Deep dive attached") or a real-world Find to a video
CREATE TABLE video_links(video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE, type TEXT NOT NULL, slug TEXT NOT NULL, PRIMARY KEY(video_id, type, slug));

-- curated threads: file-seeded (data/threads.json) and editor-approved; proposals wait as status 'proposed'
CREATE TABLE threads(
  slug TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '', aliases TEXT NOT NULL DEFAULT '[]',
  category TEXT NOT NULL DEFAULT '', topics TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'approved',               -- approved | proposed | rejected | merged
  source TEXT NOT NULL DEFAULT 'db', merged_into TEXT, proposed_by INTEGER, created_at TEXT NOT NULL);

CREATE TABLE follows(follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, followee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  muted INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, PRIMARY KEY(follower_id, followee_id));
CREATE TABLE collections(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL, premise TEXT NOT NULL DEFAULT '', visibility TEXT NOT NULL DEFAULT 'private', created_at TEXT NOT NULL);
CREATE TABLE collection_items(collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE, save_id INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
  position INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(collection_id, save_id));

CREATE TABLE reports(id INTEGER PRIMARY KEY, video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE, user_id INTEGER, reason TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'open', resolution TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
CREATE TABLE audit(id INTEGER PRIMARY KEY, actor_id INTEGER, action TEXT NOT NULL, target TEXT NOT NULL DEFAULT '', detail TEXT, created_at TEXT NOT NULL);

-- "From the desk": an editor-curated shelf above the public index
CREATE TABLE desk(id INTEGER PRIMARY KEY, title TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', curator_id INTEGER, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL);
CREATE TABLE desk_items(desk_id INTEGER NOT NULL REFERENCES desk(id) ON DELETE CASCADE, video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE, position INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(desk_id, video_id));

CREATE TABLE newsletter(email TEXT PRIMARY KEY, created_at TEXT NOT NULL);
CREATE TABLE messages(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, type TEXT NOT NULL DEFAULT '', name TEXT NOT NULL DEFAULT '', email TEXT NOT NULL DEFAULT '', message TEXT NOT NULL, created_at TEXT NOT NULL);
SQL);
    $pdo->exec("INSERT OR REPLACE INTO meta(k,v) VALUES('schema','1')");
}
