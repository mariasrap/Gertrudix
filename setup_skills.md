# Gertrudix Setup

**This file is only needed once.** After completing setup, you can delete it.

When someone says "set up Gertrudix" / "help me get started" / "initial setup", guide them through the three steps below in order.

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

**1b. Paste the secret into .env**

- Open the `.env` file in the Gertrudix folder with any text editor
- Find the line `NOTION_API_KEY=` and paste your secret right after the `=`, no spaces:
  ```
  NOTION_API_KEY=secret_xxxxxxxxxxxxxxxx
  ```
- Save the file

→ *"Done?"*

---

**1c. Create a parent page in Notion and connect the integration**

Say: *"Now create a blank page in Notion — this is where Gertrudix will build your workspace."*

- In Notion, create a new page anywhere (or use an existing empty one)
- Click **...** in the top right → **Connections** → search for your integration name → click to connect it
  *(This is required — without it the API can't access the page)*
- Then copy the page link: **...** → **Copy link**
- The page ID is the 32-character string at the end of the URL (before any `?`)
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

```bash
gertrudix_env/bin/python setup_notion.py
```

- When prompted, it will ask for the secret (already in .env so it may skip this), the page ID, and the categories
- When it finishes, it will print the remaining IDs — paste them into `.env`

→ *"Did it run without errors? Check your Notion page — you should see a new 'Job Search HQ' page."*

---

**1f. Add the formula to the Contacts database (manual step)**

Say: *"One last thing — the Notion API can't create formula properties, so you need to do this by hand. It only takes a minute."*

- Open the **Contacts** database inside the page that was just created
- Click **+** to add a new property → choose **Formula**
- Name it: `Needs to be contacted`
- Paste this formula:
  ```
  (not empty(Last Contact) and now() > Last Contact.dateAdd(1, "weeks") and ["Contacted", "Replied-waiting for their answer"].includes(Status)) or Status == "Replied-waiting for my answer" or Status == "Not started"
  ```

→ *"Done? That's the Notion setup complete!"*

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

After saving, tell them: *"You can keep adding to `data/knowledge/` over time — notes, reflections, past applications, anything useful. The more context I have, the better I'll be."*

Also point them to `gertrudix.md`: they should update it with their own background, job search plan, and preferences — that's the main config file Gertrudix reads every session.

---

## Step 4 — Job Board Scraping

Explain: *"Gertrudix can scrape job boards daily and surface new roles that might be a fit. The more sources you add, the better the coverage."*

**Good sources to scrape:**
- **Niche job boards** — e.g. [80,000 Hours](https://80000hours.org/job-board/) (impactful careers), [Climatebase](https://climatebase.org/) (climate), [AI Jobs](https://aijobs.net/), [Wellfound](https://wellfound.com/) (startups)
- **Company career pages directly** — if there are specific companies they're targeting, add their careers page. More reliable than job boards and often faster.
- **Aggregators** — [Greenhouse](https://boards.greenhouse.io/), [Lever](https://jobs.lever.co/), [Workday](https://www.myworkday.com/) are common ATS platforms — you can scrape specific companies' boards on these

**LinkedIn caveat:** LinkedIn actively blocks scrapers. Don't bother trying — it's not worth the effort. Use it manually.

Ask them: *"Are there specific companies or job boards you want me to check daily?"*
- Add their answers to `src/scrapers/job_scraper.py` as new scraper targets
- Check the existing scraper for examples of how sources are added

**First run — do it together:**

The first time you run the scraper, don't just discard or flag jobs silently. Go through results together:
- For each potential fit, present it and explain why you think it's relevant
- Let them react — *"yes", "no, too senior", "no, wrong field", "maybe later"*
- Pay attention to the reasons behind rejections — they tell you a lot about what actually fits
- Save the patterns: if they keep rejecting a certain type of role or company, update your understanding in `gertrudix.md`

*The goal is to calibrate together so daily scraping becomes genuinely useful rather than noise.*
