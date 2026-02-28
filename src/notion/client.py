import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
APPLICATIONS_DB_ID = os.getenv("NOTION_APPLICATIONS_DB_ID")
CONTACTS_DB_ID = os.getenv("NOTION_CONTACTS_DB_ID")
MAIN_PAGE_ID = os.getenv("NOTION_MAIN_PAGE_ID")
BACKLOG_PAGE_ID = os.getenv("NOTION_BACKLOG_PAGE_ID")

BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}


def _request(method, endpoint, json=None):
    """Make a request to the Notion API."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=HEADERS, json=json)
    response.raise_for_status()
    return response.json()


def get_applications():
    """Returns all entries from the Applications Log database."""
    response = _request("POST", f"databases/{APPLICATIONS_DB_ID}/query")
    applications = []

    for page in response["results"]:
        props = page["properties"]
        applications.append({
            "id": page["id"],
            "company": _get_title(props.get("Company")),
            "role": _get_rich_text(props.get("Role")),
            "date": _get_date(props.get("Submission Date")),
            "status": _get_select(props.get("Application Status")),
            "notes": _get_rich_text(props.get("Notes")),
        })

    return applications


def add_application(company: str, role: str, date: str = None, status: str = "Applied", notes: str = ""):
    """Adds a new application to the Applications Log database."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    properties = {
        "Company": {"title": [{"text": {"content": company}}]},
        "Role": {"rich_text": [{"text": {"content": role}}]},
        "Submission Date": {"date": {"start": date}},
        "Application Status": {"select": {"name": status}},
    }

    if notes:
        properties["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    return _request("POST", "pages", json={
        "parent": {"database_id": APPLICATIONS_DB_ID},
        "properties": properties
    })


def get_contacts():
    """Returns all contacts from the Contacts database."""
    response = _request("POST", f"databases/{CONTACTS_DB_ID}/query")
    contacts = []

    for page in response["results"]:
        props = page["properties"]
        contacts.append({
            "id": page["id"],
            "name": _get_title(props.get("Name")),
            "company": _get_rich_text(props.get("Company")),
            "role": _get_rich_text(props.get("Role")),
            "status": _get_select(props.get("Status")),
            "last_contact": _get_date(props.get("Last Contact")),
            "notes": _get_rich_text(props.get("Notes")),
        })

    return contacts


def add_contact(name: str, company: str = "", role: str = "", status: str = "New",
                last_contact: str = None, notes: str = ""):
    """Adds a new contact to the Contacts database."""
    properties = {
        "Name": {"title": [{"text": {"content": name}}]},
    }

    if company:
        properties["Company/organization"] = {"rich_text": [{"text": {"content": company}}]}
    if role:
        properties["Role"] = {"rich_text": [{"text": {"content": role}}]}
    if status:
        properties["Status"] = {"status": {"name": status}}
    if last_contact:
        properties["Last Contact"] = {"date": {"start": last_contact}}
    if notes:
        properties["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    return _request("POST", "pages", json={
        "parent": {"database_id": CONTACTS_DB_ID},
        "properties": properties
    })


def _get_todo_item(block):
    """Recursively get a to-do item and its sub-tasks."""
    text = _get_rich_text_from_block(block["to_do"]["rich_text"])
    if not text:
        return None

    item = {
        "id": block["id"],
        "type": "to_do",
        "text": text,
        "checked": block["to_do"]["checked"],
        "children": []
    }

    # Check for nested children (sub-tasks, paragraphs, etc.)
    if block.get("has_children"):
        children = _request("GET", f"blocks/{block['id']}/children")
        for child in children["results"]:
            parsed = _parse_block(child)
            if parsed:
                item["children"].append(parsed)

    return item


def _parse_block(block):
    """Recursively parse any block type into a structured dict.

    Handles: to_do, paragraph (as pointer), heading_3 (as sub-category),
    toggle, and any other block with children.
    """
    btype = block["type"]
    has_children = block.get("has_children", False)

    if btype == "to_do":
        return _get_todo_item(block)

    if btype == "paragraph":
        text = _get_rich_text_from_block(block["paragraph"]["rich_text"])
        if not text:
            return None
        item = {
            "id": block["id"],
            "type": "pointer",
            "text": text,
            "children": []
        }
        if has_children:
            children = _request("GET", f"blocks/{block['id']}/children")
            for child in children["results"]:
                parsed = _parse_block(child)
                if parsed:
                    item["children"].append(parsed)
        return item

    if btype in ("heading_3", "toggle"):
        key = btype
        text = _get_rich_text_from_block(block[key]["rich_text"])
        if not text:
            return None
        item = {
            "id": block["id"],
            "type": "subcategory",
            "text": text,
            "children": []
        }
        if has_children:
            children = _request("GET", f"blocks/{block['id']}/children")
            for child in children["results"]:
                parsed = _parse_block(child)
                if parsed:
                    item["children"].append(parsed)
        return item

    return None


