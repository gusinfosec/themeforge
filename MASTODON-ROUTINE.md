# MASTODON-ROUTINE.md — daily check-in & reply policy

> **🔑 Token (2026-08-17):** persistent copy at `~/.config/mastodon/token`
> (chmod 600, app `cyberlab-launch-cli`, scopes read + write:statuses +
> write:media). The routine scripts read `/tmp/itchflow/masto_token.txt`
> (restored on riverstone + this machine); if a reboot clears /tmp, restore
> with: `cp ~/.config/mastodon/token /tmp/itchflow/masto_token.txt`
> (and via ssh on riverstone). **Never commit or paste the token value.**

> **Cadence:** check once a day, or every two days — whichever fits.
> **Reminder:** ntfy push "☕ Mastodon check-in" every morning at **09:00**
> (riverstone `mastodon-checkin.timer`). The brief itself is one command —
> `~/scripts/mastodon-brief.sh` — see "☕ Morning brief" below.
> **Rule:** NEVER post a reply or new post without showing the user the draft
> and getting a "go ahead" first. Check → summarize → await approval → post.

---

## ☕ Morning brief (start here)

Run the read-only brief, then summarize it for the user:

```bash
~/scripts/mastodon-brief.sh
```

It prints (and never posts):
- Mastodon notifications **new since the last brief** — mentions, favourites, reblogs, follows
- GitHub clones / views / stars for `sweep-lite`, `gmail-organizer`, `ai-workflow-kit`
- A last-seen marker in `~/.cache/mastodon-brief/` so each run only shows what's new

Then present the brief with these fixed agenda items (show drafts, await "go ahead"):

1. New replies/mentions → propose a reply draft (never post first)
2. New favourites/reblogs/follows → offer thank-you replies
3. gmail-organizer traffic + stars (the #12 gate)
4. Thunderbird add-ons — ATN review status (manual, not scripted)
5. AI Workflow Kit #12 — still on hold (user 2026-08-18)
6. @simonzerafa Thunderbird thread — reply once a TB add-on ships
7. awesome-gnome PR #222 — still open

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
3. **GitHub traffic** (free-tools repos — skip private ones, they show 0s):
   ```bash
   for r in sweep-lite gmail-organizer ai-workflow-kit; do
     echo "=== $r ==="
     gh api repos/gusinfosec/$r/traffic/clones 2>/dev/null | python3 -c \
       "import json,sys; d=json.load(sys.stdin); print('clones', d.get('count'), '| uniques', d.get('uniques'))"
     gh api repos/gusinfosec/$r/traffic/views 2>/dev/null | python3 -c \
       "import json,sys; d=json.load(sys.stdin); print('views ', d.get('count'), '| uniques', d.get('uniques'))"
   done
   ```
4. **Summarize for the user** — what's new, who, what it says, plus the clone/view
   trend. Flag anything that needs a reply or action.
5. **Await approval** — present the proposed reply draft. Post ONLY on "go ahead".
6. **Log** — product signals/questions → `FEEDBACK.md`; new posts → `MASTODON-POSTS.md`;
   traffic numbers → update the table below.

## ✅ Approval gate (non-negotiable)

- [ ] Show the user a draft of every reply/post
- [ ] Wait for explicit approval before posting
- [ ] Log what was posted (URL + date) in the trackers

---

## 📋 Current status (checked 2026-08-18)

| Item | State |
|---|---|
| **VendorSafe post** | ✅ **LIVE** — https://mastodon.social/@cyberlab/117064193889929882 (branded card image, posted via API) |
| Siteintel thread | ✅ **Closed 2026-08-11** — our reply https://mastodon.social/@cyberlab/117077906758170203; Siteintel replied warmly + favourited + followed back; we **favourited** their reply (117079300594574452, verified true) — no further reply needed, loop closed |
| prometheus GitLab/agentic thread | ✅ Both replies live (agentic joke + GitLab CI job announcement) — no pending ball |
| Thunderbird question (@simonzerafa) | ⏳ Our reply live — no answer from Simon yet |
| Booster replies (@FDT123, @prometheus, @eutechnews) | ✅ All 3 posted + logged in FEEDBACK.md |
| New engagement 2026-08-12→17 | @DarkRockStudios ❤️ gmail-organizer (✅ replied) · @python + @prometheus 🔁 sweep-lite · @ab78702 ❤️ sweep-lite (logged in FEEDBACK.md) |
| AI Workflow Kit #12 | ⏳ **HOLD (user 2026-08-18)** — gmail-organizer shows movement (21 clones/1⭐) but user chose to keep holding |
| Pending replies | None — no new replies/mentions needing a response (2026-08-18) |
| GamingOnLinux | ❌ **Declined 2026-08-11** — Liam replied: GOL doesn't accept anything with AI coding at the moment. Thread closed; consider re-pitching when policy changes |
| awesome-gnome PR #222 | ✅ Open |
| GitHub traffic (free-tools) | 📈 sweep-lite 32 clones / 13 uniq / 0⭐ · gmail-organizer 21 clones / 14 uniq / 1⭐ (checked 2026-08-18) |

## 🔗 Trackers

- `FEEDBACK.md` — product signals & feature requests
- `MASTODON-POSTS.md` — all live posts + pinned hub
- `OUTREACH.md` — press/pitch status (GOL in §7)
