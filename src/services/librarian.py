import logging
import os
import subprocess
from mimetypes import MimeTypes

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.common import config


class Librarian:
    def __init__(self):
        """
        Initializes the Librarian class, setting up the necessary configurations and credentials.

        This constructor sets up the Google Drive API configuration parameters, including
        the service account file, folder ID, and scopes required for authentication.

        Attributes:
            self.__SERVICE_ACCOUNT_FILE (str): Path to the service account JSON key file.
            self.__FOLDER_ID (str): ID of the folder in which files will be uploaded.
            self.__SCOPES (list): List of scopes required for authentication.
            self.__FIELDS (list): List of fields to fetch upon successful upload.
        """

        self.__SERVICE_ACCOUNT_FILE = config.Constants.creds['librarian']['json-key-file']
        self.__FOLDER_ID = config.Constants.creds['librarian']['folder-id']
        self.__SCOPES = config.Constants.creds['librarian']['scopes']
        self.__FIELDS = config.Constants.creds['librarian']['fields']

    def __exec(self, command: str) -> list:
        """
        Execute a shell command and return a list of file paths.

        This private method is used internally to execute shell commands and retrieve
        a list of file paths based on the command's output.

        Args:
            command (str): The shell command to execute.

        Returns:
            list: A list of file paths resulting from the executed command.
        """

        try:
            result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                raise Exception(result.stderr)
            
            filenames = result.stdout.splitlines()
            filepaths = list(map(os.path.normpath, filenames))
            return filepaths
        
        except Exception as e:
            return str(e)

    def title_tracker(self, path_to_search: str, string_to_match: str) -> list:
        """
        Search for files with a specific string in their names.

        This method searches for files in the specified directory and its subdirectories
        that contain a given string in their filenames.

        Args:
            path_to_search (str): The directory path to start the search from.
            string_to_match (str): The string to match in the filenames.

        Returns:
            list: A list of file paths matching the search criteria.
        """

        command = f"find {path_to_search} -type f -name '*{string_to_match}*' -not -path '*/.*'"
        return self.__exec(command)

    def content_curator(self, path_to_search: str, string_to_match: str) -> list:
        """
        Search for files containing a specific string in their content.

        This method searches for files in the specified directory and its subdirectories
        that contain a given string within their content using the 'grep' command.

        Args:
            path_to_search (str): The directory path to start the search from.
            string_to_match (str): The string to match within the file content.

        Returns:
            list: A list of file paths whose content matches the search criteria.
        """

        command = f"find {path_to_search} -type f -exec grep -li '{string_to_match}' {{}} + -not -path '*/.*'"
        return self.__exec(command)
    
    def tome_transporter(self, file_path: str) -> str:
        """
        Upload a file to Google Drive and return a shareable link.

        This method uploads a file to Google Drive, and upon successful upload,
        it returns a shareable link to the uploaded file.

        Args:
            file_path (str): The local file path to the file to be uploaded.

        Returns:
            str: The shareable web link to the uploaded file on Google Drive.
        """

        if not os.path.exists(file_path):
            raise Exception(f"Cannot find {file_path}")
        
        creds = service_account.Credentials.from_service_account_file(
            self.__SERVICE_ACCOUNT_FILE,
            scopes=self.__SCOPES,
        )
        drive_service = build('drive', 'v3', credentials=creds)

        only_file = file_path.split('/')[-1]
        mime_type = MimeTypes().guess_type(only_file)[0]

        file_metadata = {
            'name': only_file,
            'parents': [self.__FOLDER_ID]
        }

        fields_to_fetch = ','.join(self.__FIELDS)

        try:
            media = MediaFileUpload(file_path, mimetype=mime_type)

            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields=fields_to_fetch
            ).execute()

            return {
                field: file.get(field) for field in self.__FIELDS
            }
        
        except Exception as e:
            return str(e)


if __name__ == '__main__':
    print(Librarian().title_tracker('/home/suman/', 'pirate'))