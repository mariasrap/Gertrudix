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

6. If you had to ask for clarification, or the user corrected your interpretation, or you noticed a recurring pattern — save it to the **To-Dos & Planning** section of `data/knowledge/profile/learned_patterns.md` before moving on.

7. Move on to the next message.

---

## Write a Message

**Trigger:** "write a message to X" / "reach out to X" / "draft a DM to X" / "follow up with X" / "how should I reach out to X"

**1. Understand the context.**
If not already clear from the request, ask:
- Who is this person and what's the connection (cold, referral, met at an event, follow-up)?
- What's the goal (explore opportunities, ask for advice, follow up on a conversation, apply for a role)?
- What channel — LinkedIn DM or email?

Check Notion contacts to see if they're already there and if there's relevant history:
```bash
gertrudix_env/bin/python -c "from src.notion.client import get_contacts; import json; print(json.dumps(get_contacts(), indent=2))"
```

**2. Load context.**
Read `data/knowledge/profile/knowledge_base.md` — background, current goals, how the user presents themselves.
If past message examples exist in `data/knowledge/messages/`, read them to understand the user's tone and style.

**3. Draft the message.**

What separates messages that get replies from ones that don't:

- **Specific, verifiable personalization.** Include one concrete detail about *them* — a post they wrote, a project they worked on, a mutual connection, a career move. Generic openers ("I came across your profile") get ignored. One genuine detail outperforms a polished but templated message.
- **Open by proving you've done your homework.** The first line decides whether they keep reading. It should reference something specific to them, not introduce yourself.
- **Background in one focused paragraph.** Pick the thread most relevant to *this* person and purpose — don't narrate your whole history. What makes you credible for this specific ask?
- **One clear, low-commitment ask.** A question, a request for a 15-minute call, a pointer. Not a big ask on first contact. The goal of the message is to open a conversation, not close anything.
- **Close with flexibility.** Make it easy to say yes — offer options, adapt to their schedule, don't create friction.
- **Keep it short.** LinkedIn DMs: under ~150 words. Cold emails: 100–200 words. If you can't say it in that space, the ask isn't focused enough yet.
- **Sound like a person.** Avoid polished corporate language. Slightly informal and genuine beats perfectly smooth and forgettable. Read it aloud — if it doesn't sound like something you'd say, rewrite it.
- **Match the register.** Informal if you met recently or have a warm connection; more formal for cold outreach to senior people or professors; match the language if they speak another language.

Show the draft and briefly explain any choices that weren't obvious. Iterate until confirmed.

**4. Once confirmed:**
- If this is a new contact, add them to Notion:
  ```bash
  gertrudix_env/bin/python -c "from src.notion.client import add_contact; add_contact('Name', company='Company', role='Role', notes='NOTE')"
  ```
- Remind the user to send the message themselves and update the Last Contact date once they do.

**5. Learn.** If the user rewrote anything substantially or gave feedback on tone — save it to the **Outreach & Networking** section of `data/knowledge/profile/learned_patterns.md`.

---

## Write an Application

**Trigger:** "help me apply to X" / "write a cover letter for X" / "draft an application for X" / "I want to apply to [role]"

**1. Get the job description.**
If you don't have it, ask for the URL or a paste. Read it carefully — the cover letter needs to speak to the specific role, not a generic version of the company.

**1b. Check for specific application questions.**
Many applications include prompts beyond the cover letter — "Why this role?", "Describe a research interest", "What's a challenge you've overcome?", custom essay questions. Ask: *"Does the application ask any specific questions or prompts beyond the cover letter?"* If yes, list them and draft an answer to each before writing the letter — they often clarify what to emphasize.

**2. Load context.**
- `data/knowledge/profile/knowledge_base.md` — background, goals, how the user presents themselves
- `data/knowledge/cover_letters/` — past cover letters for tone and structure reference
- `data/knowledge/applications/` — past applications for reference

**3. Draft the cover letter.**

What separates cover letters that move forward from ones that don't:

