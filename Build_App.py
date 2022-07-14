import PyInstaller.__main__
import os
import shutil
from HelperFunc import writeLocalFile
from settings import appVersionNo
from platform import release, architecture

cwd = os.getcwd()
writeLocalFile(f'{cwd}/src/Commands/log.txt', '')

outputFileName = f'Pump_Handler_v{appVersionNo}-Win_{release()}-{architecture()[0]}'
PyInstaller.__main__.run([
    'Pump_Handler.py',
    f'-n{outputFileName}',
    '--onefile',
    '--windowed',
    '--add-data', 'src;src',
    '-i', ".\src\pump_icon.ico",
    '--splash', ".\src\pump_splash.png",
])

dirsToRemove = [f'{cwd}\\build', f'{cwd}\\__pycache__']
for d in dirsToRemove:
    if os.path.exists(d):
        shutil.rmtree(d)
os.remove(f'{cwd}\\{outputFileName}.spec')

os.startfile(f'{cwd}\dist')
