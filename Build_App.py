import PyInstaller.__main__

PyInstaller.__main__.run([
    'Pump_Handler.py',
    '--onefile',
    '--windowed',
    '--add-data', 'src;src',
    '-i', ".\src\pump_icon.ico",
    '--splash', ".\src\pump_splash.png",
])
