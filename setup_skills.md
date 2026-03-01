# Gertrudix Setup

**This file is only needed once.** After all steps are done, you can delete it.

## Progress
- [ ] Step 1 — Notion
- [ ] Step 2 — Telegram Bot
- [ ] Step 3 — Knowledge Base
- [ ] Step 4 — Job Board Scraping

When someone says "set up Gertrudix" / "help me get started" / "initial setup" / "continue setup", check the progress section above and resume from the first unchecked step.

After finishing each step, ask: *"Want to continue with the next step now, or stop here for today?"*
- If **yes**: move on
- If **no**: mark the completed step as `[x]` in the progress section above (edit this file), then say: *"No problem — next time just tell me to continue setup and I'll pick up from [next step name]."*

---

## Step 1 — Notion

Do this one substep at a time. After each one, wait for them to confirm before moving on.

**1a. Create the Notion integration**

Say: *"First, let's create a Notion integration so Gertrudix can read and write to your Notion."*

- Go to https://www.notion.so/my-integrations
- Click **New integration**
- Set type to **Internal** (not Public — that one asks for a ton of extra info)
- Give it a name (e.g. "Gertrudix"), select your workspace, hit Submit
- Copy the **Internal Integration Secret**

→ *"Done? Tell me when you have the secret copied."*

---

**1b. Create the .env file**

Claude Code may be running from a worktree (not the actual project folder). Run this to find the real project root and create `.env` there:

```bash
PROJECT_ROOT=$(dirname "$(git rev-parse --git-common-dir)")
ENV_FILE="$PROJECT_ROOT/.env"
[ -f "$ENV_FILE" ] || cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
echo "Your .env is at: $ENV_FILE"
```

Then open the file directly so the user doesn't have to find it (`.env` is hidden by default in Finder/File Explorer):

- **Mac:** `open -e "$ENV_FILE"` — opens in TextEdit
- **Windows:** `notepad "$ENV_FILE"` — opens in Notepad

If you're not sure which OS they're on, just run the Mac command — if it fails, try Windows. Either way, once it's open, say:

*"A file just opened — that's your `.env`. Find the line `NOTION_API_KEY=` and paste your secret right after the `=`, no spaces:*
```
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxx
```
*Save and close."*

→ *"Done?"*

---

**1c. Create a page in Notion and connect the integration**

Say: *"Now create a blank page in Notion — the script will turn it into your Job Search HQ."*