def get_todo_page():
    """Reads the To-Do List from toggleable headings in the main page.

    Structure:
    - H2 "TO-DO LIST" at the top level
    - column_list(s) underneath containing columns
    - Each column has category heading_3 toggles (ML Research, Academia, etc.)
    - Inside each category: mix of paragraphs (pointers), to_do items,
      and sub-heading_3/toggles (sub-categories like Climate, AI Safety)
    - Pointers (paragraphs) have to_do children as action items
    - Sub-categories have their own pointers and to_do items

    Returns nested structure preserving the full hierarchy.
    """
    blocks = _request("GET", f"blocks/{MAIN_PAGE_ID}/children")
    all_blocks = blocks["results"]

    # Find the TO-DO LIST H2 and the column_lists after it
    todo_h2_idx = None
    for i, block in enumerate(all_blocks):
        if block["type"] == "heading_2":
            text = _get_rich_text_from_block(block["heading_2"]["rich_text"])
            if "to-do" in text.lower() or "todo" in text.lower():
                todo_h2_idx = i
                break

    if todo_h2_idx is None:
        return {"error": "Could not find a 'TO-DO' heading on the main page."}

    todos = {}

    # Collect all column_lists between the TO-DO H2 and the next H2
    for block in all_blocks[todo_h2_idx + 1:]:
        if block["type"] == "heading_2":
            break  # next section
        if block["type"] != "column_list":
            continue

        columns = _request("GET", f"blocks/{block['id']}/children")
        for column in columns["results"]:
            items = _request("GET", f"blocks/{column['id']}/children")
            for item in items["results"]:
                # Category heading_3 toggles
                if item["type"] == "heading_3" and item.get("has_children"):
                    category = _get_rich_text_from_block(item["heading_3"]["rich_text"])
                    children = _request("GET", f"blocks/{item['id']}/children")
                    category_items = []
                    for child in children["results"]:
                        parsed = _parse_block(child)
                        if parsed:
                            category_items.append(parsed)
                    todos[category] = category_items

    return {"page_id": MAIN_PAGE_ID, "categories": todos}


def add_todo_item(category: str, task_name: str):
    """Adds a task under a category toggle (heading_3) in the main page."""
    # Get blocks from the main page
    blocks = _request("GET", f"blocks/{MAIN_PAGE_ID}/children")

    target_heading_id = None

    # Find the toggleable heading_3 for this category
    for block in blocks["results"]:
        if block["type"] == "column_list":
            columns = _request("GET", f"blocks/{block['id']}/children")
            for column in columns["results"]:
                items = _request("GET", f"blocks/{column['id']}/children")
                for item in items["results"]:
                    if item["type"] == "heading_3" and item.get("has_children"):
                        heading_text = _get_rich_text_from_block(item["heading_3"]["rich_text"])
                        if category.lower() in heading_text.lower():
                            target_heading_id = item["id"]
                            break
                if target_heading_id:
                    break
            if target_heading_id:
                break

    if not target_heading_id:
        return {"error": f"Category '{category}' not found. Available: ML Research Industry, Academia Collaborations, Exploring Fit in Other Fields, Other"}

    # Add the to-do item as a child of the heading
    return _request("PATCH", f"blocks/{target_heading_id}/children", json={
        "children": [{
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": task_name}}],
                "checked": False
            }
        }]
    })


def add_to_backlog(company: str, role: str, url: str, notes: str = ""):
    """Adds a job to the Phase 2 Backlog page as a bullet point."""
    # Format: Company - Role (URL) - Notes
    text = f"{company} - {role}"

    children = [
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": text + " ("}},
                    {"type": "text", "text": {"content": "link", "link": {"url": url}}},
                    {"type": "text", "text": {"content": ")"}}
                ]
            }
        }
    ]

    # Add notes as nested item if provided
    if notes:
        children[0]["bulleted_list_item"]["children"] = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": notes}}]
                }
            }
        ]

    return _request("PATCH", f"blocks/{BACKLOG_PAGE_ID}/children", json={
        "children": children
    })


