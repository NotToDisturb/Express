# Express development

Express is developed on Python 3.8.10 using [tesserocr](https://github.com/sirfz/tesserocr) to extract contract information from the game. If you want to create new features, improve existing ones or fix bugs, you will need the following:
- A [Python](https://www.python.org/downloads/release/python-3810/) installation
- [tesserocr for Windows](https://github.com/sirfz/tesserocr#pip) (this will also install the other depenecy, [PIL](https://pypi.org/project/Pillow/))
    - The [`eng.traineddata`](https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata) file in the [`tessdata`](https://github.com/NotToDisturb/Express/tree/0.1/tessdata) folder
- If you want to build standalone versions, you will need [Nuitka](https://nuitka.net/doc/download.html#pypi) (which in turn needs [Visual Studio 2022](https://nuitka.net/doc/user-manual.html#id4))

## Running using Python
You can run `py express.py -h` to see information about what each accepted parameter does.

## Building a standalone version
Simply run `.\build.bat` and after some time you will find the executable at `.\output\Express.exe`.