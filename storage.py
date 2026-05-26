import json
import os

from models import Contact


CONTACTS_FILE = "contacts.json"


def load_contacts():

    if not os.path.exists(CONTACTS_FILE):
        return []

    with open(CONTACTS_FILE, "r") as f:

        try:
            data = json.load(f)

        except json.JSONDecodeError:
            return []

    return [
        Contact.from_dict(contact)
        for contact in data
    ]


def save_contacts(contacts):

    data = [
        contact.to_dict()
        for contact in contacts
    ]

    with open(CONTACTS_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=4
        )