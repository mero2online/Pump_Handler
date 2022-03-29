from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import *
import os
from HelperFunc import *

wellNumber = ''
allWells = ''

cwd = os.getcwd()

dirPuTTY = resource_path('PuTTY/').replace('/', '\\')
dirCommands = resource_path('Commands/').replace('/', '\\')


def setEntryDisabled():
    pump_one_value_entry.config(state="disabled")
    pump_two_value_entry.config(state="disabled")
    pump_thr_value_entry.config(state="disabled")


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
    if (pump_thr_checked.get() == 0):
        pump_thr_value.set('')
        pump_thr_value_entry.config(state="disabled")
    else:
        pump_thr_value_entry.config(state="normal")


def getPumpsValues():
    values = []
    p_one_v = pump_one_value.get()
    p_two_v = pump_two_value.get()
    p_thr_v = pump_thr_value.get()

    if pump_one_checked.get() == 1 and p_one_v != '':
        stk1 = f'{"{:.2f}".format(int(p_one_v)/60)}' if int(p_one_v) > 60 else '1'
        values.append(f'-dSPM1:{p_one_v} -dSTK1:{stk1}')

    if pump_two_checked.get() == 1 and p_two_v != '':
        stk2 = f'{"{:.2f}".format(int(p_two_v)/60)}' if int(p_two_v) > 60 else '1'
        values.append(f'-dSPM2:{p_two_v} -dSTK2:{stk2}')

    if pump_thr_checked.get() == 1 and p_thr_v != '':
        stk3 = f'{"{:.2f}".format(int(p_thr_v)/60)}' if int(p_thr_v) > 60 else '1'
        values.append(f'-dSPM3:{p_thr_v} -dSTK3:{stk3}')

    final = ' '.join(values)
    return final


def getWellNumber():
    # checkConnection = os.system('ping 192.168.10.10 -n 1')
    # if checkConnection == 1:
    #     messagebox.showerror('Network error', 'Please connect to server first')

    path = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command0qw.txt > {dirCommands}log.txt \nexit'
    well = os.system(path)
    if well == 1:
        messagebox.showerror('Network error', 'Please connect to server first')

    log = readLocalFile(f'{dirCommands}log.txt')

    start = 'Well Type   Status   UWID                Name'
    end = 'Done querying wells'
    global allWells
    allWells = log[log.find(start)+len(start):log.rfind(end)]
    matched_lines = [line for line in allWells.split(
        '\n') if "Logging" in line]
    global wellNumber
    wellNumber = matched_lines[0].split('    ')[0]


def populate_wells_list():
    splitWells = allWells.split('\n')
    wellByWell = splitWells[1:len(splitWells)-1]
    for idx, well in enumerate(wellByWell):
        wells_list.insert(END, f' {well}')


def saveStartCommand():
    pumpsValues = getPumpsValues()
    command = f'sh\nWWsim -W{wellNumber} {pumpsValues}\nexit\nexit\n'
    writeLocalFile(resource_path('Commands/command1override.txt'), command)


def openOverrideCommand():
    path = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command1override.txt > {dirCommands}log.txt \nexit'
    os.system(path)
    start_pump_btn.config(state='normal')
    stop_pump_btn.config(state='normal')


def startpump():
    if ((pump_one_checked.get() == 0 and pump_two_checked.get() == 0 and pump_thr_checked.get() == 0)):
        messagebox.showerror(
            'Required Fields', 'Please check at least one pump')
        return
    if (wellNumber == ''
            or (pump_one_checked.get() == 1 and pump_one_value.get() == '')
            or (pump_two_checked.get() == 1 and pump_two_value.get() == '')
            or (pump_thr_checked.get() == 1 and pump_thr_value.get() == '')):
        messagebox.showerror('Required Fields', 'Please include all fields')
        return

    matched_lines = checkDataSim()
    if len(matched_lines) > 0:
        dataSimValue = matched_lines[0].split('     ')[1].split(' ')[0]
        messagebox.showerror(
            'Error', f'Please Stop DATA-SIM {dataSimValue} first')
        return

    saveStartCommand()
    start_pump_btn.config(state='disabled')
    stop_pump_btn.config(state='disabled')
    app.after(5000, openOverrideCommand)
    startProgressBar()
    print('start pump')


def checkDataSim():
    pathqp = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command2qp.txt > {dirCommands}log.txt \nexit'
    os.system(pathqp)

    log = readLocalFile(f'{dirCommands}log.txt')

    matched_lines = [line for line in log.split('\n') if "DATA-SIM" in line]

    return matched_lines


def openKillCommand():
    pathkill = f'{dirPuTTY}plink.exe root@192.168.10.10 -pw WeatherfordSLS < {dirCommands}command3kill.txt > {dirCommands}log.txt \nexit'
    os.system(pathkill)
    start_pump_btn.config(state='normal')
    stop_pump_btn.config(state='normal')


def stoppump():
    matched_lines = checkDataSim()
    if len(matched_lines) == 0:
        messagebox.showerror('Error', 'No DATA-SIM started yet')
        return

    dataSimValue = matched_lines[0].split('     ')[1].split(' ')[0]

    command = f'sh\nkill -s2 {dataSimValue}\nexit\nexit\n'
    writeLocalFile(resource_path('Commands/command3kill.txt'), command)
    start_pump_btn.config(state='disabled')
    stop_pump_btn.config(state='disabled')
    app.after(5000, openKillCommand)
    startProgressBar()
    print('stop pump')


