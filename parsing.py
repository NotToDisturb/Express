import re
from PIL import Image

from recognition import DeliveryOCR
from graph import Region, Location, Package, DeliveryVerse

GENERIC_TEMPLATES = {
    "simple_contract": {
        "pickup_headers": ["PACKAGE FOR PICK UP", "PACKAGES FOR PICK UP \(ANY ORDER\)"],
        "pickup_package": ["- Package \#(?P<name>.*) from (?P<location>.*) on (?P<region>.*)"],
        "dropoff_headers": ["DROP OFF LOCATION", "DROP OFF LOCATIONS \(ANY ORDER\)"],
        "dropoff_package": ["- Package \#(?P<name>.*) to (?P<location>.*) on (?P<region>.*)"]
    },
    "one_to_n": {
        "pickup_headers": ["PACKAGE FOR PICK UP", "PACKAGES FOR PICK UP \(ANY ORDER\)"],
        "pickup_package": ["- Package \#(?P<name>.*) from (?P<location>.*) on (?P<region>.*)"],
        "dropoff_headers": ["DROP OFF LOCATION", "DROP OFF LOCATIONS \(ANY ORDER\)"],
        "dropoff_package": ["- Package \#(?P<name>.*) to (?P<location>.*) on (?P<region>.*)"]
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

PICK_UP_STRING = "PICK UP"
DROP_OFF_STRING = "DROP OFF"
PACKAGE_STRING = "Package"
TO_STRING = " to "
FROM_STRING = " from "
ON_STRING = " on "
ID_LENGTH = 6
INFINITY = float("inf")

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
        self.regions = {}
        self.locations = {}
        self.packages = {}

    def confirm_detections(self):
        self.__apply_list(self.regions, self.verse.regions)
        self.__apply_list(self.locations, self.verse.locations)
        self.__apply_list(self.packages, self.verse.packages)
    
    def __apply_list(self, detections_list: list, verse_dict: dict):
        for element in detections_list:
            if not element.name in verse_dict.keys():
                verse_dict[element.name] = element

class DeliveryParser:
    def __init__(self, verse: DeliveryVerse):
        self.verse = verse
        self.detections = []

    def get_package_lines(self, packages_str):
        return [package_line for package_line in packages_str.split("\n") if PACKAGE_STRING in package_line]

    def package_line_to_dict(self, package_line):
        package_dict = {}
        id_index = package_line.index("#") + 1
        location_index = package_line.index(FROM_STRING) + len(FROM_STRING) if FROM_STRING in package_line else package_line.index(TO_STRING) + len(TO_STRING)
        package_dict["id"] = package_line[id_index:id_index + ID_LENGTH]
        on_index = -1
        try:
            on_index = package_line.index(ON_STRING)
            package_dict["region"] = package_line[on_index + len(ON_STRING):]
            package_dict["location"] = package_line[location_index:on_index]
        except ValueError:
            print(f"    [WARN] Could not find region string, targeting end of line ({package_line[location_index:]})")
            package_dict["location"] = package_line[location_index:]
            package_dict["region"] = self.verse.locations[package_dict["location"]].region.name if package_dict["location"] in self.verse.locations else ""
        return package_dict

    def process_package_dict(self, package_dict):
        region_str = package_dict["region"]
        location_str = package_dict["location"]
        self.verse.regions[region_str] = self.verse.regions.get(region_str, Region(region_str))
        self.verse.locations[location_str] = self.verse.locations.get(location_str, Location(location_str, self.verse.regions[region_str]))

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
        print(start_index)
        return start_index
    
    def build_task_detection(package: str, location: str, region: str, task: str):
        if task == "pickup":
            return PickupDetection(package)

    def get_packages_and_index(self, detections: DeliveryDetections, task: str, lines: list, start_index: int):
        matched = False
        for index in range(start_index, len(lines)):
            line_matched = False
            for template in PER_COMPANY_TEMPLATES[detections.company][detections.contract][f"{task}_package"]:
                matches = re.match(template, lines[index])
                expected_group_count = len(re.findall(GROUP_EXPRESSION, template))
                if matches and len(matches.groups()) == expected_group_count:
                    # Do stuff
                    if not matched:
                        matched = True
                    if not line_matched:
                        line_matched = True
                    break
            if not line_matched:
                print(f"[WARN] Could not find all {expected_group_count} field{'s' if expected_group_count != 1 else ''} for a delivery")
                if matched:
                    return index
        if not matched:
            print(f"[WARN] Could not find any packages for {task} task")
            return start_index
                

    def detect_deliveries(self, mission: int, image: Image):
        ocr = DeliveryOCR(image)
        print(f"[INFO] Processing image {mission + 1}")

        """WIP PARSING REWRITE
        company, contract = self.get_delivery_company_and_contract(ocr.texts["title"])
        detections = DeliveryDetections(self.verse, mission, company, contract)
        self.detections.append(detections)
        lines = ocr.texts["text"].split("\n")
        pickup_headers_index = self.get_headers_index(detections, "pickup", lines)
        last_pickup_index = self.get_packages_and_index(detections, "pickup", lines, pickup_headers_index)
        dropoff_headers_index = self.get_headers_index(detections, "dropoff", lines, last_pickup_index)
        self.get_packages_and_index(detections, "dropoff", lines, dropoff_headers_index)"""


        text = ocr.texts["text"]
        pickup_index = text.index(PICK_UP_STRING)
        dropoff_index = text.index(DROP_OFF_STRING)
        pickup_packages = text[pickup_index:dropoff_index]
        dropoff_packages = text[dropoff_index:]
        pickup_lines = self.get_package_lines(pickup_packages)
        dropoff_lines = self.get_package_lines(dropoff_packages)
        if len(pickup_lines) == len(dropoff_lines):
            for line in range(len(pickup_lines)):
                pickup_dict = self.package_line_to_dict(pickup_lines[line])
                dropoff_dict = self.package_line_to_dict(dropoff_lines[line])
                if pickup_dict["id"] != dropoff_dict["id"]:
                    print(f"    [WARN] Differing pickup #{pickup_dict['id']} and dropoff #{dropoff_dict['id']} package IDs, using #{pickup_dict['id']}")
                self.process_package_dict(pickup_dict)
                self.process_package_dict(dropoff_dict)
                package = Package(mission, pickup_dict["id"], self.verse.locations[pickup_dict["location"]], self.verse.locations[dropoff_dict["location"]])
                self.verse.packages[pickup_dict["id"]] = package
        else:
            print(f"    [ERROR] Differing pickup ({len(pickup_lines)}) and dropoff ({len(dropoff_lines)}) package counts, aborting")