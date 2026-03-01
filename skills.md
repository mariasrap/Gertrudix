# Gertrudix Skills

Skills are triggered by the user's message. Read the relevant skill and follow it.

All Notion functions live in `src/notion/client.py`. Call them via:
```bash
gertrudix_env/bin/python -c "from src.notion.client import FUNCTION; FUNCTION(args)"
```

---

## Process Telegram Inbox

**Trigger:** "check telegram" / "what's in my inbox?" / "process inbox"

1. Read the current to-do categories from Notion so you can suggest the right ones:
   ```bash
   gertrudix_env/bin/python -c "from src.notion.client import get_todo_page; import json; print(json.dumps(list(get_todo_page()['categories'].keys())))"
   ```
   Keep this list in mind for the whole session.

2. Glob `data/telegram_inbox/` for `.md` files. If empty, say: *"No messages in the inbox."* and stop.

3. For each file, read it and present the message to the user. Then:

   - **If the message is cryptic or unclear**, ask what it's about before proposing anything.

   - **Propose what to do with it.** Options:
     - Add a to-do → suggest the most fitting category from the list you fetched, and the exact wording
     - Add to this week's plan directly → if it's time-sensitive or the user wants to do it soon
     - Add a contact → if it's about a person they met or want to reach out to
     - Add an application → if it's a specific role they want to apply to
     - Discard → if there's nothing actionable

   - **To-do wording matters.** Don't just mirror the message. Make it specific and actionable:
     - Bad: *"Check out Stripe"*
     - Good: *"Stripe — look at open roles, decide if worth applying, note any interesting teams"*

   - **If there are two distinct things in one message** (e.g. a person + a company), split into two to-dos.

   - **If something is urgent** (e.g. a follow-up with a deadline, something happening this week), suggest adding it to the weekly plan under a specific day rather than the general to-do list.

   - Always confirm the wording and destination with the user before executing.

4. Execute the confirmed action:
   ```bash
   # Add to-do under a category
   gertrudix_env/bin/python -c "from src.notion.client import add_todo_item; add_todo_item('CATEGORY', 'TASK')"

   # Add to a specific day in weekly plan
   gertrudix_env/bin/python -c "from src.notion.client import add_todo_to_day; add_todo_to_day('Monday', 'TASK')"

   # Add a contact
   gertrudix_env/bin/python -c "from src.notion.client import add_contact; add_contact('Name', company='Company', role='Role', notes='NOTE')"

   # Add an application
   gertrudix_env/bin/python -c "from src.notion.client import add_application; add_application('Company', 'Role')"
   ```

5. Delete the processed file:
   ```bash
   rm "data/telegram_inbox/FILENAME.md"
   ```

6. If you had to ask for clarification, or the user corrected your interpretation, or you noticed a recurring pattern — save it to `data/knowledge/profile/learned_patterns.md` before moving on.

7. Move on to the next message.

---

## Add Scraping Source

**Trigger:** "add [company/site] to my sources" / "I want to track [company]" / "watch [job board]"

### Step 1 — Identify the platform

If you don't have a URL, ask: *"Do you have the careers page URL?"*

Check the URL against known patterns:

| URL pattern | Type | How to get the slug |
|---|---|---|
| `greenhouse.io/[slug]` or `boards.greenhouse.io/[slug]` | `greenhouse` | last path segment |
| `jobs.lever.co/[slug]` | `lever` | last path segment |
| `jobs.ashbyhq.com/[slug]` | `ashby` | last path segment |
| `linkedin.com` | ❌ cannot scrape | — |
| `myworkday.com` | ❌ cannot scrape | — |
| `indeed.com` | ❌ cannot scrape | — |

If the URL doesn't match any of these, go to **Scenario 2** below.

---

### Scenario 1 — Supported ATS (Greenhouse, Lever, Ashby)

1. Extract the slug from the URL
2. Tell the user what they can filter on:
   *"I can filter the results by **location** (e.g. 'Remote', 'London') and/or **department** (e.g. 'Engineering', 'Research'). Filtering is done after fetching, so the values need to match what the job board actually uses. Do you want any filters, or should I fetch everything?"*
