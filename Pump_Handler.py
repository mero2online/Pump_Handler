from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import *
import os
import shutil
import keyboard as kb
import win32api
import threading
import paramiko
from paramiko_expect import SSHClientInteraction

from HelperFunc import *
from settings import appVersionNo
try:
    import pyi_splash  # type: ignore
    pyi_splash.close()
except:
    pass

cwd = os.getcwd()

dirPuTTY = resource_path('PuTTY/').replace('/', '\\')
dirCommands = resource_path('Commands/').replace('/', '\\')


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


def getSTK_Value(pumpValue):
    if int(pumpValue) == 0:
        return '0'
    elif int(pumpValue) > 60:
        return f'{"{:.2f}".format(int(pumpValue)/60)}'
    else:
        return '1'


def getPumpsValues():
    values = []
    p_one_v = pump_one_value.get()
    p_two_v = pump_two_value.get()
    p_thr_v = pump_thr_value.get()

    if pump_one_checked.get() == 1 and p_one_v != '':
        stk1 = getSTK_Value(p_one_v)
        values.append(f'-dSPM1:{p_one_v} -dSTK1:{stk1}')

    if pump_two_checked.get() == 1 and p_two_v != '':
        stk2 = getSTK_Value(p_two_v)
        values.append(f'-dSPM2:{p_two_v} -dSTK2:{stk2}')

    if pump_thr_checked.get() == 1 and p_thr_v != '':
        stk3 = getSTK_Value(p_thr_v)
        values.append(f'-dSPM3:{p_thr_v} -dSTK3:{stk3}')

    final = ' '.join(values)
    return final


def openPuTTY():
    sessionCommand = f'powershell reg import {dirPuTTY}putty-sessions.reg'
    os.system(sessionCommand)
    tempPath = os.environ['TEMP']
    local_PuTTY_path = f'{tempPath}\\PuTTY'
    src_files = os.listdir(resource_path('PuTTY'))
    if os.path.exists(local_PuTTY_path) == False:
        os.mkdir(local_PuTTY_path)
        # shutil.rmtree(local_PuTTY_path)
    for file_name in src_files:
        if os.path.isfile(resource_path(f'PuTTY\\{file_name}')):
            shutil.copy(resource_path(f'PuTTY\\{file_name}'), local_PuTTY_path)

    win32api.LoadKeyboardLayout('00000409', 1)  # to switch to english
    path = f'start {local_PuTTY_path}\\putty.exe -load "Server" -l root -pw WeatherfordSLS'
    os.system(path)
    app.after(1000, print('OK'))
    kb.write('sh')
    kb.press('enter')


def connectSSHClient():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    HOSTNAME = '192.168.10.10'
    USERNAME = 'root'
    PASSWORD = 'WeatherfordSLS'
    try:
        client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
        app.update()
        return client
    except Exception as err:
        return [err]


def getWellNumber():
    client = connectSSHClient()
    if type(client) == list:
        messagebox.showerror('Network error', client[0])
        app.destroy()
        return
    with SSHClientInteraction(client, timeout=10, display=True) as interact:
        interact.send('sh')
        interact.send('qw')
        interact.send('exit')
        interact.send('exit')
        interact.expect('', timeout=1, lines_to_check=2)
        cmd_output = interact.current_output
        writeLocalFile(f'{dirCommands}log.txt', cmd_output)
    interact.close()
    client.close()

    log = readLocalFile(f'{dirCommands}log.txt')
    if len(log.splitlines()) == 0:
        messagebox.showerror('Network error', 'Please connect to server first')
        wellNumber.set('0')
    else:
        start = 'Well Type   Status   UWID                Name\n'
        end = 'Done querying wells'
        global listAllWells
        allWells = log[log.find(start)+len(start):log.rfind(end)]
        listAllWells = allWells.splitlines()
        for i, w in enumerate(listAllWells):
            splitted = w.split()
            if splitted[2] == 'Logging':
                wellNumber.set(splitted[0])
                wellIndex.set(i)
                wellName.set(splitted[4])

    populate_wells_list()
    wells_list.selection_set(wellIndex.get())
    wells_list.yview_scroll(wellIndex.get(), 'units')


def populate_wells_list():
    for idx, well in enumerate(listAllWells):
        wells_list.insert(END, f' {well}')