- **Ruthless personalization.** "I'd love to work at [Company]" is not personalization. Reference the specific team, an ongoing project, a recent publication, or a stated direction. Show you've read past the About page.
- **Lead with "why you / why now."** The first paragraph should answer why *this* role at *this* organization makes sense for you, and why now. Not your backstory — that comes second.
- **One through-line, not a list of achievements.** Pick the single thread from your background that connects most directly to what this role needs. Build the letter around it. Don't narrate your whole CV.
- **Concrete examples over adjectives.** "I'm a fast learner" means nothing. "I built X from scratch in 3 months, shipping to 50k users" does. Every claim needs a specific, verifiable detail.
- **Flip the frame: contribution, not aspiration.** "I want to learn" signals you need something from them. "My experience with X is directly relevant to Y" signals you bring something. Lead with what you offer.
- **Address non-traditional background proactively.** If you don't tick every box, don't ignore it — briefly acknowledge the gap, reframe it as a strength if you can, and move on. Silence reads as unawareness.
- **Short and clean.** 3–4 paragraphs, under ~400 words. If it takes longer to explain why you're a fit, the focus isn't there yet.
- **Follow the instructions exactly.** Word limits, format requirements, "submit via form not email" — ignoring these signals you don't read carefully.

Show the draft. Explain any choices that weren't obvious. Iterate.

**4. Once confirmed:**
- Save to `data/knowledge/applications/[Company]_[Role]_[MonthYear].md`
- Log in the applications tracker:
  ```bash
  gertrudix_env/bin/python -c "from src.notion.client import add_application; add_application('Company', 'Role')"
  ```
- Add a to-do for next steps (submit, follow up, find a contact):
  ```bash
  gertrudix_env/bin/python -c "from src.notion.client import add_todo_item; add_todo_item('Applications', 'Submit — [Role] at [Company]')"
  ```

**5. Learn.** If the user made substantial changes or expressed a preference — update the **Applications** section of `data/knowledge/profile/learned_patterns.md`.

---

## Plan Day

**Trigger:** "plan my day" / "what should I work on today?" / "help me plan today" / "morning planning" / "organize my day"

**1. Get the lay of the land.**
Pull both the current week's plan and the full to-do list:
```bash
gertrudix_env/bin/python -c "from src.notion.client import get_weekly_plan; import json; print(json.dumps(get_weekly_plan(), indent=2))"
gertrudix_env/bin/python -c "from src.notion.client import get_todo_page; import json; print(json.dumps(get_todo_page(), indent=2))"
```

Check what day it is and what's already in today's slot (if anything).

**2. Ask about constraints before planning.**
*"Before I suggest anything — any calls or meetings today, or things you specifically want to get done?"*

Keep it brief. Just enough context to plan around.

**3. Suggest a realistic plan.**

Don't try to fit everything in. A good day has:
- 1–2 things that actually move something forward
- Some lower-effort tasks that are satisfying to close off
- Nothing that would require superhuman focus or time

Present the plan as a short list, not a schedule. Explain briefly why you picked these over other things (e.g. *"This follow-up has been sitting a while"* or *"This deadline is coming up"*).

Ask: *"Does this feel right, or do you want to adjust?"*

**4. Lock it in.**
For each confirmed item, add it to today in Notion:
```bash
gertrudix_env/bin/python -c "from src.notion.client import add_todo_to_day; add_todo_to_day('Monday', 'TASK')"
```

**5. Keep it brief.** This skill should feel like a quick check-in, not a planning session. If the user wants to go deeper on priorities or is feeling stuck, follow their lead.

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

### Phase 1 — Prepare (requires user)

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

**4. Handle stale jobs.**
If `data/scraped_jobs/latest_scrape.json` exists (i.e. not the first run), read `data/scraped_jobs/analyzed_jobs.json` and check if each job's URL still appears in `latest_scrape.json` — but only for the sources being scraped this session. Any that no longer appear may have been filled. Flag them: *"[X] roles you had saved are no longer listed — they may have been filled: [list]. Want to drop them?"*
- Drop: remove those entries from `analyzed_jobs.json`
- Keep: leave them — user may still want to act on the company

---

### Phase 2 — Scrape

**1. Run the queue update script:**
```bash
# All sources
gertrudix_env/bin/python src/scraping/update_queue.py

# Specific source(s)  — names must match exactly as they appear in sources.json
gertrudix_env/bin/python src/scraping/update_queue.py --sources "Source Name"
gertrudix_env/bin/python src/scraping/update_queue.py --sources "Source A,Source B"
```
The script fetches all jobs per source, filters to those posted since that source's last scrape date, writes the new jobs to `data/scraped_jobs/scraped_tmp.json`, saves the full scrape to `data/scraped_jobs/latest_scrape.json`, and updates `scrape_state.json`. It does NOT touch `analyzed_jobs.json` — that is Gertrudix's job in Phase 3.

**2. If `scraped_tmp.json` is empty and `analyzed_jobs.json` is also empty:** say *"Nothing new — all caught up."* and stop.

---

### Phase 3 — Categorize (autonomous)

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

