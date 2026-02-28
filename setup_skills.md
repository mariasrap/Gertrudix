# Gertrudix Setup

**This file is only needed once.** After completing setup, you can delete it.

When someone says "set up Gertrudix" / "help me get started" / "initial setup", guide them through the three steps below in order.

---

## Step 1 — Notion

1. Tell them: *"I'll create your Notion workspace. You need a free Notion account and a Notion integration token."*

2. **Get the API key:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration", give it a name (e.g. "Gertrudix"), copy the token
   - Add to `.env`: `NOTION_API_KEY=your_token_here`

3. **Find the parent page ID:**
   - Open Notion, navigate to the page where you want Gertrudix to live
   - Click `...` → `Copy link`
   - The page ID is the 32-character string at the end of the URL (before any `?`)

4. **Choose to-do categories:**
   - Ask them what high-level buckets make sense for their search
   - Suggest the defaults: *Interesting Companies, Networking, Applications, Skill Building*
   - They can always ask Gertrudix to restructure these later

5. **Run the setup script:**
   ```bash
   gertrudix_env/bin/python setup_notion.py
   ```
   - Follow the prompts (API key, parent page ID, categories)
   - Copy the outputted `.env` values into your `.env` file

6. **Manual step — add the formula:**
   - The Notion API can't create formula properties, so this one's by hand
   - Open the **Contacts** database → click `+` → choose **Formula**
   - Name it: `Needs to be contacted`
   - Paste this formula:
     ```
     (not empty(Last Contact) and now() > Last Contact.dateAdd(1, "weeks") and ["Contacted", "Replied-waiting for their answer"].includes(Status)) or Status == "Replied-waiting for my answer" or Status == "Not started"
     ```
   - This is what Gertrudix uses during the morning routine to flag who needs attention

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