3. Add the entry to `src/scraping/sources.json`:
   ```json
   {
     "name": "Company Name",
     "type": "greenhouse",
     "slug": "slug-here",
     "filters": {
       "locations": [],
       "departments": []
     }
   }
   ```
4. Confirm: *"Done — I'll pick up [Company] jobs on the next scrape."*

---

### Scenario 2 — Not natively supported, but potentially scrapeable

**First, check for an RSS feed.** Try fetching these URLs (replace `[base]` with the site's base URL):
- `[base]/feed`
- `[base]/rss`
- `[base]/jobs/feed`
- `[base]/feed.xml`

If an RSS feed exists → add it as type `rss` with the feed URL as the slug, then ask about filters (RSS feeds rarely have structured location/department fields, so let the user know filtering may be limited).

**If no RSS feed**, use WebFetch to inspect the careers page:
- Look for Algolia API calls (`algolia.net` in page source or script tags)
- Look for public JSON endpoints (e.g. `/api/jobs`, `/careers/api`)
- Look for other ATS patterns you recognise

**If you find a clean API pattern:**
1. Inspect the API response to understand what fields are available (e.g. location, department, category, area)
2. Tell the user what filtering options the API supports, and ask if they want any
3. Write a new scraper class in `src/scraping/scrapers/` that extends `BaseScraper` — follow the pattern in `greenhouse.py` or `lever.py`, wiring the user's chosen filters into the class
4. Register it in `SCRAPER_MAP` in `src/scraping/run_scrapers.py`
5. Add the entry to `src/scraping/sources.json`
6. Confirm: *"Done — wrote a custom scraper for [site] and added it to your sources."*

**If the site is too complex or unclear:**
Say: *"I couldn't find a clean way to scrape [site] automatically. You'll need to check it manually for now."*

---

### Scenario 3 — Cannot be scraped (LinkedIn, Workday, etc.)

Say: *"[Site] actively blocks scrapers — it's not possible to automate this reliably. You'll need to check it manually."*

If relevant, suggest an alternative: *"If you're looking for specific companies on LinkedIn, I can try their direct careers pages instead — those are often easier to scrape."*

---

## Run Scrapers

**Trigger:** "run scrapers" / "check for new jobs" / "any new jobs?" / "scrape [source]"

Two persistent files manage state across sessions:
- `data/scraped_jobs/scrape_state.json` — last scrape date **per source**
- `data/scraped_jobs/analyzed_jobs.json` — jobs queued for review; survives across sessions

---

### Phase 1 — Scrape & update the queue

**1. Check for leftover jobs from a previous session.**
Read `data/scraped_jobs/analyzed_jobs.json`. If it has jobs, mention it: *"You have [X] jobs left from last time. I'll add any new ones and we'll go through everything together."*

**2. Handle new sources before scraping.**
Read `data/scraped_jobs/scrape_state.json` (or note it doesn't exist yet) and compare its keys against the source names in `src/scraping/sources.json`. For any source in `sources.json` that has no entry in `scrape_state.json`, ask:
*"[Source] hasn't been scraped before — how far back do you want to go? (e.g. 'last 6 months', 'everything', or a specific date)"*
Add that source to `scrape_state.json` with the date they give, formatted as `"YYYY-MM-DDT00:00:00"`. Default if unspecified: `"2020-01-01T00:00:00"`. Do this for all new sources before running the script.

**3. Decide which sources to scrape.**
Ask if they want to scrape everything today or just specific ones. Default to all.

**3b. Validate the requested sources.**
If they named specific sources, check that each one exists in `src/scraping/sources.json`. Match by name (case-sensitive). If any don't match, show the available names and ask them to clarify before continuing.

**4. Run the queue update script:**
```bash
# All sources
gertrudix_env/bin/python src/scraping/update_queue.py

# Specific source(s)  — names must match exactly as they appear in sources.json
gertrudix_env/bin/python src/scraping/update_queue.py --sources "Source Name"
gertrudix_env/bin/python src/scraping/update_queue.py --sources "Source A,Source B"
```
The script fetches all jobs per source, filters to those posted since that source's last scrape date, writes the new jobs to `data/scraped_jobs/scraped_tmp.json`, saves the full scrape to `data/scraped_jobs/latest_scrape.json`, and updates `scrape_state.json`. It does NOT touch `analyzed_jobs.json` — that is Gertrudix's job in Phase 2.

**5. Handle stale jobs.**
Read `data/scraped_jobs/analyzed_jobs.json`. For every job in the file, check if its URL still appears in `data/scraped_jobs/latest_scrape.json` (only for the sources just scraped). Any that no longer appear may have been filled. Flag them: *"[X] roles you had saved are no longer listed — they may have been filled: [list]. Want to drop them?"*
- Drop: remove those entries from `analyzed_jobs.json`
- Keep: leave them — user may still want to act on the company

**6. If `scraped_tmp.json` is empty and `analyzed_jobs.json` is also empty:** say *"Nothing new — all caught up."* and stop.

---

### Phase 2 — Categorize & review

**1. Load context:**
- `data/knowledge/profile/knowledge_base.md` — background, target role, hard nos, constraints
- `data/knowledge/profile/learned_patterns.md` — past decisions and preferences

**2. Read new jobs from `data/scraped_jobs/scraped_tmp.json`.** Also read any leftover jobs already in `data/scraped_jobs/analyzed_jobs.json` (from previous sessions). Together these are the full set to review.

**3. Do a silent first pass on the new jobs from `scraped_tmp.json`.** Assign each a category:

| Category | Meaning |
|---|---|
| ✅ **Apply** | Good fit — role, level, and direction align |
| 🔍 **Worth discussing** | Not a perfect fit but interesting — adjacent role, stretch, or something they hadn't considered |
| 🤝 **Worth knowing about** | Role isn't right but company/team is relevant — good for a connection, future role, or keeping on radar |
| ❌ **Skip** | Genuinely irrelevant — wrong field, geography, clearly misaligned |

**Be conservative, especially early on.** When in doubt, bump it up. Surface borderline things — the user's feedback is how your judgement improves over time.

**4. Write newly categorized jobs to `data/scraped_jobs/analyzed_jobs.json`** — append them to any existing entries. Then delete `scraped_tmp.json`.

**5. Show a summary overview** of everything now in `analyzed_jobs.json` before diving in:
```
✅ Apply (2): Senior PM at Anthropic, Research Lead at Redwood
🔍 Worth discussing (4): Operations at OpenPhil, ...
🤝 Worth knowing about (3): Policy Lead at DeepMind, ...
```
Ask: *"How do you want to go through these?"* Follow their lead — one by one, by category, priorities first, whatever they prefer.

**6. For each job, show:**
- **Title — Company — Location**
- 1–2 sentence description of what the role actually involves
- Your category + one-line reason
- Anything specific that stood out (team, skill gap, person worth knowing)

Then ask: *"What do you think?"* Keep it open.

**7. Act on their answer:**

- **Apply** → add a to-do (`add_todo_item('Applications', 'Apply — [Role] at [Company]')`) and add to the applications tracker (`add_application('[Company]', '[Role]')`)

- **Network / connect with someone** → `add_todo_item('Networking', '[Company] — find someone on the [team] to connect with')`

- **Worth knowing about / keep on radar** — the job itself isn't what to save, it's what's actionable about it. Ask: *"Is this more about applying later, connecting with the team, or just keeping an eye on the company?"*
  - Apply later → `add_todo_item('Interesting Companies', '[Company] — watch for [type of role]')`
  - Connect → `add_todo_item('Networking', '[Company] — [specific team/reason]')`
  - Just watching → `add_todo_item('Interesting Companies', '[Company] — [why interesting]')`
  - If "apply later" becomes a recurring pattern, offer: *"You're saving quite a few roles for later — want me to create a dedicated place in Notion for those?"*

- **Something else** → do whatever makes sense

- **Skip** → no action

**8. Remove each job from `analyzed_jobs.json` as it's processed** — don't wait until the end. Edit the file to remove the entry by URL.

**9. Learn from every decision.** Corrected category, reason for skipping, revealed preference — update `data/knowledge/profile/learned_patterns.md` before moving on. Don't ask permission.

**10. If the user stops mid-session:** remaining jobs stay in `analyzed_jobs.json` and are picked up next time.

**11. When everything has been reviewed:** summarize: *"All done — [X] to apply, [Y] to network with, [Z] on radar, [W] skipped."*

---
