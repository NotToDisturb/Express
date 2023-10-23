import os
import tesserocr
from graph import Region, Location, Package, DeliveryVerse

PICK_UP_STRING = "PICK UP"
DROP_OFF_STRING = "DROP OFF"
PACKAGE_STRING = "Package"
TO_STRING = " to "
FROM_STRING = " from "
ON_STRING = " on "
ID_LENGTH = 6
INFINITY = float("inf")

class DeliveryParser:
    def __init__(self, verse: DeliveryVerse):
        self.verse = verse

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
            package_dict["region"] = self.verse.locations[package_dict["location"]].region.region if package_dict["location"] in self.locations else ""
        return package_dict

    def process_package_dict(self, package_dict):
        region_str = package_dict["region"]
        location_str = package_dict["location"]
        self.verse.regions[region_str] = self.verse.regions.get(region_str, Region(region_str))
        self.verse.locations[location_str] = self.verse.locations.get(location_str, Location(location_str, self.verse.regions[region_str]))

    def detect_deliveries(self, images):
        for i in range(len(images)):
            print(f"[INFO] Processing image {i + 1}")
            text = tesserocr.image_to_text(images[i], path=f"{os.path.dirname(os.path.abspath(__file__))}/tessdata")
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
                    package = Package(i, pickup_dict["id"], self.verse.locations[pickup_dict["location"]], self.verse.locations[dropoff_dict["location"]])
                    self.verse.packages[pickup_dict["id"]] = package
            else:
                print(f"    [ERROR] Differing pickup ({len(pickup_lines)}) and dropoff ({len(dropoff_lines)}) package counts, aborting")