- In Notion, create a new blank page anywhere
- Click **...** in the top right → **Connections** → search for your integration name → click to connect it
  *(Required — without this the API can't access the page)*
- Copy the page link: **...** → **Copy link**
- The page ID is the 32-character string at the end of the URL (before any `?`). Keep it handy — you'll need it in step 1e.
- Paste it into `.env`:
  ```
  NOTION_MAIN_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

→ *"Done?"*

---

**1d. Choose your to-do categories**

Say: *"Almost ready to run the script. Last thing: the Notion page will have a to-do list divided into sections — one per category. Think of them as buckets to organize your job search tasks. For example: companies you want to research, people to reach out to, applications in progress, skills to build."*

- Suggest the defaults: **Interesting Companies, Networking, Applications, Skill Building**
- Ask: *"Do these work for you, or do you want different ones? You can always ask me to reorganize them later."*
- Wait for their answer

---

**1e. Run the setup script**

By now you have the page ID (from step 1c) and the categories (from step 1d). Run the script from the real project root, passing both as arguments:

```bash
PROJECT_ROOT=$(dirname "$(git rev-parse --git-common-dir)")
cd "$PROJECT_ROOT"
gertrudix_env/bin/python setup_notion.py \
  --page-id PAGE_ID_HERE \
  --categories "Interesting Companies, Networking, Applications, Skill Building"
```

Replace `PAGE_ID_HERE` with the actual page ID from step 1c, and adjust the categories if the user chose different ones.

- The script will rename that page to "Job Search HQ" and fill it with content — no subpage created
- When it finishes, it prints two IDs — open `.env` and add them (same way as step 1b):
  ```
  NOTION_CONTACTS_DB_ID=...
  NOTION_APPLICATIONS_DB_ID=...
  ```

→ *"Did it run without errors? Check your Notion page — you should see a new 'Job Search HQ' page."*

---

**1f. Add the formula to the Contacts database (manual step)**

Say: *"One last thing — the Notion API can't create formula properties, so you need to do this by hand. It only takes a minute."*

- Open the **Contacts** database — click on it to open it as a full page
- Click the **+** button at the far right of the column headers to add a new property
- In the property type list, choose **Formula**
- At the top, rename it from "Formula" to: `Needs to be contacted`
- Click **Edit formula**, paste this, then click **Done**:
  ```
  (not empty(prop("Last Contact")) and now() > dateAdd(prop("Last Contact"), 1, "weeks") and (prop("Status") == "Contacted" or prop("Status") == "Replied-waiting for their answer")) or prop("Status") == "Replied-waiting for my answer" or prop("Status") == "Not started"
  ```

→ *"Done! That's the Notion setup finished."*

Mark Step 1 as `[x]` in the progress section, then ask: *"Want to continue with Step 2 (Telegram bot) now, or stop here for today?"*

---

## Step 2 — Telegram Bot

1. Tell them: *"The Telegram bot lets you send yourself quick notes, links, or job leads from your phone. Gertrudix picks them up during the morning routine."*

2. **Create the bot:**
   - Open Telegram, search for **@BotFather**
   - Send `/newbot`, follow the prompts, copy the token
   - Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token_here`

3. **Run the bot:**
   ```bash
   gertrudix_env/bin/python run_telegram_bot.py
   ```

4. **Test it:**
   - Open the new bot in Telegram and send any message
   - Confirm a file appeared in `data/telegram_inbox/`

---

## Step 3 — Knowledge Base

This is what makes Gertrudix actually useful for *you specifically*. Ask these questions one at a time, wait for the answer, then save everything to `data/knowledge/profile/knowledge_base.md`.

1. **Background:** "Tell me about your professional background — what have you worked on, what are your main skills?"
2. **What you're looking for:** "What kind of role are you looking for? What does your ideal job look like?"
3. **What you're NOT looking for:** "What would make a role a hard no?"
4. **Constraints:** "Any constraints — location, visa, salary, timeline?"
5. **Current status:** "Where are you in the search right now? What have you already tried?"
6. **Writing style:** "Drop a few examples of messages you've sent — LinkedIn DMs, emails, anything. This is how I learn to write like you."
   - Save these to `data/knowledge/messages/` (one file per type, e.g. `linkedin_example.md`, `email_example.md`)

**Documents to add (if they have them):**

Say: *"If you have any of these, drop them into the `data/knowledge/documents/` folder — I'll be able to read them when writing applications or tailoring your pitch:*
- *CV / resume (PDF or Word)*
- *Cover letters from past applications*
- *Any past application forms you filled out*
- *Portfolio, writing samples, or anything else that shows your work"*

After saving, tell them: *"You can keep adding to `data/knowledge/` over time — the more context I have, the better I'll be at writing in your voice and pitching you accurately."*

---

## Step 4 — Job Board Scraping

Explain: *"Gertrudix can scrape job boards daily and surface new roles that might be a fit. Let's save which sources you want me to watch."*

**Good sources to suggest:**
- **Niche job boards** — e.g. [80,000 Hours](https://80000hours.org/job-board/) (impactful careers), [Climatebase](https://climatebase.org/) (climate), [AI Jobs](https://aijobs.net/), [Wellfound](https://wellfound.com/) (startups)
- **Company career pages** — if they have specific companies in mind, their careers page is more reliable and often faster than job boards
- **Aggregators** — [Greenhouse](https://boards.greenhouse.io/), [Lever](https://jobs.lever.co/), [Workday](https://www.myworkday.com/) for specific companies

**LinkedIn caveat:** LinkedIn actively blocks scrapers — use it manually.

Ask: *"Are there specific companies or job boards you want me to check daily?"*
- Save their answers to `src/scrapers/job_scraper.py` as scraper targets (check the file for examples of how sources are added)

Once the sources are saved, ask: *"Want to run the first scrape now to see what comes up, or save that for another time?"*
- If yes: run it (first-scrape skill coming soon — skip for now if not built yet)
- If no: that's fine, wrap up setup
