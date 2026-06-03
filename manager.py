from models import Contact
from storage import (
    load_contacts,
    save_contacts
)


class ContactManager:

    def __init__(self):
        self.contacts = load_contacts()

    def add_contact(
        self,
        username,
        name,
        phone
    ):
        contact = Contact(
            username,
            name,
            phone
        )

        self.contacts.append(contact)

        save_contacts(self.contacts)

        return contact

    def list_contacts(self):
        return self.contacts

    def find_contact(self, name):

        for contact in self.contacts:
            if contact.name == name:
                return contact

        return None

    def update_contact(
        self,
        old_name,
        new_name,
        new_phone
    ):

        contact = self.find_contact(old_name)

        if contact:
            contact.name = new_name
            contact.phone = new_phone

            save_contacts(self.contacts)

            return True

        return False

    def delete_contact(self, name):

        contact = self.find_contact(name)

        if contact:
            self.contacts.remove(contact)

            save_contacts(self.contacts)

            return True

        return False

    def save_contacts(self):
        save_contacts(self.contacts)


