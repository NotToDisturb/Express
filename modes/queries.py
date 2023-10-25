from tabulate import tabulate

from graph import DeliveryVerse

def query_show_deliveries_per_package(verse: DeliveryVerse):
    headers = ["Mission", "ID", "Pickup location", "Dropoff location"]
    rows = [(package.mission + 1, package.package, 
             f"{package.pickup_location.location}, {package.pickup_location.region.region}",
             f"{package.dropoff_location.location}, {package.dropoff_location.region.region}")
             for package in verse.packages.values()]
    table = tabulate(rows, headers, tablefmt="simple_outline", numalign="center", stralign="center")
    print(f"\n{table}")

def generate_package_list(packages: list):
    return f"({len(packages)}) {', '.join([package.package for package in packages])}" if len(packages) else ""

def query_show_deliveries_per_location(verse: DeliveryVerse):
    headers = ["Location", "Task", "Packages"]
    rows = [(f"{location.location}, {location.region.region}", "Pick up\nDrop off",
             f"{generate_package_list(location.pickup_packages)}\n{generate_package_list(location.dropoff_packages)}" )
             for location in verse.locations.values()]
    table = tabulate(rows, headers, tablefmt="simple_grid", numalign="center", stralign="center")
    print(f"\n{table}")

def query_show_optimal_route(verse: DeliveryVerse):
    verse.build_graph()
    route = verse.get_shortest_route()
    headers = ["Location", "Task", "ID", "Mission"]
    rows = [(step.location, step.task, step.package.package, step.package.mission + 1)
             for step in route]
    table = tabulate(rows, headers, tablefmt="simple_outline", numalign="center", stralign="center")
    print(f"\n{table}")

def query_exit(_: DeliveryVerse):
    exit()
