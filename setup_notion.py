#!/usr/bin/env python3
"""
Set up the Notion workspace for Gertrudix.

Creates:
- Main page with This Week's Plans, TO-DO LIST, databases, and Notes/Research
- Contacts database
- Applications database

Run: python setup_notion.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

DEFAULT_CATEGORIES = [
    "Interesting Companies",
    "Networking",
    "Applications",
    "Skill Building",
]


def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_request(method, endpoint, headers, json=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=json)
    if not response.ok:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)
    return response.json()


def create_main_page(headers, parent_page_id, categories):
    """Create the main Gertrudix page with weekly plan, to-do list, and notes."""

    # --- TO-DO LIST ---

    # Split categories across 2 columns (Notion requires at least 2)
    mid = (len(categories) + 1) // 2
    col1_cats = categories[:mid]
    col2_cats = categories[mid:]

    def make_category_blocks(cats):
        blocks = []
        for cat in cats:
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": cat}}],
                    "is_toggleable": True,
                },
            })
        return blocks

    # --- WEEKLY PLAN ---

    day_groups = [
        ["Monday", "Tuesday"],
        ["Wednesday", "Thursday"],
        ["Friday"],
    ]

    week_columns = []
    for days in day_groups:
        column_children = []
        for day in days:
            column_children.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": day},
                                   "annotations": {"bold": True}}],
                },
            })
        week_columns.append({
            "type": "column",
            "column": {"children": column_children},
        })

    # --- BUILD PAGE ---

    children = [
        # THIS WEEK'S PLANS (first)
        {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "This Week's Plans"}}],
            },
        },
        {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {
                    "content": "Your plan for the week. Each day, have Gertrudix help you "
                               "choose which tasks to pull from the to-do list below into today's slot."
                }}],
            },
        },
        {
            "type": "column_list",
            "column_list": {"children": week_columns},
        },
        # Divider
        {"type": "divider", "divider": {}},
        # TO-DO LIST
        {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "TO-DO LIST"}}],
            },
        },
        {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {
                    "content": "A dump of everything you should or could do."
                }}],
            },
        },
        {
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Tip: "}, "annotations": {"bold": True}},
                    {"type": "text", "text": {
                        "content": "Ask Gertrudix to customize these categories for your use case — "
                                   "by field, by stage, or however makes sense for your search."
                    }},
                ],
                "icon": {"type": "emoji", "emoji": "💡"},
            },
        },
        {
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Tip: "}, "annotations": {"bold": True}},
                    {"type": "text", "text": {
                        "content": "Gertrudix is trained to make to-do's actionable. Not just "
                                   "\"look into Company X\" — but a group of tasks like: "
                    }},
                    {"type": "text", "text": {
                        "content": "read their website, decide if it's interesting or discard, "
                                   "find open positions, contact someone on the team."
                    }, "annotations": {"italic": True}},
                    {"type": "text", "text": {
                        "content": " Hold them accountable if they don't."
                    }},
                ],
                "icon": {"type": "emoji", "emoji": "💡"},
            },
        },
        {
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "type": "column",
                        "column": {"children": make_category_blocks(col1_cats)},
                    },
                    {
                        "type": "column",
                        "column": {"children": make_category_blocks(col2_cats)},
                    },
                ],
            },
        },
        # Divider
        {"type": "divider", "divider": {}},
        # NOTES & RESEARCH
        {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Notes & Research"}}],
            },
        },
        {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {
                    "content": "Use this section to store notes on companies, roles, industries, "
                               "or anything you're researching. "
                               "(e.g. ask Gertrudix to summarize how to ace a PM interview and save it here)"
                }}],
            },
        },
    ]

    result = api_request("POST", "pages", headers, json={
        "parent": {"page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "🦫"},
        "properties": {
            "title": [{"type": "text", "text": {"content": "Job Search HQ"}}],
        },
        "children": [
            # Header banner
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "powered by "}, "annotations": {"color": "gray"}},
                        {"type": "text", "text": {"content": "Gertrudix 🦫"}, "annotations": {"bold": True, "color": "yellow"}},
                        {"type": "text", "text": {"content": "  ·  your AI job search sidekick"}, "annotations": {"italic": True, "color": "gray"}},
                    ],
                },
            },
            {"type": "divider", "divider": {}},
        ] + children,
    })

    return result["id"]


def add_databases(headers, main_page_id):
    """Add dividers and databases to the main page (appended after initial content)."""

    # Add divider + contacts header + description
    api_request("PATCH", f"blocks/{main_page_id}/children", headers, json={
        "children": [
            {"type": "divider", "divider": {}},
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Contacts"}}],
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {
                            "content": "Everyone relevant to your job search — people you've talked to, "
                                       "want to reach out to, or were referred to. "
                                       "If you ask Gertrudix to run the morning routine, they will check this "
                                       "database and flag who needs attention: "
                        }},
                        {"type": "text", "text": {
                            "content": "contacts you haven't reached out to yet, "
                                       "people waiting on your reply, "
                                       "or anyone you haven't followed up with in over a week."
                        }, "annotations": {"italic": True}},
                    ],
                },
            },
        ],
    })

    # Create contacts DB
    contacts_db_id = create_contacts_db(headers, main_page_id)

    # Add formula manual step — broken into readable blocks
    api_request("PATCH", f"blocks/{main_page_id}/children", headers, json={
        "children": [
            {
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {
                        "content": "Manual step — Add the 'Needs to be contacted' formula",
                    }, "annotations": {"bold": True}}],
                    "icon": {"type": "emoji", "emoji": "⚠️"},
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {
                        "content": "The Notion API can't create formula properties, so you need to do this once by hand:"
                    }}],
                },
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Open the Contacts database"}}],
                },
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Click  +  to add a new property → choose "}, },
                                  {"type": "text", "text": {"content": "Formula"}, "annotations": {"bold": True}}],
                },
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Name it: "}, },
                                  {"type": "text", "text": {"content": "Needs to be contacted"}, "annotations": {"code": True}}],
                },
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Paste this formula:"}}],
                },
            },
            {
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {
                        "content": "(not empty(Last Contact) and now() > Last Contact.dateAdd(1, \"weeks\") "
                                   "and [\"Contacted\", \"Replied-waiting for their answer\"].includes(Status)) "
                                   "or Status == \"Replied-waiting for my answer\" "
                                   "or Status == \"Not started\""
                    }}],
                    "language": "plain text",
                },
            },
            {"type": "divider", "divider": {}},
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Applications"}}],
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {
                            "content": "Have Gertrudix log every application you submit. "
                        }},
                        {"type": "text", "text": {
                            "content": "Company · Role · Date · Status"
                        }, "annotations": {"bold": True}},
                        {"type": "text", "text": {
                            "content": " — so you always know where things stand."
                        }},
                    ],
                },
            },
        ],
    })

    # Create applications DB
    applications_db_id = create_applications_db(headers, main_page_id)

    # Final divider after databases
    api_request("PATCH", f"blocks/{main_page_id}/children", headers, json={
        "children": [
            {"type": "divider", "divider": {}},
        ],
    })

    return contacts_db_id, applications_db_id


def create_contacts_db(headers, parent_page_id):
    """Create the Contacts database."""

    result = api_request("POST", "databases", headers, json={
        "parent": {"page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Contacts"}}],
        "is_inline": True,
        "properties": {
            "Name": {"title": {}},
            "Company/organization": {"rich_text": {}},
            "Role": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Not started", "color": "default"},
                        {"name": "Contacted", "color": "blue"},
                        {"name": "Replied-waiting for their answer", "color": "yellow"},
                        {"name": "Replied-waiting for my answer", "color": "orange"},
                        {"name": "Pinged", "color": "purple"},
                        {"name": "In progress", "color": "green"},
                        {"name": "Ended", "color": "gray"},
                    ],
                },
            },
            "Last Contact": {"date": {}},
            "Notes": {"rich_text": {}},
        },
    })

    return result["id"]


def create_applications_db(headers, parent_page_id):
    """Create the Applications database."""

    result = api_request("POST", "databases", headers, json={
        "parent": {"page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Applications Log"}}],
        "is_inline": True,
        "properties": {
            "Company": {"title": {}},
            "Role": {"rich_text": {}},
            "Submission Date": {"date": {}},
            "Application Status": {
                "select": {
                    "options": [
                        {"name": "Not started", "color": "default"},
                        {"name": "Applied", "color": "blue"},
                        {"name": "Interview", "color": "yellow"},
                        {"name": "Offer", "color": "green"},
                        {"name": "Rejected", "color": "red"},
                        {"name": "Withdrawn", "color": "gray"},
                    ],
                },
            },
            "Notes": {"rich_text": {}},
        },
    })

    return result["id"]


def main():
    print("=== Gertrudix Notion Setup ===\n")

    # Get API key
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        api_key = input("Enter your Notion API key (integration token): ").strip()
        if not api_key:
            print("Error: API key is required.")
            sys.exit(1)

    headers = get_headers(api_key)

    # Get parent page
    print("\nGertrudix needs a parent page in Notion to create its workspace under.")
    print("Go to Notion, open the page where you want Gertrudix, click '...' > 'Copy link'.")
    print("The page ID is the 32-character string at the end of the URL.\n")
    parent_page_id = input("Enter the parent page ID: ").strip().replace("-", "")
    if not parent_page_id:
        print("Error: Parent page ID is required.")
        sys.exit(1)

    # Get categories
    print("\nNow let's set up your to-do list categories.")
    print("These are the high-level buckets for organizing your job search tasks.")
    default_str = ", ".join(DEFAULT_CATEGORIES)
    print(f"Default: {default_str}")
    print("Press Enter to use defaults, or type your own (comma-separated).\n")
    categories_input = input("Categories: ").strip()
    if categories_input:
        categories = [c.strip() for c in categories_input.split(",") if c.strip()]
    else:
        categories = DEFAULT_CATEGORIES

    if len(categories) < 2:
        print("Error: At least 2 categories are required (Notion needs at least 2 columns).")
        sys.exit(1)

    # Create everything
    print("\nCreating Notion workspace...")

    print("  - Main page (weekly plan, to-do list, notes)...")
    main_page_id = create_main_page(headers, parent_page_id, categories)
    print(f"    Done: {main_page_id}")

    print("  - Contacts & Applications databases...")
    contacts_db_id, applications_db_id = add_databases(headers, main_page_id)
    print(f"    Contacts DB: {contacts_db_id}")
    print(f"    Applications DB: {applications_db_id}")

    # Output
    print("\n=== Setup complete! ===\n")
    print("Add these to your .env file:\n")
    print(f"NOTION_API_KEY={api_key}")
    print(f"NOTION_MAIN_PAGE_ID={main_page_id}")
    print(f"NOTION_CONTACTS_DB_ID={contacts_db_id}")
    print(f"NOTION_APPLICATIONS_DB_ID={applications_db_id}")

    print("\n--- Manual step ---")
    print("Open the Contacts database in Notion and add a Formula property")
    print("called 'Needs to be contacted' (see the callout in the page for details).")

    print("\nYour Gertrudix workspace is ready!")


if __name__ == "__main__":
    main()