def openOverrideCommand():
    pumpsValues = getPumpsValues()
    client = connectSSHClient()
    interact = SSHClientInteraction(client, timeout=10, display=True)
    interact.send('sh')
    interact.send(f'WWsim -W{wellNumber.get()} {pumpsValues}')
    interact.send('exit')
    interact.send('exit')
    interact.expect('', timeout=1, lines_to_check=2)
    cmd_output = interact.current_output
    writeLocalFile(f'{dirCommands}log.txt', cmd_output)
    interact.close()
    client.close()


def startPump():
    if ((pump_one_checked.get() == 0 and pump_two_checked.get() == 0 and pump_thr_checked.get() == 0)):
        messagebox.showerror(
            'Required Fields', 'Please check at least one pump')
        return
    if (wellNumber.get() == ''
            or (pump_one_checked.get() == 1 and pump_one_value.get() == '')
            or (pump_two_checked.get() == 1 and pump_two_value.get() == '')
            or (pump_thr_checked.get() == 1 and pump_thr_value.get() == '')):
        messagebox.showerror('Required Fields', 'Please include all fields')
        return

    setButtonsDisabled()
    checkDataSim()
    if len(dataSim_matched) > 0:
        dataSimValue = dataSim_matched[0].split('     ')[1].split(' ')[0]
        messagebox.showerror(
            'Error', f'Please Stop DATA-SIM {dataSimValue} first')
        return

    setButtonsDisabled()
    startProgressBar()
    openOverrideCommand()
    setButtonsNormal()
    print('start pump')


def checkDataSim():
    p.stop()
    clearFiles()
    client = connectSSHClient()
    interact = SSHClientInteraction(client, timeout=10, display=True)
    interact.send('sh')
    interact.send('qp')
    interact.send('exit')
    interact.send('exit')
    interact.expect('', timeout=1, lines_to_check=2)
    cmd_output = interact.current_output
    writeLocalFile(f'{dirCommands}log.txt', cmd_output)
    interact.close()
    client.close()

    log = readLocalFile(f'{dirCommands}log.txt')

    global dataSim_matched
    dataSim_matched = [line for line in log.split('\n') if "DATA-SIM" in line]
    setButtonsNormal()


def openKillCommand():
    startProgressBar()
    dataSimValue = dataSim_matched[0].split('     ')[1].split(' ')[0]

    client = connectSSHClient()
    interact = SSHClientInteraction(client, timeout=10, display=True)
    interact.send('sh')
    interact.send(f'kill -s2 {dataSimValue}')
    interact.send('exit')
    interact.send('exit')
    interact.expect('', timeout=1, lines_to_check=2)
    cmd_output = interact.current_output
    writeLocalFile(f'{dirCommands}log.txt', cmd_output)
    interact.close()
    client.close()

    setButtonsNormal()


def stopPump():
    setButtonsDisabled()
    checkDataSim()
    if len(dataSim_matched) == 0:
        messagebox.showerror('Error', 'No DATA-SIM started yet')
        return

    openKillCommand()
    print('stop pump')


def limitInputPump(i, var):
    value = var.get()
    if len(value) > 3:
        var.set(value[:3])
    if value != '' and int(value) > 200:
        messagebox.showerror(
            'Error', f'Pump {i+1} value {value} exceed value limit')
        var.set(value[:2])


def clearFiles():
    writeLocalFile(resource_path('Commands/log.txt'), '')


def stepVa(idx):
    stepVal = 1 if idx == 3 else 50
    p.step(stepVal)


def startProgressBar():
    p.stop()
    for idx, i in enumerate(range(1, 3, 1)):
        threading.Timer(i, lambda id=idx: stepVa(id)).start()
        app.update()


def showWaitLabel():
    wait_label.place(x=380, y=350, width=25, height=25)


def hideWaitLabel():
    wait_label.place(x=0, y=0, width=0, height=0)


def setEntryDisabled():
    pump_one_value_entry.config(state="disabled")
    pump_two_value_entry.config(state="disabled")
    pump_thr_value_entry.config(state="disabled")


def setButtonsDisabled():
    start_pump_btn.config(state='disabled')
    stop_pump_btn.config(state='disabled')
    openPuTTY_btn.config(state='disabled')


