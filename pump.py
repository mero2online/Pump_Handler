from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import os
import sys

cwd = os.getcwd()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'src/', relative_path)


def saveStartCommand():
    command = f'sh\nqw\nWWsim -W{well_number.get()} -dSPM{pump_number.get()}:{pump_value.get()}\nexit\nexit\n'
    saveCommand = open(
        resource_path('PuTTY/command1override.txt'), "w")
    saveCommand.write(command)
    saveCommand.close()


def openOverrideCommand():
    directory = resource_path('PuTTY/').replace('/', '\\')
    path = f'{directory}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {directory}command1override.txt \nexit'
    os.system(path)


def startpump():
    if well_number.get() == '' or pump_number.get() == '' or pump_value.get() == '':
        messagebox.showerror('Required Fields', 'Please include all fields')
        return
    saveStartCommand()
    openOverrideCommand()
    print('start pump')


def stoppump():
    directory = resource_path('PuTTY/').replace('/', '\\')
    pathqp = f'{directory}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {directory}command2qp.txt > {directory}logqp.txt \nexit'
    os.system(pathqp)

    f = open(f'{directory}logqp.txt', 'r')
    logqp = f.read()
    f.close()

    matched_lines = [line for line in logqp.split('\n') if "DATA-SIM" in line]
    dataSimValue = matched_lines[0].split('     ')[1].split(' ')[0]

    command = f'sh\nqp\nkill -s2 {dataSimValue}\nexit\nexit\n'
    saveCommand = open(
        resource_path('PuTTY/command3kill.txt'), "w")
    saveCommand.write(command)
    saveCommand.close()

    pathkill = f'{directory}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {directory}command3kill.txt \nexit'
    os.system(pathkill)

    print('stop pump')


# Create window object
app = Tk()

# Buttons

well_number = StringVar()
well_label = Label(app, text='Well Number', pady=20)
well_label.grid(row=0, column=0)
well_entry = Entry(app, textvariable=well_number)
well_entry.grid(row=0, column=1)

pump_number = StringVar()
pump_label = Label(app, text='Pump Number', pady=20)
pump_label.grid(row=0, column=2)
pump_entry = Entry(app, textvariable=pump_number)
pump_entry.grid(row=0, column=3)

pump_value = StringVar()
pump_value_label = Label(app, text='Pump Value', pady=20)
pump_value_label.grid(row=0, column=4)
pump_value_entry = Entry(app, textvariable=pump_value)
pump_value_entry.grid(row=0, column=5)

run_command_btn = Button(app, text='Start Pump',
                         background='#A3E4DB', command=startpump)
run_command_btn.grid(row=2, pady=20)

Button(app, text="Stop Pump",
       command=stoppump).grid(row=3, column=0, pady=5)

app.title('Pump')
app.geometry('900x400')
app.configure(bg='#000')

# To center all app columns
app.grid_columnconfigure((0, 1), weight=1)

p1 = PhotoImage(file=resource_path('pump_icon.png'))

# Setting icon of master window
app.iconphoto(False, p1)

# Start program
app.mainloop()
