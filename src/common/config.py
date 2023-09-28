#!/usr/bin/python3

import json
import os
import logging


class Constants:
    @classmethod
    def expose_constants(cls, constants_directory):

        is_json_file = lambda file: file.endswith('.json')
        json_files = list(filter(is_json_file, os.listdir(constants_directory)))

        json_files_with_path = [os.path.join(constants_directory, file) for file in json_files]

        for file_path in json_files_with_path:
            file_name = os.path.split(file_path)[1]
            var_name = os.path.splitext(file_name)[0]

            with open(file_path) as json_file:
                data = json.load(json_file)
                setattr(cls, var_name, data)

__constants_directory = os.path.join(os.path.dirname(__file__), 'constants')
Constants.expose_constants(__constants_directory)

if __name__ == '__main__':

    print(dir(Constants))
    print(Constants.chroma, type(Constants.chroma))
    print(Constants.creds, type(Constants.creds))
    print(Constants.rse, type(Constants.rse))