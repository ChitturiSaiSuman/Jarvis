import json
import os
from mimetypes import MimeTypes

import requests
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Set the path to your OAuth 2.0 Client ID JSON file (replace with your file)
CLIENT_ID_FILE = '<CLIENT_ID_FILE>.json'

SCOPES = ['https://www.googleapis.com/auth/drive']

# flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=SCOPES,
)

service = build('drive', 'v3', credentials=creds)

# Set the folder ID where you want to upload the file (replace with your folder ID)
FOLDER_ID = '<FOLDER_ID>'

# Path to the file you want to upload
filepath = 'names.txt'

# Define the MIME type for the file (replace with the appropriate MIME type)
MIME_TYPE = 'text/plain'  # Example for a plain text file, adjust accordingly

name = filepath.split('/')[-1]

# Find the MimeType of the file
mimetype = MimeTypes().guess_type(name)[0]

# create file metadata
file_metadata = {
    'name': name,
    'parents': [FOLDER_ID]
}

try:
    media = MediaFileUpload(filepath, mimetype=mimetype)

    # Create a new file in the Drive storage
    file = service.files().create(
        body=file_metadata, media_body=media, fields='id').execute()

    print("File Uploaded To GDrive.")

except Exception as e:
    print(e)
    # Raise UploadError if file is not uploaded.
    print("Can't Upload File To GDrive.")