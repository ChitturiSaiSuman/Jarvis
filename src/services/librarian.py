#!/usr/bin/python3

import logging
import os
import subprocess
import traceback
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

        self.__SERVICE_ACCOUNT_FILE = Constants.creds["librarian"]["json-key-file"]
        self.__FOLDER_ID = Constants.creds["librarian"]["folder-id"]
        self.__SCOPES = Constants.creds["librarian"]["scopes"]
        self.__FIELDS = Constants.creds["librarian"]["fields"]

    def __initiate_bifrost(self):
        """
        Establish a connection to the Google Drive API.

        Initializes the Google Drive API service by creating and returning
        an authenticated service instance with the provided credentials.

        Returns:
            googleapiclient.discovery.Resource: An authenticated Google Drive API service.
        """

        logging.info("Initializing connection to Google Drive API")

        creds = service_account.Credentials.from_service_account_file(
            self.__SERVICE_ACCOUNT_FILE,
            scopes=self.__SCOPES,
        )
        drive_service = build("drive", "v3", credentials=creds)

        logging.info("Connection to Google Drive API established successfully")
        return drive_service

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

            return {"status": "success", "filepaths": filepaths}

        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": traceback.format_exc()}

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

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

        logging.info(
            f"Searching for files with name matching '{string_to_match}' in {path_to_search}"
        )

        command = (
            f"find {path_to_search} -iname '*{string_to_match}*' -not -path '*/.*'"
        )
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

        logging.info(
            f"Searching for files with content matching '{string_to_match}' in {path_to_search}"
        )

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
                zipf = zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)
            else:
                zipf = pyzipper.AESZipFile(
                    zip_file_path,
                    "w",
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES,
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

            return {"status": "success", "zip_file_path": zip_file_path}

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

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

            drive_service = self.__initiate_bifrost()

            only_file = file_path.split("/")[-1]
            mime_type = MimeTypes().guess_type(only_file)[0]

            file_metadata = {"name": only_file, "parents": [self.__FOLDER_ID]}

            fields_to_fetch = ",".join(self.__FIELDS)

            logging.info(f"Uploading {file_path} to Google Drive")

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = (
                drive_service.files()
                .create(body=file_metadata, media_body=media, fields=fields_to_fetch)
                .execute()
            )

            return {"status": "success"} | {
                field: file.get(field) for field in self.__FIELDS
            }

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

    def enumerate_collection(self) -> dict:
        """
        Retrieves a comprehensive listing of files in the Google Drive collection.

        This method fetches detailed information about all files in the Google Drive,
        including their unique identifiers, names, MIME types, and web view links.

        Returns:
            list: A list containing dictionaries with information about each file in the collection.
                Each dictionary includes 'id', 'name', 'mimeType', and 'webViewLink' fields.

            Example:
                [
                    {'id': 'unique_identifier', 'name': 'file_name', 'mimeType': 'file_mime_type', 'webViewLink': 'web_link'},
                    ...
                ]

            In case of no files found, the returned dictionary includes a success status and a message.

                {'status': 'success', 'message': 'No files found.'}

        Raises:
            Exception: If an error occurs during the retrieval process, an 'error' status
                    along with an error message is returned.

        Note:
            Ensure that proper Google Drive API credentials are set up in the service account file.
        """
        try:
            drive_service = self.__initiate_bifrost()

            results = (
                drive_service.files()
                .list(
                    fields="files(id, name, mimeType, webViewLink)",
                )
                .execute()
            )

            files = results.get("files", [])

            if not files:
                return {"status": "success", "message": "No files found."}

            return {"status": "success", "files": files}

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

    def snap_remote(self, file_id: str) -> dict:
        """
        Remove a file from Google Drive.

        This method initiates the deletion of a file from the connected Google Drive.
        The file is identified by its unique identifier (file_id).

        Args:
            file_id (str): The unique identifier of the file to be removed.

        Returns:
            dict: A dictionary indicating the status of the file removal operation.
                The dictionary includes 'status' and 'message' fields.

                Example:
                    {'status': 'success', 'message': 'File removed successfully.'}

        Raises:
            Exception: If an error occurs during the file removal process,
                an 'error' status along with an error message is returned.

        Note:
            Ensure that proper Google Drive API credentials are set up in the service account file.
        """

        try:
            drive_service = self.__initiate_bifrost()
            drive_service.files().delete(fileId=file_id).execute()

            return {
                "status": "success",
                "message": f'File with ID="{file_id}" removed successfully.',
            }

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

    def purge_remote(self) -> dict:
        """
        Remove all files from Google Drive.

        This method initiates the deletion of all files from the connected Google Drive.
        It iterates through the list of files, deleting each one individually.

        Returns:
            dict: A dictionary indicating the status of the file removal operation.
                The dictionary includes 'status' and 'message' fields.

                Example:
                    {'status': 'success', 'message': 'All files removed successfully.'}

        Raises:
            Exception: If an error occurs during the file removal process,
                an 'error' status along with an error message is returned.

        Note:
            Ensure that proper Google Drive API credentials are set up in the service account file.
        """

        try:
            drive_service = self.__initiate_bifrost()

            results = (
                drive_service.files()
                .list(
                    fields="files(id)",
                )
                .execute()
            )

            files = results.get("files", [])

            # Drop the parent folder from the list
            files = [file for file in files if file["id"] != self.__FOLDER_ID]

            if not files:
                return {"status": "success", "message": "No files found to delete."}

            logging.info(f"Deleting {len(files)} files from Google Drive")

            for file in files:
                drive_service.files().delete(fileId=file["id"]).execute()

            return {"status": "success", "message": "All files removed successfully."}

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

    def clone_to_local(self, file_id: str, destination: str) -> dict:
        """
        Clone a file from Google Drive to the local machine.

        This method downloads a file from Google Drive to the local machine, identified by
        its unique identifier (file_id). The file is saved locally at the specified destination
        path with a filename based on the original file's name.

        Args:
            file_id (str): The unique identifier of the file to be cloned from Google Drive.
            destination (str): The local path where the cloned file will be saved.

        Returns:
            dict: A dictionary indicating the status of the cloning operation.
                The dictionary includes 'status' and 'message' fields.

                Example:
                    {
                        'status': 'success',
                        'message': 'The file has been downloaded to /home/suman/Downloads/file_name'
                    }

        Raises:
            Exception: If an error occurs during the cloning process,
                an 'error' status along with an error message is returned.

        Note:
            Ensure that proper Google Drive API credentials are set up in the service account file.
        """
        try:
            drive_service = self.__initiate_bifrost()
            # check if destination is a file or a directory
            if os.path.isdir(destination):
                # Get the file name from Google Drive
                file = drive_service.files().get(fileId=file_id).execute()
                file_name = file["name"]
                destination_path = os.path.join(destination, file_name)
            else:
                destination_path = destination

            request = drive_service.files().get_media(fileId=file_id)
            fh = open(destination_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)

            logging.info(f"Downloading file with ID={file_id} to {destination_path}")

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logging.info(f"Download progress: {status.progress() * 100} %")

            fh.close()

            return {
                "status": "success",
                "message": f"The file has been downloaded to {destination_path}",
            }

        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}


if __name__ == "__main__":
    print(Librarian().title_tracker("/home/suman/", "pirate"))
