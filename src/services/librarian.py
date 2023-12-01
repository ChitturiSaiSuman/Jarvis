#!/usr/bin/python3

import logging
import os
import subprocess
import zipfile
from mimetypes import MimeTypes

import pyzipper
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from src.common.config import Constants


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

        self.__SERVICE_ACCOUNT_FILE = Constants.creds['librarian']['json-key-file']
        self.__FOLDER_ID = Constants.creds['librarian']['folder-id']
        self.__SCOPES = Constants.creds['librarian']['scopes']
        self.__FIELDS = Constants.creds['librarian']['fields']

    def __exec(self, command: str) -> dict:
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
            result = subprocess.check_output(command, shell=True, text=True)

            filenames = str(result).splitlines()
            filepaths = list(map(os.path.normpath, filenames))

            return {
                'status': 'success',
                'filepaths': filepaths
            }

        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def title_tracker(self, path_to_search: str, string_to_match: str) -> dict:
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

        command = f"find {path_to_search} -iname '*{string_to_match}*' -not -path '*/.*'"
        return self.__exec(command)

    def content_curator(self, path_to_search: str, string_to_match: str) -> dict:
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

    def archive_creator(self, path_to_archive: str, password: str) -> dict:
        """
        Create a zip archive of a file or folder. Optionally password protect the archive.

        This method takes a file or folder path as input, along with a password (optional),
        and creates a zip archive containing the specified file
        or folder. The resulting zip file is stored in the same location as the
        original file or folder.

        Args:
            path_to_archive (str): The path to the file or folder to be archived.
            password (str): The password to protect the zip archive. If None, Archive will not be encrypted.

        Returns:
            str: The path to the created (password-protected) zip archive.
        """

        try:
            # Check if the path exists
            if not os.path.exists(path_to_archive):
                raise Exception(f"Cannot find {path_to_archive}")

            # Extract the directory and file name
            dir_name, base_name = os.path.split(path_to_archive)

            # Construct the path for the zip archive
            zip_file_path = os.path.join(dir_name, f"{base_name}.zip")

            if password == None:
                zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
            else:
                zipf = pyzipper.AESZipFile(
                    zip_file_path,
                    'w',
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES
                )
                zipf.pwd = password.encode()

            if os.path.isdir(path_to_archive):
                # If it's a folder, add its contents to the archive
                for folder_root, _, files in os.walk(path_to_archive):
                    for file in files:
                        file_path = os.path.join(folder_root, file)
                        arcname = os.path.relpath(file_path, path_to_archive)
                        zipf.write(file_path, arcname=arcname)
            else:
                # If it's a file, add the file itself to the archive
                zipf.write(path_to_archive, arcname=base_name)

            return {
                'status': 'success',
                'zip_file_path': zip_file_path
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def tome_transporter(self, file_path: str) -> dict:
        """
        Upload a file to Google Drive and return a shareable link.

        This method uploads a file to Google Drive, and upon successful upload,
        it returns a shareable link to the uploaded file.

        Args:
            file_path (str): The local file path to the file to be uploaded.

        Returns:
            str: The shareable web link to the uploaded file on Google Drive.
        """

        try:

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

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields=fields_to_fetch
            ).execute()

            return {
                'status': 'success'
            } | {
                field: file.get(field) for field in self.__FIELDS
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        
    def download_file(self, file_id, index):
        try:

            destination_path = f'/home/suman/{index}.tar.gz'
            log_file = f'/home/suman/{index}.txt'
            log_file = open(log_file, 'w')

            creds = service_account.Credentials.from_service_account_file(
                self.__SERVICE_ACCOUNT_FILE,
                scopes=self.__SCOPES,
            )

            drive_service = build('drive', 'v3', credentials=creds)

            request = drive_service.files().get_media(fileId=file_id)
            fh = open(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                log_file.write(str(status.progress()) + '\n')
                log_file.flush()

            log_file.write(str(done) + '\n')
            log_file.flush()

            fh.close()

            some_return = {
                'status': 'success',
                'message': f'The file has been downloaded to {destination_path}'
            }

            log_file.write(str(some_return) + '\n')
            log_file.flush()

            log_file.close()

            return some_return

        except Exception as e:
            err_return = {
                'status': 'error',
                'message': str(e)
            }
            log_file.write(str(err_return) + '\n')
            log_file.flush()
            log_file.close()
            return err_return


def download():
    ids = []
    for index, file_id in enumerate(ids):
        print(Librarian().download_file(file_id, index))

if __name__ == '__main__':
    print(Librarian().title_tracker('/home/suman/', 'pirate'))