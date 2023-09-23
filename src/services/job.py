from abc import ABC, abstractmethod
import collections, os, pathlib, subprocess

class Job:
    """
    Base class for defininig a Job's structure

    This class provides a virtual structure for a Job and requires
    subclasses to implement the abstract methods defined here.

    Subclasses inheriting from this class must implement the following abstract methods:
        - get_signature(): Returns the Language String
        - prepare(): Get the environment ready for execution
        - run(): Run Remote Script Execution
        - get_status(): Get the current status of the Job
        - purge(): Perform any necessary cleanup after Execution
    """

    @classmethod
    @abstractmethod
    def get_signature(cls) -> str:
        """
        Abstract method to return Language String
        """
        pass

    @abstractmethod
    def prepare(self, args: collections.defaultdict) -> collections.defaultdict:
        """
        Abstract method that prepares the environment for Remote Script Execution

        This method should be implemented by subclasses to define the environment setup

        Raises:
            NotImplementedError: If the method is not implemented by the subclass
        """
        pass

    @abstractmethod
    def run(self) -> collections.defaultdict:
        """
        Abstract method to execute the Script

        This method should be implemented by subclasses to run the Remote Script.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    def start(self, args: collections.defaultdict) -> collections.defaultdict:
        """
        Method that calls prepare and run internally

        Collects the returned values from both routines,
        consolidates and sends them to the caller
        """
        response = collections.defaultdict()

        try:
            response['Job.prepare()'] = self.prepare(args)
            response['Job.run()'] = self.run()
        except Exception as e:
            response['error'] = str(e)

        return response

    @classmethod
    @abstractmethod
    def get_status(cls) -> list:
        """
        Abstract method to show the current status of the Job.

        This method should be implemented by subclasses to display the current
        status information of the Job.

        Raises:
            NotImplementedErr
        """
        pass

    @classmethod
    @abstractmethod
    def purge(cls) -> bool:
        """
        Abstract method to perform any necessary clean-up after the Job has finished.

        This method should be implemented by subclasses to perform any necessary
        clean-up steps required after the Script has finished executing.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass