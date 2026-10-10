# Connecting a Facebook Page

Facebook's API can publish to **Pages only**. Personal profiles and Groups cannot be posted
to by any app — for those, download the post's pack in the app and post by hand, then
record it on the Publish page so it appears in the history.

## 1. Get a Page access token

1. Create an app at <https://developers.facebook.com/apps> (type: Business). Keep it in
   **development mode**: as its admin you can post to Pages you manage without App Review.
2. In **Graph API Explorer**: select the app, add the permissions `pages_show_list`,
   `pages_manage_posts`, `pages_read_engagement` (and `pages_read_user_content` to scan
   comments), generate a **User token**, then under "Page access tokens" pick your Page.
3. Exchange it for a long-lived token (Access Token Debugger → "Extend access token"), then
   request the Page token again with the long-lived user token: Page tokens obtained this
   way do not expire while you remain an admin.
4. The Page ID is on the Page's "About" → "Page transparency", or in the Explorer response.

## 2. Configure

```
# .env (gitignored — never put tokens in YAML or commit them)
FB_PAGE_ID=1234567890
FB_PAGE_TOKEN=EAAG...
# FB_GRAPH_VERSION=v23.0
```

Restart the app, open **Publish**, click **Check connection** (or `python studio.py publish
--smoke facebook`). It calls `GET /me` with the token and refuses unless the answer is the
Page in `FB_PAGE_ID`. Publishing stays locked until this check has passed for that Page and
Graph version.

## 3. First post

- Make the first real post to a **test Page** you own.
- Dry run first: it lists the exact requests (photo uploads, the feed post, the first comment)
  without sending anything.
- Publishing asks you to type the Page name.

## What the publisher does

1. `POST /{page-id}/photos` with `published=false` for each image (invisible on the Page).
2. `POST /{page-id}/feed` with the caption and `attached_media[n]={"media_fbid": …}`.
3. `POST /{post-id}/comments` with the first comment (the tracked survey link).

Every step is recorded in `campaigns/<c>/published.yaml`. If the network fails during step 2,
the row stays **pending**: look at the Page, then resolve it as "It is on the Page" or "It is
not on the Page". The studio never sends a post twice on its own.

## Scanning comments

On **Posting history**, the refresh button reads reactions, shares and comments of posts the
studio published (`GET /{post-id}` and `/{post-id}/comments`). Only the comment text, time and
like count are stored — no names — in gitignored `campaigns/<c>/feedback/`.
