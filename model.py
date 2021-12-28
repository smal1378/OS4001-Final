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


class ScheduleFCFS(ScheduleMother):
    def __init__(self):
        self.processes = []
        self.gant_output = []
        self.calc = False  # Whether a simulation has been done or not

    def add_process(self, process: Process):
        self.processes.append(process)

    def _calc(self):
        self.gant_output.clear()
        # we need a simple queue to add processes into it in order of getting in
        queue: List[Process] = sorted(self.processes, key=lambda e: e.enter)
        # queue.pop(0) will return first element in queue,

        time = queue[0].enter  # time starts when first process entered
        while queue:  # until there is process
            process = queue.pop(0)
            self.gant_output.append((time, process.name))
            time += process.calc
            process.response = time - process.enter  # exit time - enter time
            process.waiting = time - process.calc - process.enter  # exit - calculate time - enter
        self.calc = True

    def get_output(self) -> List[Process]:
        if not self.calc:
            self._calc()
        return self.processes.copy()

    def get_gant(self) -> List[Tuple[int, str]]:
        if not self.calc:
            self._calc()
        return self.gant_output.copy()

