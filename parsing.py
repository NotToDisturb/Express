import re
from PIL import Image

from recognition import DeliveryOCR
from graph import Region, Location, Package, DeliveryVerse

START_WITH_ANY = ""
GENERIC_TEMPLATES = {
    "simple_contract": {
        "pickup_headers": ["PACKAGE FOR PICK UP", "PACKAGES FOR PICK UP \(ANY ORDER\)"],
        "pickup_package": ["Package \#(?P<name>.*) from (?P<location>.*) on (?P<region>.*)"],
        "dropoff_headers": ["DROP OFF LOCATION", "DROP OFF LOCATIONS \(ANY ORDER\)"],
        "dropoff_package": ["Package \#(?P<name>.*) to (?P<location>.*) on (?P<region>.*)"]
    },
    "one_to_n": {
        "pickup_headers": ["PACKAGE FOR PICK UP", "PACKAGES FOR PICK UP \(ANY ORDER\)"],
        "pickup_package": ["Collect all packages from (?P<location>.*) on (?P<region>.*)"],
        "dropoff_headers": ["DROP OFF LOCATION", "DROP OFF LOCATIONS \(ANY ORDER\)"],
        "dropoff_package": ["Package \#(?P<name>.*) to (?P<location>.*) on (?P<region>.*)"]
    }
}
PER_COMPANY_TEMPLATES = {
    "covalex": {
        "simple_contract": {
            "titles": ["Covalex Evaluation", "Covalex Local Delivery Route"],
            "pickup_headers": GENERIC_TEMPLATES["simple_contract"]["pickup_headers"],
            "pickup_package": GENERIC_TEMPLATES["simple_contract"]["pickup_package"],
            "dropoff_headers": GENERIC_TEMPLATES["simple_contract"]["dropoff_headers"],
            "dropoff_package": GENERIC_TEMPLATES["simple_contract"]["dropoff_package"]
        },
        "one_to_n": {
            "titles": ["Shipping Error - QT Sensitive Cargo"],
            "pickup_headers": GENERIC_TEMPLATES["one_to_n"]["pickup_headers"],
            "pickup_package": GENERIC_TEMPLATES["one_to_n"]["pickup_package"],
            "dropoff_headers": GENERIC_TEMPLATES["one_to_n"]["dropoff_headers"],
            "dropoff_package": GENERIC_TEMPLATES["one_to_n"]["dropoff_package"]
        }
    }
}
COMPANY_TO_PROPER_NAME = {
    "covalex": "Covalex Shipping"
}

GROUP_EXPRESSION = "\(\?P"


class LocationDetection:
    def __init__(self, name: str, region: str):
        self.name = name
        self.region = region

class PickupDetection:
    def __init__(self, name: str, location: LocationDetection):
        self.name = name
        self.location = location

class DropoffDetection:
    def __init__(self, name: str, location: LocationDetection):
        self.name = name
        self.location = location

class PackageDetection:
    def __init__(self, name: str, pickup_location: LocationDetection, dropoff_location: LocationDetection):
        self.name = name
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location

