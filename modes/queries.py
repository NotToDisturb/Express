from graph import Location, DeliveryVerse

def query_show_deliveries_per_package(verse):
    print(f"\n┌{'─'*100}┐")
    print("│ {:^98} │".format("Detected packages"))
    print(f"├{'─'*9}┬{'─'*10}┬{'─'*39}┬{'─'*39}┤")
    print("│ {:7} │ {:^8} │ {:^37} │ {:^37} │".format(*["Mission", "ID", "Pickup location", "Dropoff location"]))
    print(f"├{'─'*9}┼{'─'*10}┼{'─'*39}┼{'─'*39}┤")
    for package in verse.packages.values():
        print(package)
    print(f"└{'─'*9}┴{'─'*10}┴{'─'*39}┴{'─'*39}┘\n")

def generate_package_list(packages: list):
    return f"({len(packages)}) {', '.join([package.package for package in packages])}"

def generate_package_lists(verse: DeliveryVerse):
    max_length = 0
    package_lists = {
        "pickups": {},
        "dropoffs": {}
    }
    for location in verse.locations.values():
        if len(location.pickup_packages) == 0 and len(location.dropoff_packages) == 0:
            continue
        package_lists["pickups"][location] = generate_package_list(location.pickup_packages) if len(location.pickup_packages) else ""
        package_lists["dropoffs"][location] = generate_package_list(location.dropoff_packages) if len(location.dropoff_packages) else ""
        if len(package_lists["pickups"][location]) > max_length:
            max_length = len(package_lists["pickups"][location])
        if len(package_lists["dropoffs"][location]) > max_length:
            max_length = len(package_lists["dropoffs"][location])
    return max_length, package_lists


def query_show_deliveries_per_location(verse: DeliveryVerse):
    max_length, package_lists = generate_package_lists(verse)
    print(f"\n┌{'─'*(max_length + 55)}┐")
    print("│ {:^{total_length}} │".format("Detected packages per location", total_length=max_length + 53))
    print(f"├{'─'*41}┬{'─'*10}┬{'─'*(max_length + 2)}┤")
    print("│ {:^39} │ {:^8} │ {:^{max_length}} │".format(*["Location", "Task", "Packages"], max_length=max_length))
    for location in verse.locations.values():
        full_location = f"{location.location}, {location.region.region}"
        print(f"├{'─'*41}┼{'─'*10}┼{'─'*(max_length + 2)}┤")
        print("│ {:>39} │ {:^8} │ {:^{max_length}} │".format(*[full_location, "Pick up", package_lists["pickups"][location]], max_length=max_length))
        print("│ {:>39} │ {:^8} │ {:^{max_length}} │".format(*["", "Drop off", package_lists["dropoffs"][location]], max_length=max_length))
    print(f"└{'─'*41}┴{'─'*10}┴{'─'*(max_length + 2)}┘\n")

def query_show_optimal_route(verse):
    verse.build_graph()
    route = verse.get_shortest_route()
    print(f"\n┌{'─'*71}┐")
    print("│ {:^69} │".format("Optimal path"))
    print(f"├{'─'*41}┬{'─'*10}┬{'─'*8}┬{'─'*9}┤")
    print("│ {:^39} │ {:^8} │ {:^6} │ {:^7} │".format(*["Location", "Task", "ID", "Mission"]))
    print(f"├{'─'*41}┼{'─'*10}┼{'─'*8}┼{'─'*9}┤")
    for step in route:
        print(step)
    print(f"└{'─'*41}┴{'─'*10}┴{'─'*8}┴{'─'*9}┘\n")