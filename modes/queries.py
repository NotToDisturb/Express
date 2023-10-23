def query_deliveries_per_location(verse):
    print("\n[INFO] Detected deliveries:") 
    for location in verse.locations.values():
        if len(location.pickup_packages) == 0 and len(location.dropoff_packages) == 0:
            continue
        print(f"{location.location}")
        print(f" - Pickup: {', '.join([package.package for package in location.pickup_packages])}")
        print(f" - Dropoff: {', '.join([package.package for package in location.dropoff_packages])}")

def query_deliveries_per_package(verse):
    for package in verse.packages.values():
        print(package)

def query_optimal_route(verse):
    verse.build_graph()
    route = verse.get_shortest_route()
    print("\n[INFO] Optimal route is:")
    for step in route:
        print(f"    {step.location}: {step}")