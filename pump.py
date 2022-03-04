from tkinter import messagebox
from tkinter import *
import os
import sys

wellNumber = ''
allWells = ''

cwd = os.getcwd()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'src/', relative_path)


dirPuTTY = resource_path('PuTTY/').replace('/', '\\')
dirCommands = resource_path('Commands/').replace('/', '\\')


def setEntryDisabled():
    pump_one_value_entry.config(state="disabled")
    pump_two_value_entry.config(state="disabled")
    pump_three_value_entry.config(state="disabled")


def change_check_value():
    if (pump_one_checked.get() == 0):
        pump_one_value.set('')
        pump_one_value_entry.config(state="disabled")
    else:
        pump_one_value_entry.config(state="normal")
    if (pump_two_checked.get() == 0):
        pump_two_value.set('')
        pump_two_value_entry.config(state="disabled")
    else:
        pump_two_value_entry.config(state="normal")
    if (pump_three_checked.get() == 0):
        pump_three_value.set('')
        pump_three_value_entry.config(state="disabled")
    else:
        pump_three_value_entry.config(state="normal")


def getPumpsValues():
    values = []
    if pump_one_checked.get() == 1 and pump_one_value.get() != '':
        values.append(f'-dSPM1:{pump_one_value.get()} -dSTK1:1')
    if pump_two_checked.get() == 1 and pump_two_value.get() != '':
        values.append(f'-dSPM2:{pump_two_value.get()} -dSTK2:1')
    if pump_three_checked.get() == 1 and pump_three_value.get() != '':
        values.append(f'-dSPM3:{pump_three_value.get()} -dSTK3:1')
    final = ' '.join(values)
    return final


def getWellNumber():
    # checkConnection = os.system('ping 192.168.10.10 -n 1')
    # if checkConnection == 1:
    #     messagebox.showerror('Network error', 'Please connect to server first')

    path = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command0qw.txt > {dirCommands}logqw.txt \nexit'
    well = os.system(path)
    if well == 1:
        messagebox.showerror('Network error', 'Please connect to server first')

    f = open(f'{dirCommands}logqw.txt', 'r')
    logqw = f.read()
    f.close()
    start = 'Well Type   Status   UWID                Name'
    end = 'Done querying wells'
    global allWells
    allWells = logqw[logqw.find(start)+len(start):logqw.rfind(end)]
    matched_lines = [line for line in allWells.split(
        '\n') if "Logging" in line]
    global wellNumber
    wellNumber = matched_lines[0].split('    ')[0]


def saveStartCommand():
    pumpsValues = getPumpsValues()
    command = f'sh\nqw\nWWsim -W{wellNumber} {pumpsValues}\nexit\nexit\n'
    saveCommand = open(
        resource_path('Commands/command1override.txt'), "w")
    saveCommand.write(command)
    saveCommand.close()


def openOverrideCommand():
    path = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command1override.txt \nexit'
    os.system(path)


def startpump():
    if ((pump_one_checked.get() == 0 and pump_two_checked.get() == 0 and pump_three_checked.get() == 0)):
        messagebox.showerror(
            'Required Fields', 'Please check at least one pump')
        return
    if (wellNumber == ''
            or (pump_one_checked.get() == 1 and pump_one_value.get() == '')
            or (pump_two_checked.get() == 1 and pump_two_value.get() == '')
            or (pump_three_checked.get() == 1 and pump_three_value.get() == '')):
        messagebox.showerror('Required Fields', 'Please include all fields')
        return
    saveStartCommand()
    openOverrideCommand()
    print('start pump')


def stoppump():
    pathqp = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command2qp.txt > {dirCommands}logqp.txt \nexit'
    os.system(pathqp)

    f = open(f'{dirCommands}logqp.txt', 'r')
    logqp = f.read()
    f.close()

    matched_lines = [line for line in logqp.split('\n') if "DATA-SIM" in line]
    dataSimValue = matched_lines[0].split('     ')[1].split(' ')[0]

    command = f'sh\nqp\nkill -s2 {dataSimValue}\nexit\nexit\n'
    saveCommand = open(
        resource_path('Commands/command3kill.txt'), "w")
    saveCommand.write(command)
    saveCommand.close()

    pathkill = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command3kill.txt \nexit'
    os.system(pathkill)

    print('stop pump')


# Create window object
app = Tk()

getWellNumber()

# Buttons

all_wells_label = Label(app, text=allWells, pady=20)
all_wells_label.grid(row=0, column=2)

well_label = Label(app, text='Logging Well Number', pady=20, padx=20)
well_label.grid(row=1, column=0)
well_no_label = Label(app, text=wellNumber, pady=20, padx=20, width=5)
well_no_label.grid(row=1, column=1)

pump_label = Label(app, text='Pump Number', pady=20, padx=20)
pump_label.grid(row=2, column=0)
pump_one_checked = IntVar()
c1 = Checkbutton(app, text="Pump 1", variable=pump_one_checked,  pady=20, padx=20,
                 command=change_check_value)
c1.grid(row=2, column=1)
pump_two_checked = IntVar()
c2 = Checkbutton(app, text="Pump 2", variable=pump_two_checked,  pady=20, padx=20,
                 command=change_check_value)
c2.grid(row=2, column=2)
pump_three_checked = IntVar()
c3 = Checkbutton(app, text="Pump 3", variable=pump_three_checked,  pady=20, padx=20,
                 command=change_check_value)
c3.grid(row=2, column=3)

pump_value_label = Label(app, text='Pump Value', pady=20, padx=20)
pump_value_label.grid(row=3, column=0)

pump_one_value = StringVar()
pump_two_value = StringVar()
pump_three_value = StringVar()
pump_one_value_entry = Entry(app, textvariable=pump_one_value)
pump_one_value_entry.grid(row=3, column=1)
pump_two_value_entry = Entry(app, textvariable=pump_two_value)
pump_two_value_entry.grid(row=3, column=2)
pump_three_value_entry = Entry(app, textvariable=pump_three_value)
pump_three_value_entry.grid(row=3, column=3)

run_command_btn = Button(app, text='Start Pump',
                         background='#A3E4DB', command=startpump)
run_command_btn.grid(row=4, column=1, pady=20)

Button(app, text="Stop Pump",
       command=stoppump).grid(row=4, column=3, pady=20)

setEntryDisabled()

app.title('Pump')
app.geometry('800x400')
app.configure(bg='#000')

# To center all app columns
# app.grid_columnconfigure((0, 1), weight=1)

p1 = PhotoImage(file=resource_path('pump_icon.png'))

# Setting icon of master window
app.iconphoto(False, p1)

# Start program
app.mainloop()
