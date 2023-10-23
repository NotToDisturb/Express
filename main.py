import os
import keyboard
from PIL import Image, ImageGrab
from parsing import DeliveryParser
from graph import DeliveryVerse

PICK_UP_STRING = "PICK UP"
DROP_OFF_STRING = "DROP OFF"
PACKAGE_STRING = "Package"
TO_STRING = " to "
FROM_STRING = " from "
ON_STRING = " on "
ID_LENGTH = 6
INFINITY = float("inf")

def input_images_from_screenshots():
    images = []
    print("[INFO] Taking screenshots")
    print("    ENTER to screenshot")
    print("    SPACE to continue")
    taking = True
    while taking:
        if keyboard.is_pressed("enter"):
            print("    Took screenshot")
            images.append(ImageGrab.grab())
        elif keyboard.is_pressed("space"):
            taking = False
    return images

def input_images_from_storage():
    images = []
    path = input("[INPUT] Enter a folder path: ")
    while not os.path.exists(path):
        path = input("[INPUT] Path does not exist, enter a folder path:")
    for file in os.listdir(path):
        images.append(Image.open(f"{path}/{file}"))
    return images

def input_functions_deliveries_per_location(verse):
    print("\n[INFO] Detected deliveries:") 
    for location in verse.locations.values():
        if len(location.pickup_packages) == 0 and len(location.dropoff_packages) == 0:
            continue
        print(f"{location.location}")
        print(f" - Pickup: {', '.join([package.package for package in location.pickup_packages])}")
        print(f" - Dropoff: {', '.join([package.package for package in location.dropoff_packages])}")

def input_functions_deliveries_per_package(verse):
    for package in verse.packages.values():
        print(package)

def input_functions_optimal_route(verse):
    verse.build_graph()
    route = verse.get_shortest_route()
    print("\n[INFO] Optimal route is:")
    for step in route:
        print(f"    {step.location}: {step}")

def input_functions_exit(verse):
    exit()

def input_images_select():
    input_images = {
        "1": input_images_from_screenshots,
        "2": input_images_from_storage
    }
    print("[INPUT] What images do you want to use?")
    print("    1. Take screenshots")
    print("    2. Images on a folder")
    selection = input("    Enter a number: ")
    return input_images[selection]()

def input_functions_options():
    print("    1. Deliveries per location")
    print("    2. Deliveries per package")
    print("    3. Optimal path")
    print("    4. Exit")

def input_functions_select(verse):
    input_functions = {
        "1": input_functions_deliveries_per_location,
        "2": input_functions_deliveries_per_package,
        "3": input_functions_optimal_route,
        "4": input_functions_exit
    }
    print("[INPUT] What query would you like to make?")
    input_functions_options()
    selection = input("    Enter a number: ")
    input_functions[selection](verse)
    more_queries = True
    while more_queries:
        print("[INPUT] Would you like to make another query?")
        input_functions_options()
        selection = input("    Enter a number: ")

def main():
    verse = DeliveryVerse()

    images = input_images_select()
    parser = DeliveryParser(verse)
    parser.detect_deliveries(images)
    verse.build_graph()

    input_functions_select(verse)

if __name__ == "__main__":
    main()
    