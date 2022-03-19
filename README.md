## Usage

```bash
# Install dependencies
pipenv install

# Run script
python Pump.py


# Compiled with Pyinstaller

# Windows
pyinstaller --onefile --windowed Pump.py
pyinstaller --onefile --windowed --add-data 'src;src' Pump.py
pyinstaller --add-data 'src;src' -i ".\src\pump_icon.ico" --onefile --windowed Pump.py
```

- Version: 1.0.0
- License: MIT
- Author: Mero2online