def setButtonsNormal():
    start_pump_btn.config(state='normal')
    stop_pump_btn.config(state='normal')
    openPuTTY_btn.config(state='normal')


# Create window object
app = Tk()

waitSec = IntVar()

clearFiles()

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
scrollbar.place(x=567, y=21, height=80)
# Set scroll to listbox
wells_list.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=wells_list.yview)
# Bind select
wells_list.bind('<<ListboxSelect>>')

labels = ['Logging Well Number', 'Pump Number', 'Pump Value']

for i, v in enumerate(labels):
    label = Label(app, text=v, background='#10b6a8', pady=20, padx=20)
    xPlace = 20
    yPlace = (i*65)+120
    label.place(x=xPlace, y=yPlace, width=140, height=50)

global wellNumber, wellIndex, wellName
wellNumber = StringVar()
wellIndex = IntVar()
wellName = StringVar()
well_no_label = Label(app, textvariable=wellNumber,
                      background='#5B7DB1', font=('Arial', 15, 'bold'), pady=20, padx=20)
well_no_label.place(x=180, y=120, width=100, height=50)

# Buttons
pumpsBtnVars = []
for i in range(3):
    var = IntVar()
    pumpsBtnVars.append(var)
    chkBtn = Checkbutton(app, text=f"Pump {i+1}", variable=var, background='#5B7DB1',
                         pady=20, padx=20, borderwidth=2, relief="ridge", font=('Arial', 10, 'bold'),
                         command=change_check_value)
    xPlace = (i*120)+180
    yPlace = 185
    chkBtn.place(x=xPlace, y=yPlace, width=90, height=50)

pump_one_checked, pump_two_checked, pump_thr_checked = pumpsBtnVars

pumpsVars = []
pumpsEntry = []
for i in range(3):
    var = StringVar()
    var.trace('w', lambda var, index, mode,
              idx=i, varia=var: limitInputPump(idx, varia))
    pumpsVars.append(var)
    entry = Entry(app, textvariable=var, background='#5B7DB1',
                  borderwidth=2, relief="ridge", font=('Arial', 15, 'bold'))
    xPlace = (i*120)+180
    yPlace = 250
    entry.place(x=xPlace, y=yPlace, width=90, height=50)
    pumpsEntry.append(entry)

pump_one_value, pump_two_value, pump_thr_value = pumpsVars
pump_one_value_entry, pump_two_value_entry, pump_thr_value_entry = pumpsEntry

start_pump_btn = Button(app, text='Start Pump',
                        background='#A3E4DB', command=startPump)
start_pump_btn.place(x=50, y=310, width=90, height=30)

stop_pump_btn = Button(app, text="Stop Pump",
                       background='#e00707', command=stopPump)
stop_pump_btn.place(x=50, y=345, width=90, height=30)

p = Progressbar(app, orient=HORIZONTAL, length=101,
                mode="determinate", takefocus=True, maximum=101)
p.place(x=200, y=385, width=300, height=15)

wait_label = Label(app, textvariable=waitSec,
                   background='#5B7DB1', font=('Arial', 15, 'bold'), pady=20, padx=20, width=5)

madeWithLoveBy = Label(
    app, text='Made with ❤ by Mohamed Omar', background='#10b6a8', foreground='#000000',
    font=('monospace', 9, 'bold'))
madeWithLoveBy.place(x=0, y=380, width=190, height=20)

versionNo = Label(
    app, text=f'v.{appVersionNo}', background='#10b6a8', foreground='#000000',
    font=('monospace', 9, 'bold'))
versionNo.place(x=540, y=380, width=60, height=20)

icon = PhotoImage(file=resource_path('PuTTY_icon.png'))
openPuTTY_btn = Button(app, text="PuTTY", image=icon,
                       background='#fff', command=openPuTTY)
openPuTTY_btn.place(x=540, y=320, width=40, height=37)

app.title(f'Pump_Handler {appVersionNo}')
app.geometry('600x400')
app.configure(bg='#000')
app.resizable(False, False)

# To center all app columns
# app.grid_columnconfigure((0, 1), weight=1)

p1 = PhotoImage(file=resource_path('pump_icon.png'))

# Setting icon of master window
app.iconphoto(False, p1)

getWellNumber()

# Start program
app.mainloop()
