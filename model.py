from typing import List, Tuple, Optional


class Process:
    class States:
        """Just To Indicate A Process State"""

    HALT = States()  # A Process That Is Not Running
    RUN = States()  # Current Running Process
    EXIT = States()  # Finished

    def __init__(self, name: str, enter_time: int, calc_time: int):
        self.name = name
        self.enter = enter_time
        self.calc = calc_time
        self.state = Process.HALT
        self.response: Optional[int] = None
        self.waiting: Optional[int] = None


class ScheduleMother:
    """
        Mother Class Of Process Schedulers.
        Each Scheduling Method Should Be Defined By Creating A Subclass Of This Class.
    """
    def add_process(self, process: Process):
        raise NotImplemented

    def get_output(self) -> List[Process]:
        """
            Returns A List Of Processes That 'response' And 'waiting' Attributes Are Set.
        """
        raise NotImplemented

    def get_gant(self) -> List[Tuple[int, str]]:
        """
            Returns A List Of Tuples Of An Integer And An String,
            Integer Is The Starting Time Of A Process
            String Is The Name Of That Process.
        """
        raise NotImplemented

