# Text mode view
from typing import Optional, List, Any, Tuple
import io
from contextlib import redirect_stdout
MAX_CHAR = 50  # maximum characters to print in one line


def _insert_break_line(inp: str, interval: int = None,
                       start_line: str = "", end_line: str = "\\") -> str:
    if not interval:
        interval = MAX_CHAR
    res = f"{start_line}"
    a = 0
    while a < len(inp):
        if a + interval > len(inp):
            end_line = ""
        res += inp[a:a+interval] + f"{end_line}\n{start_line}"
        a += interval
    res += inp[a:]
    return res.strip()


def ask_string(message: str):
    message = _insert_break_line(message)
    return input(message)


def ask_integer(message: str) -> Optional[int]:
    message = _insert_break_line(message)
    inp = input(message)
    if not inp:
        return None
    while inp.isnumeric():
        print("Enter Integer Please, Or empty for cancel")
        inp = input(message)
        if not inp:
            return None
    return int(inp)


def ask_options(message: str, options: List[Tuple[str, Any]]):
    def name_generator():
        a = 1
        for name1 in names:
            yield f"{a}.{name1}"
            a += 1

    message = _insert_break_line(message)
    print(message)
    print("Options:")
    values = []
    names = []
    for name, value in options:
        values.append(value)
        names.append(name)
    res = " - ".join(name_generator())
    print(_insert_break_line(res, start_line="\t"))
    while True:
        inp = input("Name Or Number Of Your Option:")
        if not inp:
            return None
        if inp.isnumeric():
            inp = int(inp)
            if 1 <= inp <= len(names):
                return values[inp-1]
        elif inp in names:
            return values[names.index(inp)]
        print("Didn't Match!")


def say(*args, **kwargs):
    f = io.StringIO()
    with redirect_stdout(f):
        print(*args, **kwargs)
    out = f.getvalue()
    _insert_break_line(out)
    print(out, end="")


def say_seperator():
    print("-" * MAX_CHAR)


def draw_gant(datas: List[Tuple[int, str]], zoom: int = 1):
    last_one = 0
    for time, name in datas:
        print("|\t\t|\n" * (((time - last_one) // zoom) - 1), end="")
        print("|\t\t|", f"  T: {time}, P: {name}")


def say_warning(message: str):
    say_seperator()
    say("\t\tWARNING")
    say(message)
    say_seperator()


def wait_for_enter(before: str = '\n'):
    ask_string(f"{before}Waiting to press 'ENTER'..")
