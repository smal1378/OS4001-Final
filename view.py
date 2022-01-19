# view.py - tkinter GUI
import os.path
from tkinter import Tk as _Tk, Label as _Label, Button as _Button, Frame as _Frame,\
    LabelFrame as _LabelFrame, StringVar as _StringVar, Entry as _Entry, Canvas as _Canvas
from tkinter.ttk import Treeview as _Treeview, Combobox as _Combobox
from typing import List, Callable, Tuple
from model import Process
from database import Database

FONT = ("Times New Roman", 16)


class Panel(_Tk):
    def __init__(self, schedule_callback: Callable[[str, str], Tuple[List[Process], List[Tuple[int, str]]]],
                 schedulers: List[str]):
        super(Panel, self).__init__()
        self.schedule_callback = schedule_callback
        self.title("OS4001 Project - Mahjoor & Eslami")
        self.geometry("1100x600")
        self.config(bg="white")
        mother = _Frame(self, bd=1, relief="solid", bg="white")
        mother.grid(row=1, column=1, padx=5, pady=5)
        up = _Frame(mother, bg="white")
        up.grid(row=1, column=1, sticky="w")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        inp = _LabelFrame(up, text="Input File", font=FONT, bg="white")
        inp.grid(row=1, column=2, padx=5, pady=5, sticky='wne')
        _Label(inp, text="File Name:", font=FONT, bg="white").grid(row=1, column=1)
        self.string_var_input_filename = _StringVar(self, value="SampleTest.txt")
        ent_filename = _Entry(inp, textvariable=self.string_var_input_filename, font=FONT)
        ent_filename.grid(row=1, column=2, pady=5, padx=5)
        ent_filename.bind("<KeyRelease>", self.validate_filename)  # Change Field Color Whether File Exists
        _Button(inp, text="Load", font=FONT, bg="white", command=self.load_inp).grid(row=2, column=2, pady=5,
                                                                                     padx=5, sticky="e")
        _Label(inp, text="Scheduler:", font=FONT, bg="white").grid(row=2, column=1, pady=5)
        self.scheduler_combo = _Combobox(inp, font=FONT, state='readonly', values=schedulers, width=10)
        self.scheduler_combo.grid(row=2, column=2, padx=5, sticky='w')
        self.scheduler_combo.set(schedulers[0])
        tr = _LabelFrame(up, text="Processes", font=FONT, bg="white")
        tr.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.tree = _Treeview(tr, columns=("Name", "Enter", "Calc", "Wait", "Response"),
                              show="headings", selectmode="none")
        self.tree.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        tree = self.tree
        tree.heading('Name', text="Name", anchor="w")
        tree.column("Name", width=100)
        tree.heading('Enter', text="Enter", anchor="w")
        tree.column("Enter", width=75)
        tree.heading('Calc', text="Calc", anchor="w")
        tree.column("Calc", width=75)
        tree.heading('Wait', text="Wait", anchor="w")
        tree.column("Wait", width=75)
        tree.heading('Response', text="Response", anchor="w")
        tree.column("Response", width=75)
        gant_frame = _LabelFrame(mother, text="Gant Chart", bg="white")
        gant_frame.grid(row=2, column=1, padx=5, pady=5)
        self.canvas = _Canvas(gant_frame, width=1000, height=50, bg="white")
        self.canvas.grid(row=1, column=1, padx=5, pady=5)
        _Button(mother, text="text-mode", command=self.exit_to_text,
                bg="white", relief="solid", bd=1).grid(row=3, column=1, padx=5, sticky="e")

    def exit_to_text(self):
        d = Database()
        d["UI"] = "TEXT"
        d.flush()
        self.destroy()

    def load_inp(self):
        self.tree.delete(*self.tree.get_children(""))
        filename = self.string_var_input_filename.get()
        if os.path.exists(filename):
            processes, gant_data = self.schedule_callback(self.scheduler_combo.get(), filename)
            for process in processes:
                self.tree.insert("", "end", values=(process.name,
                                                    process.enter,
                                                    process.calc,
                                                    process.waiting,
                                                    process.response))

                self.canvas.delete("all")
                self.canvas.create_rectangle(2, 2, 1000, 30, fill="#efefef")
                maxi = gant_data[-1][0]  # is the maximum
                for start, name in gant_data:
                    scale = int((start / maxi) * 1000)
                    self.canvas.create_line(scale, 2, scale, 30)
                    if name != "END":
                        self.canvas.create_text(scale, 30, text=name)

    @staticmethod
    def validate_filename(e):
        widget = e.widget
        if os.path.exists(widget.get()):
            widget.config(background="#afa")
        else:
            widget.config(background="#faa")