class DeliveryDetections:
    def __init__(self, verse: DeliveryVerse, mission: int, company: str, contract: str):
        self.verse = verse
        self.mission = mission
        self.company = company
        self.contract = contract

        self.pickups = {}
        self.dropoffs = {}

        self.locations = {}
        self.packages = {}

    def add_detection(self, package: str, location: str, region: str, task: str):
        if task == "pickup":
            self.pickups[package] = PickupDetection(package, self.__try_add_location(location, region))
        elif task == "dropoff":
            if self.pickups.get(package, None):
                self.__add_dropoff_detection(package, location, region)
            elif len(self.pickups) > len(self.dropoffs):
                pickup_name = self.pickups[list(self.pickups.keys())[len(self.dropoffs)]].name
                self.__add_dropoff_detection(pickup_name, location, region)
            else:
                print(f"[ERROR] Differing pickup ({len(self.pickups)}) and dropoff ({len(self.dropoffs) + 1}+) task counts, aborting")
                exit()

    def confirm_detections(self):
        for location in self.locations.values():
            self.__apply_verse_location(location)
        for package in self.packages.values():
            self.__apply_verse_package(package)

    def __try_add_location(self, location: str, region: str):
        if not self.locations.get(location, None):
            self.locations[location] = LocationDetection(location, region)
        return self.locations[location]
    
    def __add_dropoff_detection(self, package: str, location: str, region: str):
        self.dropoffs[package] = DropoffDetection(package, self.__try_add_location(location, region))
        self.packages[package] = PackageDetection(package, self.pickups[package].location, self.dropoffs[package].location)

    def __apply_verse_location(self, location: LocationDetection):
        if not self.verse.regions.get(location.region, None):
            self.verse.regions[location.region] = Region(location.region)
        if not self.verse.locations.get(location.name, None):
            self.verse.locations[location.name] = Location(location.name, self.verse.regions[location.region])

    def __apply_verse_package(self, package: PackageDetection):
        self.verse.packages[package.name] = Package(self.mission, package.name, 
                                                    self.verse.locations[package.pickup_location.name], 
                                                    self.verse.locations[package.dropoff_location.name])


class DeliveryParser:
    def __init__(self, verse: DeliveryVerse):
        self.verse = verse
        self.detections = []

    def get_delivery_company_and_contract(self, title: str):
        for company, contracts in PER_COMPANY_TEMPLATES.items():
            for contract in contracts.keys():
                for template in contracts[contract]["titles"]:
                    finds = re.findall(template, title)
                    if len(finds) > 0:
                        return company, contract
        print(f"[WARN] No template matches title '{title}'")

    def get_headers_index(self, detections: DeliveryDetections, task: str, lines: list, start_index=0):
        for index in range(start_index, len(lines)):
            for template in PER_COMPANY_TEMPLATES[detections.company][detections.contract][f"{task}_headers"]:
                finds = re.findall(template, lines[index])
                if len(finds) > 0:
                    return index
        print(f"[WARN] No line found containing {COMPANY_TO_PROPER_NAME[detections.company]} {task} headers")
        return start_index

    def match_line_to_package_template(self, detections, task, line):
        for template in PER_COMPANY_TEMPLATES[detections.company][detections.contract][f"{task}_package"]:
            matches = re.match(f".*{template}", line)
            group_count = len(re.findall(GROUP_EXPRESSION, template))
            if matches and len(matches.groups()) == group_count:
                detections.add_detection(matches.group("name"), matches.group("location"), matches.group("region"), task)
                return True, group_count
        return False, -1

    def get_packages_and_index(self, detections: DeliveryDetections, task: str, lines: list, start_index: int):
        matched = False
        for index in range(start_index, len(lines)):
            line_matched = False
            group_count = 0
            if lines[index] != "":
                line_matched, group_count = self.match_line_to_package_template(detections, task, lines[index])
            if line_matched:
                matched = True
            else:
                if lines[index] != "":
                    print(f"[WARN] Could not find all {group_count} field{'s' if group_count != 1 else ''} for {task} delivery '{lines[index]}', this will cause dragons")
                if matched:
                    return index
        if not matched:
            print(f"[WARN] Could not find any packages for {task} task, this will cause dragons")
            return start_index
                

    def detect_deliveries(self, mission: int, image: Image):
        ocr = DeliveryOCR(image)
        print(f"[INFO] Processing image {mission + 1}")

        company, contract = self.get_delivery_company_and_contract(ocr.texts["title"])
        detections = DeliveryDetections(self.verse, mission, company, contract)
        self.detections.append(detections)
        lines = ocr.texts["text"].split("\n")
        pickup_headers_index = self.get_headers_index(detections, "pickup", lines)
        last_pickup_index = self.get_packages_and_index(detections, "pickup", lines, pickup_headers_index + 1)
        dropoff_headers_index = self.get_headers_index(detections, "dropoff", lines, last_pickup_index + 1)
        self.get_packages_and_index(detections, "dropoff", lines, dropoff_headers_index + 1)