def get_weekly_plan():
    """Reads the 'This Week's Plans' section from the main page.

    Structure: H2 "This Week's Plans" → (empty paragraphs) → column_list
    Each column contains paragraph day labels ("Monday", "Tuesday", etc.)
    followed by to_do items for that day.

    Returns: {"page_id": str, "heading_id": str, "days": {day_name: {"day_block_id": str, "column_id": str, "todos": [todo_items]}}}
    """
    DAY_NAMES = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}

    blocks = _request("GET", f"blocks/{MAIN_PAGE_ID}/children")
    all_blocks = blocks["results"]

    # Find the H2 heading for this week's plans
    weekly_h2_idx = None
    weekly_h2_id = None
    for i, block in enumerate(all_blocks):
        if block["type"] == "heading_2":
            text = _get_rich_text_from_block(block["heading_2"]["rich_text"])
            if "week" in text.lower():
                weekly_h2_idx = i
                weekly_h2_id = block["id"]
                break

    if weekly_h2_id is None:
        return {"error": "Could not find a 'This Week' heading on the main page."}

    # Find the column_list that follows the H2 (skip empty paragraphs)
    column_list_block = None
    for block in all_blocks[weekly_h2_idx + 1:]:
        if block["type"] == "column_list":
            column_list_block = block
            break
        if block["type"] == "paragraph":
            continue  # skip empty paragraphs between H2 and column_list
        break  # hit something else, stop

    if not column_list_block:
        return {"page_id": MAIN_PAGE_ID, "heading_id": weekly_h2_id, "days": {}}

    # Read columns
    columns = _request("GET", f"blocks/{column_list_block['id']}/children")
    days = {}

    for column in columns["results"]:
        col_items = _request("GET", f"blocks/{column['id']}/children")
        current_day = None
        current_day_block_id = None

        for item in col_items["results"]:
            if item["type"] == "paragraph":
                text = _get_rich_text_from_block(item["paragraph"]["rich_text"]).strip()
                if text.lower().rstrip() in DAY_NAMES:
                    current_day = text.strip()
                    current_day_block_id = item["id"]
                    days[current_day] = {
                        "day_block_id": current_day_block_id,
                        "column_id": column["id"],
                        "todos": []
                    }
            elif item["type"] == "to_do" and current_day:
                todo_item = _get_todo_item(item)
                if todo_item:
                    days[current_day]["todos"].append(todo_item)

    return {"page_id": MAIN_PAGE_ID, "heading_id": weekly_h2_id, "days": days}


def _find_day_last_block_id(day_data, weekly_plan, day_name):
    """Find the block ID after which to insert a new to-do for a given day.

    Returns the ID of the last to-do in that day, or the day paragraph block
    itself if there are no to-dos yet.
    """
    if day_data["todos"]:
        return day_data["todos"][-1]["id"]
    return day_data["day_block_id"]


def add_todo_to_day(day: str, task_name: str):
    """Adds a to-do item under a specific day in the weekly plan.

    Appends the to-do block after the last existing to-do for that day
    (or after the day label paragraph if no to-dos exist yet).
    """
    weekly = get_weekly_plan()
    if "error" in weekly:
        return weekly

    # Find the day (case-insensitive partial match)
    target_day = None
    target_data = None
    for day_name, day_data in weekly["days"].items():
        if day.lower() in day_name.lower():
            target_day = day_name
            target_data = day_data
            break

    if not target_data:
        available = ", ".join(weekly["days"].keys())
        return {"error": f"Day '{day}' not found. Available: {available}"}

    after_id = _find_day_last_block_id(target_data, weekly, target_day)

    # Append to the column, positioned after the last block for this day
    return _request("PATCH", f"blocks/{target_data['column_id']}/children", json={
        "children": [{
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": task_name}}],
                "checked": False
            }
        }],
        "after": after_id
    })


def delete_block(block_id: str):
    """Deletes a Notion block by ID."""
    return _request("DELETE", f"blocks/{block_id}")


def move_todo_to_day(block_id: str, task_text: str, day: str):
    """Moves a to-do item to a day in the weekly plan.

    Creates the to-do under the day heading, then deletes the original block.
    """
    result = add_todo_to_day(day, task_text)
    if "error" in result:
        return result

    delete_block(block_id)
    return {"status": "moved", "task": task_text, "day": day}


def get_backlog():
    """Gets all items from the Phase 2 Backlog page."""
    blocks = _request("GET", f"blocks/{BACKLOG_PAGE_ID}/children")
    items = []

    for block in blocks["results"]:
        if block["type"] == "bulleted_list_item":
            text = _get_rich_text_from_block(block["bulleted_list_item"]["rich_text"])
            items.append({"id": block["id"], "text": text})

    return items


# Helper functions for extracting property values
def _get_title(prop):
    if not prop or not prop.get("title"):
        return ""
    return prop["title"][0]["plain_text"] if prop["title"] else ""


def _get_rich_text(prop):
    if not prop or not prop.get("rich_text"):
        return ""
    return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""


def _get_rich_text_from_block(rich_text_array):
    if not rich_text_array:
        return ""
    return "".join([rt["plain_text"] for rt in rich_text_array])


def _get_date(prop):
    if not prop or not prop.get("date"):
        return None
    return prop["date"]["start"] if prop["date"] else None


def _get_select(prop):
    if not prop or not prop.get("select"):
        return None
    return prop["select"]["name"] if prop["select"] else None
