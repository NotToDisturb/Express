import os
import tesserocr
import numpy as np
from PIL import Image

DESIRED_ASPECT_RATIO = 16/9
BW_THRESHOLD = 200

class DeliveryOCR:
    def __init__(self, image: Image):
        self.image = self.__prepare_image(image)
        self.cropped = {
            "title": self.__crop_mission_title(),
            "text": self.__crop_mission_text()
        }
    
    def __prepare_image(self, image: Image):
        width, height = image.size
        desired_width = DESIRED_ASPECT_RATIO * height
        excess_width = max(width - desired_width, 0)
        cropped_image = image.crop((excess_width / 2, 0, width - excess_width / 2, int(height)))
        array = np.array(cropped_image)
        array[np.where((array <= [BW_THRESHOLD, BW_THRESHOLD, BW_THRESHOLD, 255]).all(axis=2))] = [0, 0, 0, 255]
        array.transpose((2, 0, 1)).reshape(array.shape[0], array.shape[1] * array.shape[2])
        return Image.fromarray(array, mode="RGBA")

    def __crop_image(self, left_crop: int, top_crop: int, right_crop: int, bottom_crop: int):
        width, height = self.image.size
        cropped_image = self.image.crop((left_crop, top_crop, width - right_crop, height - bottom_crop))
        # Need to copy to new image or Tesseract throws an error
        new_image = Image.new("RGB", (width - left_crop - right_crop, height - top_crop - bottom_crop))
        new_image.paste(cropped_image, (0, 0))
        return new_image

    def __crop_mission_title(self):
        width, height = self.image.size
        left_crop = int(width / 10 * 4)
        top_crop = int(height / 6)
        right_crop = int(width / 14)
        bottom_crop = int(height / 5 * 4)
        return self.__crop_image(left_crop, top_crop, right_crop, bottom_crop)

    def __crop_mission_text(self, image: Image):
        width, height = image.size
        left_crop = int(width / 10 * 4)
        top_crop = int(height / 2.5)
        right_crop = int(width / 14)
        bottom_crop = int(height / 4.5)
        return self.__crop_image(left_crop, top_crop, right_crop, bottom_crop)

    def get_text(self, property: str):
        return tesserocr.image_to_text(self.cropped[property], path=f"{os.path.dirname(__file__)}/tessdata")