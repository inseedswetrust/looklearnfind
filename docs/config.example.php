<?php
// Copy to  llf-data/config.php  (one level above the website folder), or api/_data/config.php if you cannot create that folder.
return [
    // Anyone who signs up or signs in with one of these emails becomes an admin (can approve editors, load/clear sample data).
    'admin_emails'    => ['you@example.com'],
    // Optional. Lets the Ledger read duration, language and publish date for YouTube links. Without it, YouTube still gives title, creator and thumbnail.
    'youtube_api_key' => '',
    'mail_from'       => 'hello@looklearnfind.com',   // used for password-reset emails
    'site_url'        => 'https://looklearnfind.com',
    'allow_signup'    => true,
];
