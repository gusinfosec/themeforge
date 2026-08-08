# MASTODON-ROUTINE.md — daily check-in & reply policy

> **Cadence:** check once a day, or every two days — whichever fits.
> **Rule:** NEVER post a reply or new post without showing the user the draft
> and getting a "go ahead" first. Check → summarize → await approval → post.

---

## 🔁 The routine (each check)

1. **Pull notifications** — mentions, favourites, reblogs, follows:
   ```bash
   TOKEN=$(cat /tmp/itchflow/masto_token.txt | tr -d '\n')
   curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" -H 'Accept: application/json' \
     'https://mastodon.social/api/v1/notifications?limit=12' | python3 -c \
     "import json,sys,re; d=json.load(sys.stdin); [print(n.get('type'),'|',n.get('account',{}).get('acct'),'|',re.sub(r'<[^>]+>','',(n.get('status') or {}).get('content',''))[:110]) for n in d]"
   ```
2. **Check for replies to OUR replies** (e.g. Thunderbird thread):
   ```bash
   TOKEN=$(cat /tmp/itchflow/masto_token.txt | tr -d '\n')
   curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" -H 'Accept: application/json' \
     'https://mastodon.social/api/v1/statuses/<our-status-id>/context'
   ```
3. **Summarize for the user** — what's new, who, what it says. Flag anything
   that needs a reply or action.
4. **Await approval** — present the proposed reply draft. Post ONLY on "go ahead".
5. **Log** — product signals/questions → `FEEDBACK.md`; new posts → `MASTODON-POSTS.md`.

## ✅ Approval gate (non-negotiable)

- [ ] Show the user a draft of every reply/post
- [ ] Wait for explicit approval before posting
- [ ] Log what was posted (URL + date) in the trackers

---

## 📋 Current status (checked 2026-08-08)

| Item | State |
|---|---|
| Thunderbird question (@simonzerafa) | ⏳ Our reply live — no answer from Simon yet |
| Booster replies (@FDT123, @prometheus, @eutechnews) | ✅ All 3 posted + logged in FEEDBACK.md |
| Pending replies | None — nothing new since last check |
| GamingOnLinux | ⏳ Waiting on Liam (email sent 2026-08-08) |
| awesome-gnome PR #222 | ✅ Open |

## 🔗 Trackers

- `FEEDBACK.md` — product signals & feature requests
- `MASTODON-POSTS.md` — all live posts + pinned hub
- `OUTREACH.md` — press/pitch status (GOL in §7)
