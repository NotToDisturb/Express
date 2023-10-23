import sys
import getopt

import modes.gui as gui
import modes.command as command
import modes.interactive as interactive

def mode_help(_: dict):
    print("[INFO] Express usage:")
    print("    express.exe (or py express.py)")
    print("                < -h | --help   >    Displays this message (optional, overrides --mode)")
    print("                < -m | --mode   >    Selects the mode under which Express will run (optional)")
    print("                                      - command:     CLI that takes all input upfront")
    print("                                      - interactive: CLI that asks the user for input as it executes (default)")
    print("                                      - gui:         A graphical interface for Express (NOT IMPLEMENTED)")
    print("                                      - help:        Displays this message")
    print("                < -p | --path   >    Path to the images (mandatory if in 'command' mode, else not used)")
    print("                < -q | --query  >    Number of the query (mandatory if in 'command' mode, else not used)")
    print("                                      1. Show packages")
    print("                                      2. Show packages per location")
    print("                                      3. Show optimal route")
    print("                < -o | --output >    Path where the results of the selected query are stored in JSON format (NOT IMPLEMENTED)")

def main(args):
    opts, _ = getopt.getopt(args,"hm:p:q:o:",["mode=","path=","query=","output="])
    options = {
        "mode" : None,
        "path": None,
        "query": None,
        "output": None
    }
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            options["mode"] = "help"
            break
        elif opt in ("-m", "--mode"):
            options["mode"] = arg
        elif opt in ("-p", "--path"):
            options["path"] = arg
        elif opt in ("-q", "--query"):
            options["query"] = arg
        elif opt in ("-o", "--output"):
            options["output"] = arg

    mode_mapper = {
        "help": mode_help,
        "command": command.execute_mode,
        "interactive": interactive.execute_mode,
        "gui": gui.execute_mode,
        None: interactive.execute_mode
    }
    mode_mapper[options["mode"]](options)

if __name__ == "__main__":
    main(sys.argv[1:])
    