def limitInputPumpOne(var, index, mode):
    value = pump_one_value.get()
    if len(value) > 3:
        pump_one_value.set(value[:3])


def limitInputPumpTwo(var, index, mode):
    value = pump_two_value.get()
    if len(value) > 3:
        pump_two_value.set(value[:3])


def limitInputPumpThr(var, index, mode):
    value = pump_thr_value.get()
    if len(value) > 3:
        pump_thr_value.set(value[:3])


def clearFiles():
    writeLocalFile(resource_path('Commands/command1override.txt'), '')
    writeLocalFile(resource_path('Commands/command3kill.txt'), '')
    writeLocalFile(resource_path('Commands/log.txt'), '')


def startProgressBar():
    for idx, i in enumerate(range(1, 7, 1)):
        if idx == 5:
            stepVal = 1
        else:
            stepVal = 20

        app.after(1000, p.step(stepVal))
        app.update()


# Create window object
app = Tk()

clearFiles()
getWellNumber()

canvas = Canvas(app, bg="#4392F1", height=400, width=800,
                bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)
background_img = PhotoImage(file=resource_path('background.png'))
background = canvas.create_image(400.0, 200.0, image=background_img)

# Wells List (Listbox)
wells_list = Listbox(app, height=4, width=90, border=0, background='#5B7DB1',
                     selectforeground='#1A132F', selectbackground='#10b6a8',
                     selectborderwidth=2, activestyle='none')
wells_list.grid(row=0, column=0, columnspan=5, rowspan=1, pady=20, padx=20)
# Create scrollbar
scrollbar = Scrollbar(app)
scrollbar.grid(row=0, column=4)
# Set scroll to listbox
wells_list.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=wells_list.yview)
# Bind select
wells_list.bind('<<ListboxSelect>>')

well_label = Label(app, text='Logging Well Number',
                   background='#10b6a8', pady=20, padx=20)
well_label.grid(row=1, column=0)
well_no_label = Label(app, text=wellNumber,
                      background='#5B7DB1', font=('Arial', 15, 'bold'), pady=20, padx=20, width=5)
well_no_label.grid(row=1, column=1)

# Buttons
pump_label = Label(app, text='Pump Number',
                   background='#10b6a8', pady=20, padx=20)
pump_label.grid(row=2, column=0)
pump_one_checked = IntVar()
c1 = Checkbutton(app, text="Pump 1", variable=pump_one_checked, background='#e938bd', pady=20, padx=20, borderwidth=2, relief="ridge",
                 command=change_check_value)
c1.grid(row=2, column=1)
pump_two_checked = IntVar()
c2 = Checkbutton(app, text="Pump 2", variable=pump_two_checked, background='#b6108d', pady=20, padx=20, borderwidth=2, relief="ridge",
                 command=change_check_value)
c2.grid(row=2, column=2)
pump_thr_checked = IntVar()
c3 = Checkbutton(app, text="Pump 3", variable=pump_thr_checked, background='#e938bd', pady=20, padx=20, borderwidth=2, relief="ridge",
                 command=change_check_value)
c3.grid(row=2, column=3)

pump_value_label = Label(app, text='Pump Value',
                         background='#10b6a8', pady=20, padx=20)
pump_value_label.grid(row=3, column=0)

pump_one_value = StringVar()
pump_two_value = StringVar()
pump_thr_value = StringVar()

pump_one_value.trace('w', limitInputPumpOne)
pump_two_value.trace('w', limitInputPumpTwo)
pump_thr_value.trace('w', limitInputPumpThr)

pump_one_value_entry = Entry(app, textvariable=pump_one_value,
                             background='#e938bd', borderwidth=2, relief="ridge")
pump_one_value_entry.grid(row=3, column=1)
pump_two_value_entry = Entry(app, textvariable=pump_two_value,
                             background='#b6108d', borderwidth=2, relief="ridge")
pump_two_value_entry.grid(row=3, column=2)
pump_thr_value_entry = Entry(
    app, textvariable=pump_thr_value, background='#e938bd', borderwidth=2, relief="ridge")
pump_thr_value_entry.grid(row=3, column=3)

start_pump_btn = Button(app, text='Start Pump',
                        background='#A3E4DB', command=startpump)
start_pump_btn.grid(row=4, column=1, pady=5)

stop_pump_btn = Button(app, text="Stop Pump", background='#e00707',
                       command=stoppump)
stop_pump_btn.grid(row=5, column=1, pady=5)

p = Progressbar(app, orient=HORIZONTAL, length=101,
                mode="determinate", takefocus=True, maximum=101)
p.place(x=200, y=385, width=300, height=15)

populate_wells_list()
setEntryDisabled()

app.title('Pump')
app.geometry('600x400')
app.configure(bg='#000')
app.resizable(False, False)

# To center all app columns
# app.grid_columnconfigure((0, 1), weight=1)

p1 = PhotoImage(file=resource_path('pump_icon.png'))

# Setting icon of master window
app.iconphoto(False, p1)

wells_list.selection_set(int(wellNumber)-1)
wells_list.yview_scroll(int(wellNumber)-2, 'units')

# Start program
app.mainloop()
