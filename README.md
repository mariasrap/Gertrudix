# Gertrudix 🦫

A personal job search assistant that runs inside [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview). It scrapes job boards, processes your notes, drafts messages and cover letters in your voice, manages contacts and follow-ups, and helps you plan and prioritize each day.

You interact with it through Claude Code conversations — no separate app or UI. Every morning you tell it to run the routine; it handles the rest.

---

## What it does

- **Morning routine** — scrapes new jobs in the background while you clear your Telegram inbox, then reviews roles with you and plans your day
- **Job review** — reads job listings, categorizes them against your profile, and surfaces only what's worth your attention
- **Outreach** — drafts messages and follow-ups in your tone, adds contacts to Notion, reminds you when to follow up
- **Applications** — writes cover letters and answers application prompts using your background and past examples
- **Planning** — pulls your to-do list and weekly plan from Notion, helps you decide what to focus on today

---

## Getting started

**Requirements:** Python 3.10+, Claude Code, a free [Notion](https://notion.so) account, and optionally Telegram.

**Mac / Linux**
```bash
git clone https://github.com/mariasrap/Gertrudix
cd Gertrudix
python3 -m venv gertrudix_env
source gertrudix_env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows**
```bash
git clone https://github.com/mariasrap/Gertrudix
cd Gertrudix
python -m venv gertrudix_env
gertrudix_env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then open the folder in Claude Code and say:

> **"Read `setup_skills.md` and help me set up Gertrudix"**

Claude will walk you through the rest — Notion workspace, Telegram bot, and your personal profile. From there, everything is self-explanatory.

---

## Daily use

Start each session with:

> **"Read `gertrudix.md` and `skills.md` — you are Gertrudix"**

Gertrudix will suggest starting with the morning routine, or you can ask for something specific.
