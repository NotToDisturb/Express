import os
from PIL import Image

from graph import DeliveryVerse
from parsing import DeliveryParser
from modes.queries import query_deliveries_per_location, query_deliveries_per_package, query_optimal_route

def images_from_storage(path):
    images = []
    if not os.path.exists(path):
        print("[ERROR] Folder does not exist, use a valid path")
        exit()
    for file in os.listdir(path):
        images.append(Image.open(f"{path}/{file}"))
    return images

def execute_mode(options: dict):
    input_functions = {
        "1": query_deliveries_per_location,
        "2": query_deliveries_per_package,
        "3": query_optimal_route
    }
    verse = DeliveryVerse()
    images = images_from_storage(options["path"])
    parser = DeliveryParser(verse)
    parser.detect_deliveries(images)
    verse.build_graph()
    if options["output"]:
        pass
    else:
        input_functions[options["query"]](verse)