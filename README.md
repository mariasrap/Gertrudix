# Gertrudix 🦫
An agentic job search assistant built on Claude Code. Scrapes job boards, manages contacts and follow-ups, drafts applications and mails in your voice, helps you prioritize tasks and organize your days.

## Setup

**Requirements:** Python 3.10+, [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), a free [Notion](https://notion.so) account, and optionally Telegram.

> **Don't have Python?** Install it from [python.org](https://www.python.org/downloads/) or via Homebrew: `brew install python`

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

Gertrudix will guide you through the rest — creating your Notion workspace, setting up the Telegram bot, and populating your knowledge base.

## Daily use

Once set up, start every session with:

> **"Read `gertrudix.md` and `skills.md` — you are Gertrudix"**

Then try: *"run the morning routine"*
