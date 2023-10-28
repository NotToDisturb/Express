import os
import keyboard
from PIL import Image, ImageGrab

import modes.queries as queries
from graph import DeliveryVerse
from parsing import DeliveryParser, DeliveryDetections

def images_from_screenshots(parser: DeliveryParser):
    print("[INFO] Taking screenshots")
    print("    ENTER to screenshot")
    print("    SPACE to continue")
    taking = True
    index = 0
    while taking:
        if keyboard.is_pressed("enter"):
            print("    Took screenshot")
            process_image(parser, index, ImageGrab.grab(), True)
            index += 1
        elif keyboard.is_pressed("space"):
            taking = False

def images_from_storage(parser: DeliveryParser):
    path = input("[INPUT] Enter a folder path: ")
    while not os.path.exists(path):
        path = input("[INPUT] Path does not exist, enter a folder path: ")
    for index, file in enumerate(os.listdir(path)):
        process_image(parser, index, Image.open(f"{path}/{file}"), validate=False)

def validate_image(detections: DeliveryDetections, index: int):
    queries.query_show_detected_packages(detections, index)
    return True

def process_image(parser: DeliveryParser, index: int, image: Image, validate: bool):
        parser.detect_deliveries(index, image)
        validated = True if not validate else validate_image(parser.detections[-1], index)
        if validated:
            parser.detections[-1].confirm_detections()

def select_and_process_images(parser: DeliveryParser):
    input_images = {
        "1": images_from_screenshots,
        "2": images_from_storage
    }
    print("[INPUT] What images do you want to use?")
    print("    1. Take screenshots")
    print("    2. Images on a folder")
    selection = input("    Enter a number: ")
    return input_images[selection](parser)

def show_queries():
    print("    1. Deliveries per location")
    print("    2. Deliveries per package")
    print("    3. Optimal path")
    print("    4. Exit")

def select_query(verse):
    input_functions = {
        "1": queries.query_show_deliveries_per_package,
        "2": queries.query_show_deliveries_per_location,
        "3": queries.query_show_optimal_route,
        "4": queries.query_exit
    }
    print("[INPUT] What query would you like to make?")
    show_queries()
    selection = input("    Enter a number: ")
    input_functions[selection](verse)
    while True:
        print("[INPUT] Would you like to make another query?")
        show_queries()
        selection = input("    Enter a number: ")
        input_functions[selection](verse)

def execute_mode(_: dict):
    verse = DeliveryVerse()
    parser = DeliveryParser(verse)
    select_and_process_images(parser)
    verse.build_graph()
    select_query(verse)