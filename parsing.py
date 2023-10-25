import os
import re
import tesserocr
import numpy as np
from PIL import Image
from graph import Region, Location, Package, DeliveryVerse

GENERIC_TEMPLATES = {
    "simple_contract": {
        "pickup_headers": ["package for pickup", "packages for pickup (any order)"],
        "pickup_package": ["Package #(?P<package_id>.*) from (?P<location>.*) on (?P<region>.*)"],
        "dropoff_headers": ["drop off location", "drop off locations (any order)"],
        "dropoff_package": ["Package #(?P<package_id>.*) to (?P<location>.*) on (?P<region>.*)"]
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
        }
    }
}

DESIRED_ASPECT_RATIO = 16/9
BW_THRESHOLD = 200


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

    def prepare_image(self, image: Image):
        width, height = image.size
        desired_width = DESIRED_ASPECT_RATIO * height
        excess_width = max(width - desired_width, 0)
        cropped_image = image.crop((excess_width / 2, 0, width - excess_width / 2, int(height)))
        array = np.array(cropped_image)
        array[np.where((array <= [BW_THRESHOLD, BW_THRESHOLD, BW_THRESHOLD, 255]).all(axis=2))] = [0, 0, 0, 255]
        array.transpose((2, 0, 1)).reshape(array.shape[0], array.shape[1] * array.shape[2])
        return Image.fromarray(array, mode="RGBA")
    
    def crop_mission_title(self, image: Image):
        width, height = image.size
        left_crop = int(width / 10 * 4)
        top_crop = int(height / 6)
        right_crop = int(width / 14)
        bottom_crop = int(height / 5 * 4)
        cropped_image = image.crop((left_crop, top_crop, width - right_crop, height - bottom_crop))
        # Need to copy to new image or Tesseract throws an error
        new_image = Image.new("RGB", (width - left_crop - right_crop, height - top_crop - bottom_crop))
        new_image.paste(cropped_image, (0, 0))
        return new_image

    def crop_mission_text(self, image: Image):
        width, height = image.size
        left_crop = int(width / 10 * 4)
        top_crop = int(height / 2.5)
        right_crop = int(width / 14)
        bottom_crop = int(height / 4.5)
        cropped_image = image.crop((left_crop, top_crop, width - right_crop, height - bottom_crop))
        # Need to copy to new image or Tesseract throws an error
        new_image = Image.new("RGB", (width - left_crop - right_crop, height - top_crop - bottom_crop))
        new_image.paste(cropped_image, (0, 0))
        return new_image

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
            package_dict["region"] = self.verse.locations[package_dict["location"]].region.region if package_dict["location"] in self.verse.locations else ""
        return package_dict

    def process_package_dict(self, package_dict):
        region_str = package_dict["region"]
        location_str = package_dict["location"]
        self.verse.regions[region_str] = self.verse.regions.get(region_str, Region(region_str))
        self.verse.locations[location_str] = self.verse.locations.get(location_str, Location(location_str, self.verse.regions[region_str]))

    def detect_deliveries(self, mission: int, image: Image):
        image = self.prepare_image(image)
        print(f"[INFO] Processing image {mission + 1}")
        text = tesserocr.image_to_text(self.crop_mission_text(image), path=f"{os.path.dirname(__file__)}/tessdata")
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