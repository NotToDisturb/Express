# Express development

Express is developed on Python 3.8.10 using [tesserocr](https://github.com/sirfz/tesserocr) to extract contract information from the game. Keep reading if you want an in-depth explanation of how to work on Express.

1. [Environment setup](#environment-setup)
1. [Run Express](#run-express)
1. [Build a standalone release](#building-a-standalone-release)
1. [Project structure](#project-structure)

## Environment setup
If you want to create new features, improve existing ones or fix bugs, you will need the following:
- A [Python 3.8](https://www.python.org/downloads/release/python-3810/) installation *
- [tabulate](https://github.com/gregbanks/python-tabulate) → `pip install tabulate`
- [keyboard](https://pypi.org/project/keyboard) → `pip install keyboard`
- [tesserocr for Windows, Python 3.8](https://github.com/sirfz/tesserocr#pip) (this will also install other dependencies such as [Pillow](https://github.com/python-pillow/Pillow) and [numpy](https://github.com/numpy/numpy))
    - The [`eng.traineddata`](https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata) file in the [`tessdata`](https://github.com/NotToDisturb/Express/tree/0.1/tessdata) folder
- If you want to build standalone versions, you will need [Nuitka](https://nuitka.net/doc/download.html#pypi) (which in turn needs [Visual Studio 2022](https://nuitka.net/doc/user-manual.html#id4))

\* The code should be compatible with other Python 3 versions, but you will need to download the appropriate tesserocr version

## Run Express
You can run `py express.py -h` to see information about what each accepted parameter does.

TODO: NEEDS MORE DEPTH.

## Build a standalone release
As mentioned in the [setup](#setup) section, for this you will need to install Nuitka. Installation instructions will not be provided here, intead refer to the [Nuitka site](https://nuitka.net/doc/download.html).

Once Nuitka is installed, simply run `.\build.bat` and after some time you will find the executable at `.\output\Express.exe`.

## Project structure
TODO