---

### Phase 4 — Review with user

**1. Show a summary overview** of everything now in `analyzed_jobs.json` before diving in:
```
✅ Apply (2): Senior PM at Anthropic, Research Lead at Redwood
🔍 Worth discussing (4): Operations at OpenPhil, ...
🤝 Worth knowing about (3): Policy Lead at DeepMind, ...
```
Ask: *"How do you want to go through these?"* Follow their lead — one by one, by category, priorities first, whatever they prefer.

**2. For each job, show:**
- **Title — Company — Location**
- 1–2 sentence description of what the role actually involves
- Your category + one-line reason
- Anything specific that stood out (team, skill gap, person worth knowing)

Then ask: *"What do you think?"* Keep it open.

**3. Act on their answer:**

- **Apply** → add a to-do (`add_todo_item('Applications', 'Apply — [Role] at [Company]')`) and add to the applications tracker (`add_application('[Company]', '[Role]')`)

- **Network / connect with someone** → `add_todo_item('Networking', '[Company] — find someone on the [team] to connect with')`

- **Worth knowing about / keep on radar** — the job itself isn't what to save, it's what's actionable about it. Ask: *"Is this more about applying later, connecting with the team, or just keeping an eye on the company?"*
  - Apply later → `add_todo_item('Interesting Companies', '[Company] — watch for [type of role]')`
  - Connect → `add_todo_item('Networking', '[Company] — [specific team/reason]')`
  - Just watching → `add_todo_item('Interesting Companies', '[Company] — [why interesting]')`
  - If "apply later" becomes a recurring pattern, offer: *"You're saving quite a few roles for later — want me to create a dedicated place in Notion for those?"*

- **Something else** → do whatever makes sense

- **Skip** → no action

**4. Remove each job from `analyzed_jobs.json` as it's processed** — don't wait until the end. Edit the file to remove the entry by URL.

**5. Learn from every decision.** Corrected category, reason for skipping, revealed preference — update the **Reviewing Roles** section of `data/knowledge/profile/learned_patterns.md` before moving on. Don't ask permission.

**6. If the user stops mid-session:** remaining jobs stay in `analyzed_jobs.json` and are picked up next time.

**7. When everything has been reviewed:** summarize: *"All done — [X] to apply, [Y] to network with, [Z] on radar, [W] skipped."*

---

## Morning Routine

**Trigger:** "good morning" / "morning" / "start my day" / "morning routine"

This skill runs in parallel: scraping and categorization happen in the background while you clear your inbox, then you review the results together and plan the day.

---

**1. Prepare scraping.**
Follow **Run Scrapers → Phase 1** in full — check leftover jobs, initialize new sources, confirm which sources to scrape, and handle stale entries. Note the confirmed source list for the next step.

**2. Launch background scraping.**
Spawn a background subagent (Task tool, run\_in\_background=true) with instructions to:
- Run **Run Scrapers → Phase 2** using the sources confirmed in step 1
- Run **Run Scrapers → Phase 3** — load `knowledge_base.md` and `learned_patterns.md`, categorize all new jobs, write to `analyzed_jobs.json`, delete `scraped_tmp.json`

Don't wait for it — move on immediately.

**3. Process Telegram inbox.**
Follow the **Process Telegram Inbox** skill in full while the subagent runs.

**4. Review new jobs.**
Once Telegram is cleared, check whether the subagent has finished (read `analyzed_jobs.json` — if `scraped_tmp.json` still exists, wait briefly and check again).

Then follow **Run Scrapers → Phase 4** to go through the results together.

If there's nothing new and `analyzed_jobs.json` is also empty, skip: *"Nothing new on the job front."*

**5. Plan the day.**

First, check contacts and applications for anything that needs attention:
```bash
gertrudix_env/bin/python -c "from src.notion.client import get_contacts; import json; print(json.dumps(get_contacts(), indent=2))"
gertrudix_env/bin/python -c "from src.notion.client import get_applications; import json; print(json.dumps(get_applications(), indent=2))"
```

Look for things that likely need a follow-up but don't yet have a to-do:
- **Contacts** where the status indicates follow-up is due — the "Needs to be contacted" formula in Notion already handles the date logic, so trust the `status` field rather than manually calculating dates
- **Applications** where `status` is still "Applied" and `date` is more than 2 weeks ago

Surface 2–3 items at most — don't overwhelm. For each: *"You applied to [Company] 3 weeks ago and haven't heard back — want me to add a follow-up to-do?"* Act on their answer.

Then follow the **Plan Day** skill in full.

---
