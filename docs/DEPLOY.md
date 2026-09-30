# Deploying LookLearnFind to hosting.com (step by step)

You have a ready-made file: **`looklearnfind-site.zip`**. Download it here (it is a public repository, no login needed):

https://github.com/inseedswetrust/looklearnfind/raw/claude/funny-shannon-dg9qoe/release/looklearnfind-site.zip

(Page for the same file: https://github.com/inseedswetrust/looklearnfind/blob/claude/funny-shannon-dg9qoe/release/looklearnfind-site.zip, then click **Download raw file**.)

This site is static pages **plus** a small PHP and SQLite program for the Ledger (accounts, saves, follows, review desk). There is no database server to create: the database is a single file.

> I have not seen your hosting account, so screen names may differ a little. These steps assume the standard **cPanel** panel that hosting.com plans usually include, the same pattern as the In Seeds We Trust site.

## Is it ready to launch?
It is ready to **install and test**. It is **not** ready to announce, because:
- Every story, Find and Ledger row is an illustrative sample.
- The Privacy, Terms, Community, Disclosures, Corrections and Who we are pages are drafts with `[BRACKETED]` blanks, and are hidden from search engines.
- The newsletter stores emails but does not send anything yet.

So the file ships with `robots.txt` set to **keep search engines out**. Follow steps 1 to 7 to install and test. Step 8 is launch day.

## Before you start
1. **Domain.** Make sure `looklearnfind.com` is in your hosting.com account. In cPanel, **Domains** → add it as an add-on domain if it is not there. If it is registered elsewhere, change its **nameservers** to the ones in your hosting.com welcome email. DNS can take a few hours.
2. **Folder.** Install into **this domain's own folder** (for example `/home/ascendan/looklearnfind.com`), **never** into the shared `public_html`. Wherever these steps say "the site folder", use that folder. Leave its existing `cgi-bin` and `php.ini` alone.

## 1. Turn on HTTPS first
The site forces HTTPS. cPanel → **SSL/TLS Status** → select `looklearnfind.com` and `www` → **Run AutoSSL**. Wait for a padlock or "Valid".

## 2. Choose PHP and turn on three extensions
1. cPanel → **MultiPHP Manager** → tick the domain → **PHP 8.1 or newer** → Apply.
2. cPanel → **Select PHP Version** (or **MultiPHP INI Editor**) → **Extensions** → make sure these are ticked: **pdo_sqlite**, **sqlite3**, **curl**, **mbstring**.

## 3. Upload and extract
1. cPanel → **File Manager** → open the site folder.
2. **Settings** (top right) → tick **Show Hidden Files (dotfiles)** → Save.
3. Delete any default placeholder page in the folder.
4. **Upload** → choose `looklearnfind-site.zip` → wait for 100%.
5. Right-click the zip → **Extract** → extract into the site folder itself (not a subfolder).
6. Check that `index.html`, `.htaccess`, and the `api`, `css`, `js`, `img`, `fonts` folders sit **directly in** the site folder. If they landed inside another folder, select them all, **Move** them up one level, and delete the empty folder.
7. Delete the uploaded zip.

## 4. Create the private data folder
1. In File Manager go to your **home directory** (one level **above** the site folder, for example `/home/ascendan`).
2. Click **+ Folder** → name it exactly **`llf-data`** → Create.
3. Right-click it → **Change Permissions** → set **700** (owner only) → Save. Never move it into a website folder. The database and your settings live here, so the public cannot download them.

## 5. Make yourself the admin
1. Inside `llf-data`, click **+ File** → name it `config.php` → open it with **Edit** and paste:

```php
<?php
return [
    'admin_emails' => ['YOUR-EMAIL@example.com'],
    'mail_from'    => 'hello@looklearnfind.com',
    'site_url'     => 'https://looklearnfind.com',
    'allow_signup' => true,
    'youtube_api_key' => '',
];
```

2. Replace `YOUR-EMAIL@example.com` with the email you will sign up with. Save.
3. Optional: create the mailbox `hello@looklearnfind.com` in cPanel → **Email Accounts** so password-reset emails have a real sender.

## 6. Test it (15 minutes)
Open `https://looklearnfind.com/` and check:
1. **Homepage** loads with photos and the header logo. Click through Politics, Topics, Find, Look, About.
2. **API check:** open https://looklearnfind.com/api/me . You should see `{"user":null,"csrf":null}`. If you see an error page instead, re-check step 2.
3. **Create your account:** https://looklearnfind.com/account/?mode=signup using the admin email from step 5. You are now an admin.
4. In File Manager, open `llf-data`. A file **`ledger.sqlite`** should now exist. That proves saves will work.
5. Open https://looklearnfind.com/admin/ . Go to **Sample data** → **Load sample entries** to see the Ledger populated with rows marked **Illustrative**. Then open https://looklearnfind.com/look/ .
6. Try **Save +** on a row, then https://looklearnfind.com/look/add/ with a real YouTube Shorts, Instagram Reel, or TikTok link. Submit it publicly, then approve it in the admin **Queue**.
7. Send a test on https://looklearnfind.com/contact/ and sign up for the newsletter in the yellow band. They are stored in the database (see step 9).
8. Visit https://looklearnfind.com/nope . You should see the friendly 404 page.

**If something fails:** "Something went wrong on our side" on the Ledger usually means a missing PHP extension (step 2) or `llf-data` cannot be written (permissions 700 and owned by your account). If a photo or style is missing, hard refresh (Ctrl+Shift+R).

## 7. Clear the sample data before real use
https://looklearnfind.com/admin/ → **Sample data** → **Clear sample data**. (Your real accounts and saves are not touched.) Then replace the sample stories and Finds with real ones (they live in `content/` in the repository; ask me to swap them and I will rebuild the zip).

## 8. Launch day (only when the content is real)
1. Complete the bracketed fields in the policy pages and have them reviewed. Then I remove the `noindex` flag from those pages and rebuild.
2. In File Manager, open the site folder, delete `robots.txt`, and rename **`robots.launch.txt`** to **`robots.txt`**. That lets Google in.
3. Submit https://looklearnfind.com/sitemap.xml in Google Search Console.

## 9. Day to day
- **Backups:** download `llf-data/ledger.sqlite` from File Manager regularly. It holds accounts, saves, messages and newsletter emails, so keep it private. Members can export their own saves at https://looklearnfind.com/account/ .
- **Reading submissions:** contact and contribution messages and newsletter emails are in tables `messages` and `newsletter` inside `ledger.sqlite`. Nothing is emailed to you automatically yet. Tell me and I will add notifications or connect a mailing service.
- **Updating the site:** I rebuild a new zip. Repeat step 3 (upload, **Extract**, overwrite). `llf-data` is outside the site folder, so updates never touch your data.
- **Editors:** as admin you can promote people at https://looklearnfind.com/admin/ → **People**.
- **YouTube details:** to fill in length and language automatically, create a free YouTube Data API key in Google Cloud and paste it into `youtube_api_key` in `config.php`. Instagram cannot supply details without a Meta app token, so contributors type the creator handle.

## For developers
```
python3 build.py --zip        # writes release/looklearnfind-site.zip
LLF_DATA=/tmp/llfdev LLF_DEV=1 php -S 127.0.0.1:8090 -t dist tests/router.php &
echo '<?php return ["admin_emails"=>["editor@test.local"]];' > /tmp/llfdev/config.php
LLF_DATA=/tmp/llfdev php static/api/tools/seed_demo.php dist
python3 tests/api_test.py && python3 tests/links_test.py && python3 tests/placeholders_test.py
```
