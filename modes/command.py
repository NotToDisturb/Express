import os
from PIL import Image

from graph import DeliveryVerse
from parsing import DeliveryParser
import modes.queries as queries

def images_from_storage(path):
    images = []
    if not os.path.exists(path):
        print("[ERROR] Folder does not exist, use a valid path")
        exit()
    for file in os.listdir(path):
        images.append(Image.open(f"{path}/{file}"))
    return images

def query_deliveries_per_package(options: dict, verse: DeliveryVerse):
    if options["output"]:
        pass
    else:
        queries.query_show_deliveries_per_package(verse)

def query_deliveries_per_location(options: dict, verse: DeliveryVerse):
    if options["output"]:
        pass
    else:
        queries.query_show_deliveries_per_location(verse)

def query_optimal_route(options: dict, verse: DeliveryVerse):
    if options["output"]:
        pass
    else:
        queries.query_show_optimal_route(verse)
        

def execute_mode(options: dict):
    input_functions = {
        "1": query_deliveries_per_package,
        "2": query_deliveries_per_location,
        "3": query_optimal_route
    }
    verse = DeliveryVerse()
    images = images_from_storage(options["path"])
    parser = DeliveryParser(verse)
    for index in range(len(images)):
        parser.detect_deliveries(index, images[index])
        parser.detections[-1].confirm_detections()
    verse.build_graph()
    if options["output"]:
        pass
    else:
        input_functions[options["query"]](options, verse)