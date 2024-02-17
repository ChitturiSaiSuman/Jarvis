#!/usr/bin/python3

import collections
import logging
import os
import pathlib
import subprocess
import traceback

import src.common.config as config
from src.services import job


class Executor:
    @classmethod
    def set_attributes(cls, obj: job.Job, args: collections.defaultdict) -> None:
        for key, value in args.items():
            setattr(obj, key, value)

        # Set default Time Limit and Memory Limit if not provided

        if 'time_limit' not in args:
            setattr(obj, 'time_limit', config.Constants.rse['time_limit'][obj.lang])
            
        if 'memory_limit' not in args:
            setattr(obj, 'memory_limit', 1024 * config.Constants.rse['memory_limit'][obj.lang])

    @classmethod
    def prepare_files(cls, job: job.Job) -> tuple:
        try:
            path = os.path.join(job.path, job.source_file_name)
            with open(path, 'w') as source_file:
                source_file.write(job.source)
            return True, path
        except Exception as e:
            return False, traceback.format_exc()

    @classmethod
    def get_timeout_perl(cls) -> str:
        return os.path.dirname(__file__)

    @staticmethod
    def prep(task: job.Job, shell_cmds: list) -> collections.defaultdict:
        response = collections.defaultdict()
        try:
            process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=task.path, input=task.source, text=True)

            response['status'] = 'success'
            response['stdout'] = process.stdout
            response['stderr'] = process.stderr

        except subprocess.CalledProcessError as e:
            response['status'] = 'error'
            response['message'] = traceback.format_exc()
            response['stdout'] = e.stdout
            response['stderr'] = e.stderr

        except Exception as e:
            response['status'] = 'error'
            response['message'] = traceback.format_exc()

        return response

    @staticmethod
    def exec(task: job.Job, shell_cmds: list) -> collections.defaultdict:
        response = collections.defaultdict()
        try:
            time_limit = str(task.time_limit)
            memory_limit = str(task.memory_limit)
            timeout_perl = os.path.join(os.path.dirname(__file__), 'timeout.pl')

            shell_cmds = ['perl', timeout_perl, '-t', time_limit, '-m', memory_limit] + shell_cmds

            process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=task.path, input=task.stdin, text=True)
            
            response['status'] = 'success'
            response['stdout'] = process.stdout
            response['stderr'] = process.stderr

        except subprocess.CalledProcessError as e:
            response['status'] = 'error'
            response['message'] = traceback.format_exc()
            response['stdout'] = e.stdout
            response['stderr'] = e.stderr

        except Exception as e:
            response['status'] = 'error'
            response['message'] = traceback.format_exc()

        return response

    '''
    Classes implementing the job.Job Class.
    Each class defines execution logic for a specific Language
    '''

    class C(job.Job):
        auxiliary_data = collections.defaultdict()

        @classmethod
        def get_signature(cls) -> str:
            return "C"

        def prepare(self, args: collections.defaultdict) -> collections.defaultdict:
            Executor.set_attributes(self, args)
            self.executable = os.path.join(self.path, 'exe')
            shell_cmds = ['gcc', '-xc', '-', '-o', self.executable, '-lm']
            return Executor.prep(self, shell_cmds)

        def run(self) -> collections.defaultdict:
            shell_cmds = [self.executable]
            return Executor.exec(self, shell_cmds)
            
        @classmethod
        def get_status(cls) -> list:
            # TODO: Implement the method
            return super().get_status()

        @classmethod
        def purge(cls) -> bool:
            # TODO: Implement the method
            return super().purge()

    class CPP(job.Job):
        auxiliary_data = collections.defaultdict()

        @classmethod
        def signature(cls) -> str:
            return "CPP"

        def prepare(self, args: collections.defaultdict) -> collections.defaultdict:
            Executor.set_attributes(self, args)
            self.executable = os.path.join(self.path, 'exe')
            shell_cmds = ['g++', '-std=c++17', '-Wshadow', '-Wall', '-o', self.executable, '-O2', '-Wno-unused-result', '-xc++', '-']
            return Executor.prep(self, shell_cmds)

        def run(self) -> collections.defaultdict:
            shell_cmds = [self.executable]
            return Executor.exec(self, shell_cmds)

        @classmethod
        def get_status(cls) -> list:
            # TODO: Implement the method
            return super().get_status()

        @classmethod
        def purge(cls) -> bool:
            # TODO: Implement the method
            return super().purge()

    class JAVA(job.Job):
        auxiliary_data = collections.defaultdict()

        @classmethod
        def signature(cls) -> str:
            return "JAVA"

        def __get_main_method_classes(self) -> list:
            def disassemble(class_file: str) -> str:
                return subprocess.check_output(['javap', class_file], text=True, cwd=self.path)

            is_class_file = lambda file: file.suffix == '.class'
            has_main_method = lambda byte_code: 'public static void main' in byte_code

            class_files = list(filter(is_class_file, self.target_directory.iterdir()))
            byte_codes = list(map(disassemble, class_files))

            main_method_classes = [class_file.stem for class_file, byte_code in zip(class_files, byte_codes) if has_main_method(byte_code)]
            return main_method_classes

        def prepare(self, args: collections.defaultdict) -> collections.defaultdict:
            response = collections.defaultdict()
            try:
                Executor.set_attributes(self, args)
                created, output = Executor.prepare_files(self)

                if not created:
                    response['status'] = 'error'
                    response['message'] = output
                    return response

                self.target_directory = pathlib.Path(self.path)

                shell_cmds = ['javac', output]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, text=True)

                response['status'] = 'success'
                response['stdout'] = process.stdout
                response['stderr'] = process.stderr

                if process.returncode != 0:
                    return response
                else:
                    main_method_classes = self.__get_main_method_classes()
                    if len(main_method_classes) == 1:
                        self.main_class = main_method_classes[0]
                        response['Main Class'] = str(self.main_class)
                    else:
                        response.clear()
                        if len(main_method_classes) == 0:
                            response['status'] = 'error'
                            response['message'] = 'No main methods found'
                        elif len(main_method_classes) > 1:
                            response['status'] = 'error'
                            response['message'] = 'Multiple main methods found'

                        return response

            except subprocess.CalledProcessError as e:
                response['status'] = 'error'
                response['message'] = traceback.format_exc()
                response['stdout'] = e.stdout
                response['stderr'] = e.stderr

            except Exception as e:
                response['status'] = 'error'
                response['message'] = traceback.format_exc()

            return response

        def run(self) -> dict:
            shell_cmds = ['java', '-cp', self.path, self.main_class]
            return Executor.exec(self, shell_cmds)

        @classmethod
        def get_status(cls) -> list:
            # TODO: Implement the method
            return super().get_status()

        @classmethod
        def purge(cls) -> bool:
            # TODO: Implement the method
            return super().purge()

    class PYTHON(job.Job):
        auxiliary_data = collections.defaultdict()

        @classmethod
        def signature(cls) -> str:
            return "PYTHON"

        def prepare(self, args: collections.defaultdict) -> collections.defaultdict:
            response = collections.defaultdict()
            try:
                Executor.set_attributes(self, args)
                response['status'] = 'success'
            except Exception as e:
                response['status'] = 'error'
                response['message'] = traceback.format_exc()
            return response

        def run(self) -> dict:
            shell_cmds = ['python3', '-c', self.source]
            return Executor.exec(self, shell_cmds)

        @classmethod
        def get_status(cls) -> list:
            # TODO: Implement the method
            return super().get_status()

        @classmethod
        def purge(cls) -> bool:
            # TODO: Implement the method
            return super().purge()