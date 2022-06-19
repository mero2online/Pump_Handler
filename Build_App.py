import PyInstaller.__main__
import os
from settings import appVersionNo
from platform import release, architecture

cwd = os.getcwd()

PyInstaller.__main__.run([
    'Pump_Handler.py',
    f'-n Pump_Handler_v{appVersionNo}-Win_{release()}-{architecture()[0]}',
    '--onefile',
    '--windowed',
    '--add-data', 'src;src',
    '-i', ".\src\pump_icon.ico",
    '--splash', ".\src\pump_splash.png",
])

os.chdir(f'{cwd}\dist')  # Change directory to run command
os.system('start.')  # Run command
