from src.services import job
import collections, os, pathlib, subprocess

class Executor:
    @classmethod
    def set_attributes(cls, obj: job.Job, args: collections.defaultdict) -> None:
        for key, value in args.items():
            setattr(obj, key, value)
        timeout_perl = os.path.join(os.path.dirname(__file__), 'timeout.pl')
        setattr(obj, 'timeout_perl', timeout_perl)

    @classmethod
    def prepare_files(cls, job: job.Job) -> str:
        try:
            path = os.path.join(job.path, job.source_file_name)
            with open(path, 'w') as source_file:
                source_file.write(job.source)
            return path
        except:
            return None
        
    @classmethod
    def get_timeout_perl(cls) -> str:
        return os.path.dirname(__file__)

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
            response = collections.defaultdict()
            try:
                Executor.set_attributes(self, args)
                self.executable = os.path.join(self.path, 'exe')
                shell_cmds = ['gcc', '-xc', '-', '-o', self.executable, '-lm']
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.source, text=True)
                response['compilation_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)

            return response

        def run(self) -> collections.defaultdict:
            response = collections.defaultdict()
            try:
                time_limit = str(self.time_limit)
                memory_limit = str(self.memory_limit)
                shell_cmds = ['perl', self.timeout_perl, '-t', time_limit, '-m', memory_limit, self.executable]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.stdin, text=True)
                response['execution_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)
            
            return response

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
            response = collections.defaultdict()
            try:
                Executor.set_attributes(self, args)
                self.executable = os.path.join(self.path, 'exe')
                shell_cmds = ['g++', '-std=c++17', '-Wshadow', '-Wall', '-o', self.executable, '-O2', '-Wno-unused-result', '-xc++', '-']
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.source, text=True)
                response['compilation_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)

            return response
        
        def run(self) -> collections.defaultdict:
            response = collections.defaultdict()
            try:
                time_limit = str(self.time_limit)
                memory_limit = str(self.memory_limit)
                shell_cmds = ['perl', self.timeout_perl, '-t', time_limit, '-m', memory_limit, self.executable]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.stdin, text=True)
                response['execution_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)
            
            return response

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
                return subprocess.check_output(['javap', class_file], capture_output=True, text=True, cwd=self.path)
            
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
                source_file = Executor.prepare_files(self)

                self.current_directory = pathlib.Path.cwd()
                self.target_directory = pathlib.Path(self.path)

                shell_cmds = ['javac', source_file]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, text=True)
                response['compilation_log'] = process.stdout, process.stderr

                if process.returncode != 0:
                    return response
                else:
                    main_method_classes = self.__get_main_method_classes()
                    if len(main_method_classes) == 1:
                        self.main_class = main_method_classes[0]
                        response['Identified Main Class'] = str(self.main_class)
                    else:
                        if len(main_method_classes) == 0:
                            response['error'] = 'No main methods found'
                        elif len(main_method_classes) > 1:
                            response['error'] = 'Multiple main methods found'
                        return response

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)

            return response
        
        def run(self) -> dict:
            response = collections.defaultdict()
            try:
                time_limit = str(self.time_limit)
                memory_limit = str(self.memory_limit)
                shell_cmds = ['perl', self.timeout_perl, '-t', time_limit, '-m', memory_limit, 'java', '-cp', self.path, self.main_class]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.stdin, text=True)
                response['execution_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)
            
            return response

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
                response['log'] = 'ready'
            except Exception as e:
                response['error'] = str(e)
            return response
        
        def run(self) -> dict:
            response = collections.defaultdict()
            try:
                time_limit = str(self.time_limit)
                memory_limit = str(self.memory_limit)
                shell_cmds = ['perl', self.timeout_perl, '-t', time_limit, '-m', memory_limit, 'python3', '-c', self.source]
                process = subprocess.run(shell_cmds, capture_output=True, check=True, cwd=self.path, input=self.stdin, text=True)
                response['execution_log'] = process.stdout, process.stderr

            except subprocess.CalledProcessError as e:
                response['error'] = str(e), e.stdout, e.stderr
            except Exception as e:
                response['error'] = str(e)
            
            return response

        @classmethod
        def get_status(cls) -> list:
            # TODO: Implement the method
            return super().get_status()
        
        @classmethod
        def purge(cls) -> bool:
            # TODO: Implement the method
            return super().purge()