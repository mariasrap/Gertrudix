# Gertrudix Setup

**This file is only needed once.** After all steps are done, you can delete it.

## Progress
- [ ] Step 0 — Personalisation
- [ ] Step 1 — Notion
- [ ] Step 2 — Telegram Bot
- [ ] Step 3 — User Profile & Memory
- [ ] Step 4 — Job Board Scraping

When someone says "set up Gertrudix" / "help me get started" / "initial setup" / "continue setup", check the progress section above and resume from the first unchecked step.

---

## Step 0 — Personalisation

Light and quick — just sets the tone before anything technical.

**0a. Name**

Ask: *"First things first — what should I call you? First name, nickname, whatever you prefer."*

Wait for their answer. Use it for the rest of setup and from now on.

---

**0b. Personality**

Say: *"How would you like me to be? I can be pretty much anything — describe it however you want, or pick something from this list (or mix and match):"*

- **Empathetic & supportive** — check in on you, celebrate the small wins, notice when things are rough
- **Assertive coach** — push you, hold you accountable, call it out when you're stalling (no bullying, but no coddling either)
- **Calm & methodical** — no drama, just steady progress, one thing at a time
- **Chaotic hype machine** — enthusiastic, a bit unhinged, will absolutely cheer when you get a callback
- **Dry and efficient** — minimal words, maximum output, zero small talk
- **Anxious overachiever** — always slightly worried something's been missed, triple-checks everything (arguably useful)
- Or just describe your ideal vibe — seriously, anything goes

Wait for their answer. This becomes Gertrudix's default tone going forward.

---

**0c. Folder icon**

Say: *"One small thing: want to use the Gertrudix logo as your project folder icon? It's the beaver — `logo/Gertrudix-Picsart-BackgroundRemover.png`. Totally optional, but it makes the project feel a bit more yours."*

If **yes**, ask what OS they're on, then give the right instructions:

