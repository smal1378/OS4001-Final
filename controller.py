from database import Database
import view_text as ui
from model import read_from_file, ScheduleMother, write_to_file
from view import Panel

data = Database()
if "UI" not in data:
    ui.say_seperator()
    data["UI"] = ui.ask_options("Choose UI type", [("text mode", "TEXT")])

if data["UI"] == "TEXT":
    filename = ui.ask_string("Filename (empty for SampleTest.txt): ")
    if not filename:
        filename = 'SampleTest.txt'
    processes = read_from_file(filename)
    scheduler = ui.ask_options("Choose Your Scheduler:", [(i.name, i) for i in ScheduleMother.__subclasses__()])()
    for process in processes:
        scheduler.add_process(process)
    write_to_file("Output.txt", scheduler.get_output(), "name", "response", "waiting")
    # main menu
    while True:
        ui.say_seperator()
        op = ui.ask_options("What to do:", [('exit', None),
                                            ('show gant chart', 1),
                                            ('show output file', 2),
                                            ('switch to gui', 3)
                                            ],)
        if op is None:
            break
        elif op == 1:
            z = ui.ask_integer("Gant Zoom Scale? (1 to 50 or 'enter' for 2)")
            if not z:
                z = 2
            assert 0 < z < 51, "What did you think?"
            ui.draw_gant(scheduler.get_gant(), zoom=z)
        elif op == 2:
            ui.say("\t\t\tOutput.txt")
            ui.say("name\t\tresponse\twaiting")
            with open("Output.txt") as file:
                for line in file:
                    ui.say(*line.strip().split(), sep="\t\t\t")
        elif op == 3:
            data["UI"] = "GUI"
            break
        # the exit 'elif' will break the while then saves and exits...
if data['UI'] == "GUI":  # it's an if, because if the text-mode exits by setting 'UI' to 'GUI', it'll start
    def schedule_callback(scheduler_name: str, file_name: str):
        # file_name exists checked in gui
        scheduler1 = schedulers_list[schedulers_name.index(scheduler_name)]()
        processes1 = read_from_file(file_name)
        for pro in processes1:
            scheduler1.add_process(pro)
        return scheduler1.get_output(), scheduler1.get_gant()
    schedulers_list = ScheduleMother.__subclasses__()
    schedulers_name = [x.name for x in ScheduleMother.__subclasses__()]
    win = Panel(
        schedule_callback,
        schedulers_name
    )
    win.mainloop()

data.flush()
