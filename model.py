import os.path
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
    name = ""  # name of scheduler

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
    name = "FCFS"  # name of scheduler

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
        self.gant_output.append((time, 'END'))
        self.calc = True

    def get_output(self) -> List[Process]:
        if not self.calc:
            self._calc()
        return self.processes.copy()

    def get_gant(self) -> List[Tuple[int, str]]:
        if not self.calc:
            self._calc()
        return self.gant_output.copy()


class ScheduleRR(ScheduleMother):
    name = 'RR'

    def __init__(self, quant: int = 10, change_time: int = 2):
        self.processes: List[Process] = []
        self.gant_chart = []
        self._quant = quant
        self._change_time = change_time
        self._is_calc = False

    def add_process(self, process: Process):
        self.processes.append(process)
        self._is_calc = False

    def get_output(self) -> List[Process]:
        if not self._is_calc:
            self._calc()
        return self.processes.copy()

    def get_gant(self):
        if not self._is_calc:
            self._calc()
        return self.gant_chart

    def _calc(self):
        self.gant_chart.clear()
        if not self.processes:
            return
        queue: List[Tuple[Process, int]] = [(i, i.calc) for i in sorted(self.processes, key=lambda e: e.enter)]
        time = queue[0][0].enter
        while queue:
            process, left_time = queue.pop(0)
            self.gant_chart.append((time, process.name))
            if left_time <= self._quant:
                time += left_time
                process.response = time - process.enter  # exit time - enter time
                process.waiting = time - process.calc - process.enter  # exit - calculate time - enter
            else:
                time += self._quant
                queue.append((process, left_time-self._quant))
            self.gant_chart.append((time, 'QUANT'))
            time += self._change_time
        self.gant_chart.pop()
        self.gant_chart.append((time-self._change_time, "END"))


class ScheduleSPN(ScheduleMother):
    name = "SPN/SJF"

    def __init__(self):
        self.queue1: List[Process] = []
        self.gant_chart = []
        self._is_calc = False

    def get_gant(self):
        if not self._is_calc:
            self._calc()
        return self.gant_chart

    def add_process(self, process: Process):
        self.queue1.append(process)
        self._is_calc = False

    def get_output(self):
        if not self._is_calc:
            self._calc()
        return self.queue1.copy()

    def _calc(self):
        self.gant_chart.clear()
        self._is_calc = True
        queue1 = sorted(self.queue1, key=lambda e: e.enter)
        priority_queue = []
        time = queue1[0].enter
        while queue1 or priority_queue:
            while queue1 and queue1[0].enter <= time:
                self._priority_add_helper(priority_queue, queue1.pop(0))
            time_left, elem = priority_queue.pop(0)
            self.gant_chart.append((time, elem.name))
            time += time_left
            elem.response = time - elem.enter  # exit time - enter time
            elem.waiting = time - elem.calc - elem.enter  # exit - calculate time - enter
        self.gant_chart.append((time, "END"))

    @staticmethod
    def _priority_add_helper(queue: List[Tuple[int, Process]], element: Process, time_left: int = 0):
        if time_left == 0:
            time_left = element.calc
        if queue:
            for index, (time_left1, elem) in enumerate(queue):
                if time_left1 > time_left:
                    queue.insert(index, (time_left, element))
                    return
        queue.append((time_left, element))


class ScheduleSRT(ScheduleMother):
    name = "SRT"

    def __init__(self):
        self.queue1: List[Process] = []
        self.gant_chart = []
        self._is_calc = False

    def get_gant(self):
        if not self._is_calc:
            self._calc()
        return self.gant_chart

    def add_process(self, process: Process):
        self.queue1.append(process)
        self._is_calc = False

    def get_output(self):
        if not self._is_calc:
            self._calc()
        return self.queue1.copy()

    def _calc(self):
        self.gant_chart.clear()
        self._is_calc = True
        queue1 = sorted(self.queue1, key=lambda e: e.enter)
        priority_queue = []
        time = queue1[0].enter
        old_elem = None
        while queue1 or priority_queue:
            while queue1 and queue1[0].enter <= time:
                self._priority_add_helper(priority_queue, queue1.pop(0))
            time_left, elem = priority_queue.pop(0)
            if (old_elem and old_elem is not elem) or not old_elem:  # not elem is for first time
                self.gant_chart.append((time, elem.name))
            old_elem = elem
            if queue1 and queue1[0].enter < time_left+time:
                step = queue1[0].enter - time
                time += step
                self._priority_add_helper(priority_queue, elem, time_left-step)
            else:
                # this should end for because it's our first priority
                time += time_left
                elem.response = time - elem.enter  # exit time - enter time
                elem.waiting = time - elem.calc - elem.enter  # exit - calculate time - enter
        self.gant_chart.append((time, "END"))

    @staticmethod
    def _priority_add_helper(queue: List[Tuple[int, Process]], element: Process, time_left: int = 0):
        if time_left == 0:
            time_left = element.calc
        if queue:
            for index, (time_left1, elem) in enumerate(queue):
                if time_left1 > time_left:
                    queue.insert(index, (time_left, element))
                    return
        queue.append((time_left, element))


class ScheduleHRRN(ScheduleMother):
    name = "HRRN"

    def __init__(self):
        self.queue1: List[Process] = []
        self.gant_chart = []
        self._is_calc = False

    def get_gant(self):
        if not self._is_calc:
            self._calc()
        return self.gant_chart

    def add_process(self, process: Process):
        self.queue1.append(process)
        self._is_calc = False

    def get_output(self):
        if not self._is_calc:
            self._calc()
        return self.queue1.copy()

    def _calc(self):
        self.gant_chart.clear()
        self._is_calc = True
        queue1: List[Process] = sorted(self.queue1, key=lambda e: e.enter)
        priority_queue = []
        time = queue1[0].enter
        while queue1 or priority_queue:
            while queue1 and queue1[0].enter <= time:
                self._priority_add_helper(priority_queue, queue1.pop(0), time)
            elem = priority_queue.pop(0)
            self.gant_chart.append((time, elem.name))
            time += elem.calc
            elem.response = time - elem.enter  # exit time - enter time
            elem.waiting = time - elem.calc - elem.enter  # exit - calculate time - enter
        self.gant_chart.append((time, "END"))

    @staticmethod
    def _priority_add_helper(queue: List[Process], element: Process, time: int = 0):
        w1 = ((time - element.enter) + element.calc) / element.calc
        if queue:
            for index, elem in enumerate(queue):
                w2 = ((time - elem.enter) + elem.calc) / elem.calc
                if w1 > w2:
                    queue.insert(index, element)
                    return
        queue.append(element)


def read_from_file(filename: str):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File Not Found: {filename}")
    res = []
    with open(filename, 'r') as file:
        for line in file:
            name, enter, calc = line.split()
            res.append(Process(name, int(enter), int(calc)))
    return res


def write_to_file(filename: str, objects: List, *attributes):
    with open(filename, "w") as file:
        for obj in objects:
            lst = []
            for attr in attributes:
                lst.append(getattr(obj, attr))
            file.write(" ".join(str(i) for i in lst))
            file.write("\n")