**Mac:**
- Open `logo/Gertrudix-Picsart-BackgroundRemover.png` in Preview
- **Edit → Select All** (⌘A), then **Edit → Copy** (⌘C)
- Find your Gertrudix folder in Finder, right-click → **Get Info** (⌘I)
- Click the small folder icon in the top-left of the Get Info window (it'll highlight with a blue border)
- **Paste** (⌘V) — the icon updates immediately. Close Get Info.

**Windows:**
- Convert the logo to `.ico` first — [icoconvert.com](https://icoconvert.com) is free and works well. Save the `.ico` into `logo/`.
- Right-click the Gertrudix folder → **Properties → Customize → Change Icon**
- Browse to the `.ico` file → OK → Apply

**Linux:**
- Right-click the Gertrudix folder → **Properties**
  - **Nautilus / Nemo:** click the folder icon at the top of the Properties dialog → browse to the PNG
  - **Dolphin:** click the icon thumbnail in Properties → browse to the PNG
  - If your file manager doesn't have this option, it may not support custom folder icons — skip it or try a third-party tool like `folder-color`

If **no**: no problem, skip it.

---

**0d. Save preferences**

Write the following to the **top** of `gertrudix.md` (before the `# Gertrudix 🦫` heading), using the Edit tool:

```markdown
## User Preferences

- **Name:** [name]
- **Personality:** [their description]

---

```

Mark Step 0 `[x]`, then say: *"Perfect. Let's get you set up — ready for the Notion step?"*

After finishing each step, ask: *"Want to continue with the next step now, or stop here for today?"*
- If **yes**: move on
- If **no**: mark the completed step as `[x]` in the progress section above (edit this file), then say: *"No problem — next time just tell me to continue setup and I'll pick up from [next step name]."*

**Stay focused during setup.** If the user wants to do something else mid-setup (e.g. "can you look up that company", "help me draft a message"):
- Acknowledge it, then say: *"Let's finish setup first — it won't take long. I'll make a note so we don't forget."*
- If Notion is already set up, add a to-do: `add_todo_item('Other', 'Come back to: [what they wanted to do]')`
- If they insist on stopping: mark the current step as `[x]` if fully complete (leave unchecked if mid-step), then say: *"No problem — when you're ready to continue, just say 'continue setup' and I'll pick up from [next step]. Note that Gertrudix won't work fully until setup is complete."*

---

## Step 1 — Notion

Do this one substep at a time. After each one, wait for them to confirm before moving on.

**1a. Create the Notion integration**

Say: *"First, let's create a Notion integration so Gertrudix can read and write to your Notion."*

- Go to https://www.notion.so/profile/integrations/internal
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
gertrudix_env/bin/python src/notion/setup_notion.py \
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
   gertrudix_env/bin/python src/telegram/run_telegram_bot.py
   ```

4. **Test it:**
   - Open the new bot in Telegram and send any message
   - Confirm a file appeared in `data/telegram_inbox/`

---

## Step 3 — User Profile & Memory

This is what makes Gertrudix actually useful for *you specifically*.

**3a. Create the personal files:**

```bash
cp data/knowledge/profile/lessons_learned_template.md data/knowledge/profile/lessons_learned.md
touch data/knowledge/profile/user_profile.md
```

**3b. Build the user profile:**

Ask these questions one at a time, wait for the answer, then save everything to `data/knowledge/profile/user_profile.md`.

1. **Background:** "Tell me about your professional background — what have you worked on, what are your main skills?"
2. **What you're looking for:** "What kind of role are you looking for? What does your ideal job look like?"
3. **What you're NOT looking for:** "What would make a role a hard no?"
4. **Constraints:** "Any constraints — location, visa, salary, timeline?"
5. **Current status & priority:** "Where are you in the search right now, and what does success look like in the next few months?"
6. **Writing style:** "Drop a few examples of messages you've sent — LinkedIn DMs, emails, anything. This is how I learn to write like you."
   - Save these to `data/knowledge/messages/` (one file per type, e.g. `linkedin_example.md`, `email_example.md`)

**Documents to add (if they have them):**

Say: *"If you have any of these, drop them into the relevant `data/knowledge/` subfolder — I'll be able to read them when writing applications or tailoring your pitch:*
- *CV / resume → `data/knowledge/cvs/`*
- *Cover letters → `data/knowledge/cover_letters/`*
- *Past applications → `data/knowledge/applications/`*
- *Portfolio or writing samples → `data/knowledge/reflections/`"*

After saving, tell them: *"You can keep adding to `data/knowledge/` over time — the more context I have, the better I'll be at writing in your voice and pitching you accurately."*

---

## Step 4 — Job Board Scraping

Say: *"Gertrudix can scrape job boards and company career pages daily to surface new roles. Let's set up your sources."*

**Suggest sources based on the user's profile:**

Read `data/knowledge/profile/user_profile.md` — you just filled it in. Based on their target roles, industries, and any companies they mentioned, suggest 3–5 relevant niche job boards and 3–5 specific company career pages. Explain briefly why each fits them (one line is enough — e.g. *"80,000 Hours lists research and AI safety roles, which matches your interest in that space"*).

Think across:
- **Niche job boards** — are there boards that specialise in their field? (e.g. health tech, climate, AI safety, robotics, biotech)
- **Company career pages** — did they mention specific companies or types of companies? Surface the most relevant ones directly
- **LinkedIn caveat:** LinkedIn actively blocks scrapers — tell them to check it manually

First, create the user's personal sources file from the template:

```bash
cp src/scraping/sources_template.json src/scraping/sources.json
```

Then clear the examples from `sources.json` (set it to an empty array `[]`) so you start fresh.

Ask: *"What companies or job boards do you want me to check? List as many as you'd like."*

For each source they mention, follow the **Add Scraping Source** skill (in skills.md). Then ask *"Any more?"* until they're done.

Once all sources are added, ask: *"Want to run the first scrape now to see what comes up?"*
- If yes: follow the **Run Scrapers** skill (in skills.md)
- If no: wrap up setup
