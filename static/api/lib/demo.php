<?php
if (!defined('LLF')) { http_response_code(403); exit; }
// Illustrative sample data so the Ledger can be seen working before real saves exist.
// Every row is flagged illustrative: handles, notes, dates and thumbnails are stand-ins, not real posts.

function demo_seed() {
    threads_sync();
    if (qval('SELECT COUNT(*) FROM videos WHERE illustrative=1')) return ['seeded' => 0, 'note' => 'Sample data already loaded.'];
    $mk = function ($handle, $name, $role, $bio, $looks, $int) {
        $ex = q1('SELECT id FROM users WHERE handle=?', [$handle]); if ($ex) return (int)$ex['id'];
        q('INSERT INTO users(email,handle,display_name,password_hash,role,bio,looks_for,interests,profile_public,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)',
          [$handle . '@demo.invalid', $handle, $name, password_hash(bin2hex(random_bytes(12)), PASSWORD_DEFAULT), $role, $bio, $looks, json_encode($int), now()]);
        return last_id();
    };
    $ed = $mk('looklearnfind', 'LookLearnFind', 'editor', 'Links the desk keeps coming back to, with a note on why.', 'Clips that hold up when you open the source.', ['politics', 'candidates', 'businesses']);
    $maya = $mk('maya_r', 'Maya R.', 'member', 'Sample profile.', 'Civic life and how it looks up close.', ['politics', 'candidates']);
    $noor = $mk('noor_l', 'Noor L.', 'member', 'Sample profile.', 'Weeknight dinners that work.', ['cooking']);
    $dara = $mk('dara_p', 'Dara P.', 'member', 'Sample profile.', 'Ingredient lists over promises.', ['skincare', 'self-care']);
    $ellis = $mk('ellis_t', 'Ellis T.', 'member', 'Sample profile.', 'Realistic routines.', ['working-out', 'self-improvement']);

    $days = function ($n) { return gmdate('Y-m-d H:i:s', time() - $n * 86400 - 3600); };
    $rows = [
        // user, provider, id, creator, title, thumb, secs, lang, kind, topic, note, threads, ago, links
        [$ed, 'youtube', 'ill0000001', '@localforum', 'The question behind the answer.', '/img/politics-forum.jpg', 128, 'en', 'Debate / response', 'candidates', 'A minute of a town hall tells you what someone said. The full exchange tells you what they actually answered.', ['candidate-forums', 'midterms-2026'], 9, []],
        [$maya, 'youtube', 'ill0000002', '@cityvoices', 'What it looked like at the polling place.', '/img/politics-vote.jpg', 48, 'en', 'Firsthand account', 'politics', 'The interesting part was what people said they came to ask before voting.', ['midterms-2026'], 1, []],
        [$noor, 'instagram', 'ill0000003', '@homecooknotes', 'The little move that changes dinner.', '/img/everyday-cooking.jpg', 72, 'en', 'Demonstration', 'cooking', 'I tried this with what was in my fridge. It made the weeknight version better.', ['weeknight-cooking'], 1, []],
        [$ed, 'youtube', 'ill0000004', '@cornercounter', 'What it takes to keep a small shop open.', '/img/economy-shop.jpg', 154, 'en', 'Visit / tour', 'businesses', 'The owner walks through the choices behind one shelf. More here than a price tag.', ['small-shops', 'grocery-prices'], 2, ['find:talk-to-your-local-grocer']],
        [$dara, 'instagram', 'ill0000005', '@skinquestions', 'Before you believe the skincare promise.', '/img/everyday-home.jpg', 56, 'en', 'Explainer', 'skincare', 'The ingredient list is a better starting place than the before-and-after shot.', ['skincare-claims'], 3, []],
        [$ellis, 'youtube', 'ill0000006', '@movementnotes', 'A better way to start moving again.', '/img/everyday-workout.jpg', 98, 'en', 'Demonstration', 'working-out', 'A realistic routine with an explanation for each choice. Saved this to try later.', ['getting-moving'], 3, []],
        [$maya, 'instagram', 'ill0000007', '@oldtownreels', 'The old buildings that "prove" an erased empire.', '/img/politics-forum.jpg', 83, 'en', 'Idea in progress', 'politics', 'Saved because it makes a huge claim in under a minute and cites nothing. Worth looking at what the maps actually say.', ['tartaria', 'world-fairs'], 4, ['learn:what-was-tartary', 'find:visit-an-old-map-room']],
        [$ed, 'tiktok', '7100000000000000001', '@quotecheck', 'Two quotes for the same job.', '/img/everyday-home.jpg', 61, 'en', 'Explainer', 'home-improvement', 'Shows how two estimates can describe two different jobs. The scope line is where they drift apart.', ['home-estimates'], 5, ['learn:before-you-say-yes-to-the-estimate', 'find:a-written-scope-checklist']],
        [$noor, 'youtube', 'ill0000009', '@priceshelf', 'Following one price from the farm to the shelf.', '/img/economy-shop.jpg', 140, 'en', 'Explainer', 'money', 'One item, every step. Useful for knowing which questions even have answers.', ['grocery-prices'], 6, ['learn:what-goes-into-the-price-you-pay']],
    ];
    $n = 0;
    foreach ($rows as $r) {
        list($uid, $prov, $pid, $creator, $title, $thumb, $secs, $lang, $kind, $topic, $note, $threads, $ago, $links) = $r;
        q("INSERT INTO videos(provider,provider_id,canonical_url,title,creator_handle,thumb_url,orientation,duration_sec,language,field_src,availability,last_checked,illustrative,created_at)
           VALUES(?,?,?,?,?,?,?,?,?,?, 'ok',?,1,?)", [$prov, $pid, '#illustrative', $title, $creator, $thumb, 'portrait', $secs, $lang, json_encode(['title' => 'human', 'creator_handle' => 'human']), now(), $days($ago)]);
        $vid = last_id();
        $t = topic_info($topic);
        q("INSERT INTO saves(user_id,video_id,note,category,topic,kind,visibility,status,editor_added,created_at,updated_at,approved_at) VALUES(?,?,?,?,?,?, 'public','approved',?,?,?,?)",
          [$uid, $vid, $note, $t['category'], $topic, $kind, $uid === $ed ? 1 : 0, $days($ago), $days($ago), $days($ago)]);
        $sid = last_id();
        foreach ($threads as $th) q('INSERT OR IGNORE INTO save_threads(save_id,thread) VALUES(?,?)', [$sid, $th]);
        $no = (int)qval('SELECT COALESCE(MAX(ledger_no),0) FROM videos') + 1;
        q('UPDATE videos SET primary_save_id=?, ledger_no=?, approved_at=? WHERE id=?', [$sid, $no, $days($ago), $vid]);
        foreach ($links as $l) { list($type, $slug) = explode(':', $l); q('INSERT OR IGNORE INTO video_links(video_id,type,slug) VALUES(?,?,?)', [$vid, $type, $slug]); }
        $n++;
    }
    // a second reader's note on the first clip, to show "Open notes"
    $v1 = q1("SELECT id FROM videos WHERE provider_id='ill0000001'");
    q("INSERT INTO saves(user_id,video_id,note,category,topic,kind,visibility,status,editor_added,created_at,updated_at,approved_at) VALUES(?,?,?,?,?,?, 'public','approved',0,?,?,?)",
      [$maya, $v1['id'], 'Watch for what gets dodged. The follow-up at 1:40 is the useful part.', 'politics', 'candidates', 'Debate / response', $days(2), $days(2), $days(2)]);
    // "From the desk"
    q('UPDATE desk SET active=0');
    q('INSERT INTO desk(title,note,curator_id,active,created_at) VALUES(?,?,?,1,?)', ['The midterms shelf', 'A few links we keep coming back to, and why.', $ed, now()]);
    $did = last_id();
    foreach ([$v1['id']] as $i => $vid) q('INSERT INTO desk_items(desk_id,video_id,position) VALUES(?,?,?)', [$did, $vid, $i]);
    // follows: demonstrate the Following feed
    foreach ([$maya, $noor] as $f) q('INSERT OR IGNORE INTO follows(follower_id,followee_id,created_at) VALUES(?,?,?)', [$f, $ed, now()]);
    return ['seeded' => $n];
}

function demo_clear() {
    q('DELETE FROM videos WHERE illustrative=1');
    q("DELETE FROM users WHERE email LIKE '%@demo.invalid'");
    q("DELETE FROM desk WHERE curator_id IS NULL OR curator_id NOT IN (SELECT id FROM users)");
    return ['cleared' => true];
}
