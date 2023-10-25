class Region:
    locations = []

    def __init__(self, name: str):
        self.name = name

class Location:

    def __init__(self, name: str, region: Region):
        self.pickup_packages = []
        self.dropoff_packages = []
        self.name = name
        self.region = region
        self.region.locations.append(self)

    def __str__(self):
        return self.name

class Package:
    def __init__(self, mission: int, name: str, pickup_location: Location, dropoff_location: Location):
        self.mission = mission
        self.name = name
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location
        self.pickup_location.pickup_packages.append(self)
        self.dropoff_location.dropoff_packages.append(self)

    def __str__(self):
        return self.name

class Task:
    def __init__(self, package: Package, location: Location, task: str):
        self.task = task
        self.package = package
        self.location = location
        self.done = False

    def __str__(self):
        return f"{self.task} {self.package.name}"

class Dropoff(Task):
    def __init__(self, package: Package):
        super(Dropoff, self).__init__(package, package.dropoff_location, "Drop off")

class Pickup(Task):
    def __init__(self, package: Package, dropoff: Dropoff):
        super(Pickup, self).__init__(package, package.pickup_location, "Pick up")
        dropoff.pickup = self
    
class DeliveryVerse:
    def __init__(self):
        # Verse
        self.regions = {"Lyria": Region("Lyria"), "Wala": Region("Wala")}
        self.locations = {}
        self.packages = {}
        # Graph
        self.tasks = []
        self.distances = {}

    def build_graph(self):
        self.tasks = []
        self.distances = {}
        used_locations = []
        for package in self.packages.values():
            if package.pickup_location not in used_locations:
                used_locations.append(package.pickup_location)
            if package.dropoff_location not in used_locations:
                used_locations.append(package.dropoff_location)
            dropoff = Dropoff(package)
            self.tasks.append(dropoff)
            self.tasks.append(Pickup(package, dropoff))
        for source_location in used_locations:
            self.distances[source_location] = {}
            for target_location in used_locations:
                if source_location == target_location:
                    continue
                elif source_location.region == target_location.region:
                    self.distances[source_location][target_location] = 1
                else:
                    self.distances[source_location][target_location] = 10

    def get_shortest_route(self):
        results = {}
        for start_task in [task for task in self.tasks if isinstance(task, Pickup)]:
            current_task = start_task
            current_distance = 0
            unfulfilled = {task: 0 for task in self.tasks} 
            route = []
            unfulfilled[start_task] = current_distance
            while True:
                self.evaluate_and_complete_tasks(unfulfilled, current_task, route)
                self.evaluate_potential_next_tasks(unfulfilled, current_task, current_distance)
                
                if len(unfulfilled) == 0: # If all tasks fulfilled, exit loop
                    break
                candidates = [unfulfilled_task for unfulfilled_task in unfulfilled.items() if unfulfilled_task[1] != 0]
                current_task, current_distance = sorted(candidates, key=lambda x: x[1])[0]
            
            results[start_task] = {
                "route": route,
                "distance": current_distance
            }
            self.reset_tasks()
        return results[sorted(results, key=lambda x: results[x]["distance"])[0]]["route"]
    
    def evaluate_potential_next_tasks(self, unfulfilled: dict, current_task: Task, current_distance: int):
        for next_task in unfulfilled:
            if current_task.location == next_task.location:
                continue
            distance = self.distances[current_task.location][next_task.location]
            if isinstance(next_task, Dropoff) and not next_task.pickup.done: 
                continue
            new_distance = current_distance + distance
            if unfulfilled[next_task] == 0 or unfulfilled[next_task] > new_distance:
                unfulfilled[next_task] = new_distance

    def evaluate_and_complete_tasks(self, unfulfilled: dict, current_task: Task, route: list):
        delete_queue = []
        for other_task in unfulfilled.keys():
            if current_task.location == other_task.location and (isinstance(other_task, Pickup) or (isinstance(other_task, Dropoff) and other_task.pickup.done)):
                other_task.done = True
                route.append(other_task)
                delete_queue.append(other_task)
        for delete in delete_queue:
            unfulfilled.pop(delete)

    def reset_tasks(self):
        for task in self.tasks:
            task.done = False