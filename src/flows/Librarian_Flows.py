import collections
import os

from src.common.Flow import Flow
from src.services.librarian import Librarian


class FileLocator(Flow):
    """
    Locates a File in the Local (Secondary) Storage

    Trigger:
        !locate

    Execution Args:
        path (str): Directory to search in
        pattern (str): String to match
        domain (str): Either "title" or "content"

    Raises:
        ValueError: If any of the Args are not provided

    Notes:
        "path" must be a valid path.

    Example args: {
        "path": "/home/suman",
        "pattern": "Example.txt",
        "domain": "title"
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!locate'
    
    def exec(self, args: collections.defaultdict) -> dict:
        try:
            path_to_search = args.get('path')
            string_to_match = args.get('pattern')
            domain = args.get('domain')

            if domain not in ['title', 'content']:
                raise ValueError('Invalid value for domain. domain must be in ["title", "content"]')
            
            lib = Librarian()

            if domain == 'title':
                files = lib.title_tracker(path_to_search, string_to_match)
            else:
                files = lib.content_curator(path_to_search, string_to_match)

            self.traces.append(files)

            if isinstance(files, list):
                return {
                    'response': files
                }
            else:
                return {
                    'error': files
                }

        except Exception as e:
            return {
                '': str(e)
            }
        
    @classmethod
    def ps(cls) -> list:
        return cls.traces
    
    @classmethod
    def purge(cls) -> bool:
        try:
            cls.traces.clear()
            return True
        except:
            return False
        
class FileUploader(Flow):
    """
    Uploads a File to Google Drive Storage using API

    Trigger:
        !upload:
    
    Execution Args:
        path (str): The path to the file or folder to be uploaded
        compress (bool) [True/False]: Whether to compress the file in a Zip
        password (str) [Optional]: Password to protect the zip

    Notes:
        "path" must be a valid path.
        If "path" points to a valid directory, the directory will be automatically zipped irrespective of the compress option.
        If "path" points to a valid file, "compress" will decide whether the file should be zipped or not.
        "password", if provided, must not contain spaces.

    Example args:
    Example 1: {
        "path": "/home/suman/Jarvis",
        "compress": false, # Not considered since Jarvis is a directory
        "password": "hello"
    }
    Example 2: {
        "path": "/home/suman/Music/Sample.mp3",
        "compress": false
    }
    Example 3: {
        "path": "/home/suman/Documents",
        "compress": true
        # If password is not provided, directory will not be encrypted
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return "!upload"
    
    def exec(self, args: collections.defaultdict) -> dict:
        try:
            file_path = args.get('path')
            compress = os.path.isdir(file_path) or args.get('compress')
            lib = Librarian()
            if compress:
                password = args.get('password', None)
                file_path = lib.archive_creator(file_path, password)
            
            fields = lib.tome_transporter(file_path)

            self.traces.append(file_path)
            return {
                'response': fields
            }

        except Exception as e:
            return {
                'error': str(e)
            }
        
    @classmethod
    def ps(cls) -> list:
        return cls.traces
    
    @classmethod
    def purge(cls) -> bool:
        try:
            cls.traces.clear()
            return True
        except:
            return False