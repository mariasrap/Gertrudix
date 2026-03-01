#!/usr/bin/env python3
"""Test script to verify Notion connection and read current data."""

from client import get_applications, get_contacts, get_todo_page

def main():
    print("=" * 60)
    print("GERTRUDIX - Notion Connection Test")
    print("=" * 60)

    # Test Applications
    print("\n📋 APPLICATIONS LOG")
    print("-" * 40)
    try:
        applications = get_applications()
        if applications:
            for app in applications:
                print(f"  • {app['company']} - {app['role']}")
                print(f"    Status: {app['status']} | Date: {app['date']}")
                if app['notes']:
                    print(f"    Notes: {app['notes']}")
                print()
        else:
            print("  No applications found.")
    except Exception as e:
        print(f"  Error reading applications: {e}")

    # Test Contacts
    print("\n👥 CONTACTS")
    print("-" * 40)
    try:
        contacts = get_contacts()
        if contacts:
            for contact in contacts:
                print(f"  • {contact['name']}")
                if contact['company'] or contact['role']:
                    print(f"    {contact['role']} at {contact['company']}")
                print(f"    Status: {contact['status']} | Last Contact: {contact['last_contact']}")
                if contact['notes']:
                    print(f"    Notes: {contact['notes']}")
                print()
        else:
            print("  No contacts found.")
    except Exception as e:
        print(f"  Error reading contacts: {e}")

    # Test To-Do Page
    print("\n✅ TO-DO LIST")
    print("-" * 40)
    try:
        todos = get_todo_page()
        if "error" in todos:
            print(f"  {todos['error']}")
        elif todos.get("categories"):
            for category, items in todos["categories"].items():
                print(f"\n  [{category}]")
                if items:
                    for item in items:
                        checkbox = "☑" if item["checked"] else "☐"
                        print(f"    {checkbox} {item['text']}")
                else:
                    print("    (empty)")
        else:
            print("  No to-do categories found.")
    except Exception as e:
        print(f"  Error reading to-do list: {e}")

    print("\n" + "=" * 60)
    print("Connection test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
