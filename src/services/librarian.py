import subprocess, os

class Librarian:
    def __init__(self):
        pass

    def __exec(self, command: str) -> list:
        try:
            result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                raise Exception(result.stderr)
            
            filenames = result.stdout.splitlines()
            filepaths = list(map(os.path.normpath, filenames))
            return filepaths
        
        except Exception as e:
            return str(e)

    def title_tracker(self, path_to_search, string_to_match) -> list:
        command = f"find {path_to_search} -type f -name '*{string_to_match}*'"
        return self.__exec(command)

    def content_curator(self, path_to_search, string_to_match) -> list:
        command = f"find {path_to_search} -type f -exec grep -li '{string_to_match}' {{}} +"
        return self.__exec(command)


if __name__ == '__main__':
    print(Librarian().title_tracker('/home/suman/', 'pirate'))