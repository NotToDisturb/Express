import os
import keyboard
from PIL import Image, ImageGrab

import modes.queries as queries
from graph import DeliveryVerse
from parsing import DeliveryParser

# TODO: Allow retake and cancel of screenshots, showing detected packages

def images_from_screenshots():
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

def images_from_storage():
    images = []
    path = input("[INPUT] Enter a folder path: ")
    while not os.path.exists(path):
        path = input("[INPUT] Path does not exist, enter a folder path: ")
    for file in os.listdir(path):
        images.append(Image.open(f"{path}/{file}"))
    return images



def select_images():
    input_images = {
        "1": images_from_screenshots,
        "2": images_from_storage
    }
    print("[INPUT] What images do you want to use?")
    print("    1. Take screenshots")
    print("    2. Images on a folder")
    selection = input("    Enter a number: ")
    return input_images[selection]()

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
    images = select_images()
    parser = DeliveryParser(verse)
    for index in range(len(images)):
        parser.detect_deliveries(index, images[index])
    verse.build_graph()
    select_query(verse)