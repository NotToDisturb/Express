from tabulate import tabulate

from graph import DeliveryVerse
from parsing import DeliveryDetections

def query_show_detected_packages(detections: DeliveryDetections, index: int):
    headers = ["Mission", "ID", "Pickup location", "Dropoff location"]
    rows = [(index + 1, package.name, 
             f"{package.pickup_location.name}, {package.pickup_location.region}",
             f"{package.dropoff_location.name}, {package.dropoff_location.region}")
             for package in detections.packages.values()]
    table = tabulate(rows, headers, tablefmt="simple_outline", numalign="center", stralign="center")
    print(f"{table}")

def query_show_deliveries_per_package(verse: DeliveryVerse):
    headers = ["Mission", "ID", "Pickup location", "Dropoff location"]
    rows = [(package.mission + 1, package.name, 
             f"{package.pickup_location.name}, {package.pickup_location.region.name}",
             f"{package.dropoff_location.name}, {package.dropoff_location.region.name}")
             for package in verse.packages.values()]
    table = tabulate(rows, headers, tablefmt="simple_outline", numalign="center", stralign="center")
    print(f"\n{table}")

def generate_package_list(packages: list):
    return f"({len(packages)}) {', '.join([package.name for package in packages])}" if len(packages) else ""

def query_show_deliveries_per_location(verse: DeliveryVerse):
    headers = ["Location", "Task", "Packages"]
    rows = [(f"{location.name}, {location.region.name}", "Pick up\nDrop off",
             f"{generate_package_list(location.pickup_packages)}\n{generate_package_list(location.dropoff_packages)}" )
             for location in verse.locations.values()]
    table = tabulate(rows, headers, tablefmt="simple_grid", numalign="center", stralign="center")
    print(f"\n{table}")

def query_show_optimal_route(verse: DeliveryVerse):
    verse.build_graph()
    route = verse.get_shortest_route()
    headers = ["Location", "Task", "ID", "Mission"]
    rows = [(step.location, step.task, step.package.name, step.package.mission + 1)
             for step in route]
    table = tabulate(rows, headers, tablefmt="simple_outline", numalign="center", stralign="center")
    print(f"\n{table}")

def query_exit(_: DeliveryVerse):
    exit()
