## Usage

```bash
# Install dependencies
pipenv install

# Run script
python pump.py


# Compiled with Pyinstaller

# Windows
pyinstaller --onefile --windowed pump.py
pyinstaller --onefile --windowed --add-data 'src;src' pump.py
pyinstaller --add-data 'src;src' -i ".\src\pump_icon.ico" --onefile --windowed pump.py
```

- Version: 1.0.0
- License: MIT
- Author: Brad Traversy
