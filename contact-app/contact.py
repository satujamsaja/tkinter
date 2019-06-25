"""
Google contact reader.
"""
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import operator


class ContactApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.wm_title("Contact App")
        self.geometry("600x500")

        # Contact frame.
        self.left_frame = tk.Frame(self, width=200, height=200)
        self.left_frame.pack(side=tk.LEFT, anchor="w", fill=tk.Y)
        self.right_frame = tk.Frame(self, width=200, height=200)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, anchor="w", expand=tk.YES)

        # Search field.
        self.keyword = tk.StringVar()
        self.search_field = tk.Entry(self.left_frame, textvariable=self.keyword)
        self.search_field.pack(fill=tk.BOTH, padx=5, pady=5)
        self.search_field.bind('<KeyRelease>', self.filter_contacts)


        # Tree view
        self.contact_view = ttk.Treeview(self.left_frame)
        self.contact_view.heading("#0", text="Contact name")
        self.contact_view.pack(fill=tk.BOTH, expand=tk.YES, padx=5)
        self.contact_view.bind('<Button-1>', self.view_contact)

        # Contact detail
        self.contact_name = tk.Label(self.right_frame, text="Name:")
        self.contact_name.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.phone_number = tk.Label(self.right_frame, text="Phone:")
        self.phone_number.grid(row=1, column=0, sticky=tk.W, pady=5)

        # People API get credentials.
        self.SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
        self.creds = None
        self.service = self.get_credentials()
        self.contacts = self.get_contacts()


    """
    Validate with google and get people api permission.   
    """
    def get_credentials(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        return build('people', 'v1', credentials=self.creds)

    """
    Get contact list from People API.
    """
    def get_contacts(self):
        if self.service:
            contacts = self.service.people().connections().list(
                resourceName='people/me',
                pageSize=500,
                sortOrder='FIRST_NAME_ASCENDING',
                personFields='names,emailAddresses,phoneNumbers,emailAddresses,addresses').execute()
            connections = contacts.get('connections', [])
            if connections:
                return connections
            else:
                return None

        else:
            showinfo("Service error", "Unable to connect Google API service.")

    """
    Display contact list.
    """
    def display_contacts(self):
        if self.contacts:
            for key, contact in enumerate(self.contacts):
                names = contact.get('names', [])
                if names:
                    self.contact_view.insert('', tk.END, "contact-{}".format(key), text=names[0].get('displayName'))

        else:
            showinfo("Data error", "Unable to get contact data")

    """
    Search and filter contact.
    """
    def filter_contacts(self, event):
        # Capture key release
        if event.type.value == '3':
            keyword = self.keyword.get()
            children = self.contact_view.get_children()
            if keyword.strip() != "":
                count = 0
                for child in children:
                    text = self.contact_view.item(child, "text")
                    if not operator.contains(text.lower(), keyword.lower()):
                        self.contact_view.delete(child)
                    else:
                        count +=1
                if count == 0:
                    self.refresh_contact()
            else:
                self.refresh_contact()
    """
    Refresh tree view content.
    """
    def refresh_contact(self):
        children = self.contact_view.get_children()
        # Clean all tree view items.
        for child in children:
            self.contact_view.delete(child)
        # Reload items back.
        self.display_contacts()

    """
    Display contact detail.
    """
    def view_contact(self, event):
        item = self.contact_view.identify('item', event.x, event.y)
        if item:
            item_split = item.split('-')
            for key, contact in enumerate(self.contacts):
                if key == int(item_split[1]):
                    names = contact.get('names')
                    phones = contact.get('phoneNumbers')
                    # Display data on right section.
                    self.contact_name['text'] = "Name: " + "{}".format(names[0].get('displayName'))
                    if phones:
                        self.phone_number['text'] = "Phone: " + "{}".format(phones[0].get('value'))
                    else:
                        self.phone_number['text'] = "Phone: -"

                    break


if __name__ == "__main__":
    contact_app = ContactApp()
    contact_app.display_contacts()
    contact_app.mainloop()
