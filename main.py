from sentinelhub.constants import CRS, MimeType, MosaickingOrder
from sentinelhub.data_collections import DataCollection
from sentinelhub.api.process import SentinelHubRequest
from sentinelhub.config import SHConfig
from sentinelhub.geometry import BBox
from shapely.geometry import Polygon
from typing import Union, Optional
from dotenv import load_dotenv
from datetime import datetime
from colorama import Style

import matplotlib.pyplot as plt
import tifffile as tiff
import calendar
import time
import os

class ConsolColor:
    @staticmethod
    def CustomColoredText(text : str, r : int, g : int, b : int) -> str:
        """
        Colors a given text to a given RGB color

        Args:
            szoveg (`str`): The text that you want to color.
            r (`int`): RGB color red.
            g (`int`): RGB color green.
            b (`int`): RGB color blue.

        Returns:
            `str`: Gives back the colored text.
        """
    
        color : str = f"\x1b[38;2;{r};{g};{b}m"
        coloredText : str = f"{color}{text}{Style.RESET_ALL}"
        return coloredText

    @staticmethod
    def PreSetUpColoredTextLine(text : str, textType : str) -> str:
        """
        Gives back a line of colored text with pre coded colors.

        Args:
            text (str): The text you want to color.
            textType (str): The color type.

        Returns:
            str: The colored text.

        ## Types
            `ni_tips` -> `not_important_tips` -> Tips that can be overlooked. It is a black color rgb(0,0,0).
            `i_tips` -> `important_tips` -> Tips that can make this process faster.
            `s_color` -> `system_color` -> The basic color that this code use.
            `is_color` -> `important_system_color` -> The system color that you sould look out for.
            `p_error` -> `possible_error` -> This colored message can lead to errors.
            `warning` -> `warning` -> This colored message is a warning.
            `danger` -> `danger` -> This colored message is a danger.
            `success` -> `success` -> This color means that the task went good.
            `info` -> `information` -> This colored message is an information.
        """

        Color : str = ""
        match textType:
            case "ni_tips":
                Color = f"\x1b[38;2;0;0;0m"
            case "i_tips":
                Color = f"\x1b[38;2;150;150;150m"
            case "s_color":
                Color = f"\x1b[38;2;200;200;200m"
            case "is_color":
                Color = f"\x1b[38;2;255;255;255m"
            case "p_error":
                Color = f"\x1b[38;2;255;230;0m"
            case "warning":
                Color = f"\x1b[38;2;255;100;0m"
            case "danger":
                Color = f"\x1b[38;2;255;0;0m"
            case "success":
                Color = f"\x1b[38;2;0;255;0m"
            case "info":
                Color = f"\x1b[38;2;0;0;255m"

        coloredText : str = f"{Color}{text}{Style.RESET_ALL}"
        return coloredText

    @staticmethod
    def PreSetUpColorStart(textType : str) -> str:
        """
        Gives back the start of colored line.

        Args:
            text (str): The text you want to color.
            textType (str): The color type.

        Returns:
            str: The colored text.

        ## Types
            `ni_tips` -> `not_important_tips` -> Tips that can be overlooked. It is a black color rgb(0,0,0).
            `i_tips` -> `important_tips` -> Tips that can make this process faster.
            `s_color` -> `system_color` -> The basic color that this code use.
            `is_color` -> `important_system_color` -> The system color that you sould look out for.
            `p_error` -> `possible_error` -> This colored message can lead to errors.
            `warning` -> `warning` -> This colored message is a warning.
            `danger` -> `danger` -> This colored message is a danger.
            `info` -> `information` -> This colored message is an information.
        """
    
        Color: str = ""
        match textType:
            case "ni_tips":
                Color = f"\x1b[38;2;0;0;0m"
            case "i_tips":
                Color = f"\x1b[38;2;150;150;150m"
            case "s_color":
                Color = f"\x1b[38;2;200;200;200m"
            case "is_color":
                Color = f"\x1b[38;2;255;255;255m"
            case "p_error":
                Color = f"\x1b[38;2;255;230;0m"
            case "warning":
                Color = f"\x1b[38;2;255;100;0m"
            case "danger":
                Color = f"\x1b[38;2;255;0;0m"
            case "info":
                Color = f"\x1b[38;2;0;0;255m"

        finalColor : str = f"{Color}"
        return finalColor

    @staticmethod
    def PreSetUpColorEnd() -> str:
        """
        Gives back the end of colored line.

        Returns:
            str: The end of colored text.
        """
        finalColorEnd = f"{Style.RESET_ALL}"
        return finalColorEnd   

class coordinate:
    __slots__ = ["_x", "_y"]

    def __init__(self, longitude: Union[int, float], latitude: Union[int, float]) -> None:
        self._x: Union[int, float] = longitude
        self._y: Union[int, float] = latitude

    @property
    def longitude(self) -> Union[int, float]:
        return self._x

    @longitude.setter
    def longitude(self, value: Union[int, float]):
        self._x = value

    @property
    def latitude(self) -> Union[int, float]:
        return self._y

    @latitude.setter
    def latitude(self, value: Union[int, float]):
        self._y = value

    def to_tuple(self) -> tuple[Union[int, float], Union[int, float]]:
        return (self._x, self._y)

    def __str__(self) -> str:
        return f"{self._x},{self._y}"

class date:
    __slots__ = ["_year", "_month", "_day"]

    def __init__(self, year: int, month: int, day: int) -> None:
        self._year: int = year
        self._month: int = month
        self._day: int = day

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value: int):
        self._year = value

    @property
    def month(self):
        return self._month

    @month.setter
    def month(self, value: int):
        self._month = value

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, value: int):
        self._day = value

    def __str__(self) -> str:
        return f"{self._year}-{self._month}-{self._day}"

def timer(func):
    def wrapper(*args, **kwargs):
        start: float = time.time()
        result = func(*args, **kwargs)
        end: float = time.time()
        print(f"Took {end-start:.8f} second\n\n")
        return result
    return wrapper

def try_tester(func):
    def wrapper(*args, **kwargs):
        print(ConsolColor.PreSetUpColoredTextLine("Operation starting", "s_color"))
        try:
            resoult = func(*args, **kwargs)

        except Exception as e:
            print(ConsolColor.PreSetUpColoredTextLine(f"Invalid operation: {e}", "danger"))
            return None

        else:
            print(ConsolColor.PreSetUpColoredTextLine(f"Successful operation is done", "success"))

            return resoult

        finally:
            print(ConsolColor.PreSetUpColoredTextLine("Operation ended.", "info"))
    return wrapper

class SentinelHubDownloader:
    __slots__ = ["config", "bands"]

    def __init__(self):
        load_dotenv(".env")
        self.config = SHConfig()
        self.config.sh_client_id = os.getenv("SH_CLIENT_ID", "")
        self.config.sh_client_secret = os.getenv("SH_CLIENT_SECRET", "")
        self.bands = self.ask_for_bands_parameters()

        if self.config.sh_client_id == "" or self.config.sh_client_secret == "":
            raise RuntimeError("Hiányzó Sentinel Hub hitelesítési adatok!")

    @try_tester
    def ask_for_date(self) -> date:
        year: int = int(input(ConsolColor.PreSetUpColoredTextLine("Enter year (e.g., 2026): ", "s_color")))
        month: int = int(input(ConsolColor.PreSetUpColoredTextLine("Enter month (1-12): ", "s_color")))
        day: int = int(input(ConsolColor.PreSetUpColoredTextLine(f"Enter day (1-{calendar.monthrange(year, month)[1]}): ", "s_color")))

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        if day < 1 or day > calendar.monthrange(year, month)[1]:
            raise ValueError(f"Day must be between 1 and {calendar.monthrange(year, month)[1]} for month {month}.")

        return date(year, month, day)

    def ask_for_bands_parameters(self) -> list[str]:
        option_list: list[str] = ["B01","B02","B03","B04","B05","B06","B07", "B08","B8A","B09","B10","B11","B12"]
        print(ConsolColor.PreSetUpColoredTextLine("What do you need from the list:", "s_color"))
        for optionIndex in range(len(option_list)):
            print(ConsolColor.PreSetUpColoredTextLine(f"\t{optionIndex+1})- {option_list[optionIndex]}", "s_color"))
        print(ConsolColor.PreSetUpColoredTextLine("Type the numbers of the options you need separated by commas (e.g., 1,3,5) or type all if you need all. If you want to leave press enter.:", "s_color"))

        try:
            user_input: str = input(ConsolColor.PreSetUpColoredTextLine("?.: ", "s_color")).strip().lower()

            if user_input.lower() == "all":
                print(ConsolColor.PreSetUpColoredTextLine(f"Band parameters is selected. ({user_input})", "success"))
                return option_list

            if user_input == "":
                raise ValueError("Parameters is empty.")
        except ValueError as ve:
            print(ConsolColor.PreSetUpColoredTextLine(f"Invalid input: {ve}", "danger"))
            return ["B01","B02","B03","B04","B05","B06","B07", "B08","B8A","B09","B10","B11","B12"]

        else:
            try:
                selected_options: list[str] = []
                selected_indices: list[int] = [int(x.strip()) for x in user_input.split(",")]
                for index in selected_indices:
                    if 1 <= index <= len(option_list):
                        selected_options.append(option_list[index - 1])
                    else:
                        raise ValueError("Invalid input. Please enter valid option numbers separated by commas, 'all', or press enter to leave:")
            except ValueError as ve:
                print(ConsolColor.PreSetUpColoredTextLine(f"Invalid input: {ve}", "danger"))
                return ["B01","B02","B03","B04","B05","B06","B07", "B08","B8A","B09","B10","B11","B12"]

            else:
                print(ConsolColor.PreSetUpColoredTextLine(f"Successful band parameters selection. ({user_input})", "success"))
                return selected_options

        finally:
            print(ConsolColor.PreSetUpColoredTextLine("Band parameters input attempt completed.", "info"))

    @try_tester
    def getBands(self, bands: Optional[list[str]] = None):
        if bands is None:
            return self.bands
        return bands

    @try_tester
    def getSample(self) -> str:
        return ", ".join([f"sample.{b}" for b in self.getBands()])

    @timer
    @try_tester
    def download(self, polygon_coords: list[tuple[float, float]], resolution: int = 10):
        polygon = Polygon(polygon_coords)
        minx, miny, maxx, maxy = polygon.bounds
        bbox = BBox(bbox=(minx, miny, maxx, maxy), crs=CRS.WGS84)

        width = int((maxx - minx) * 111320 / resolution)
        height = int((maxy - miny) * 110540 / resolution)
        size = (width, height)

        bands_js = ", ".join([f'"{b}"' for b in self.getBands()])
        samples_js = self.getSample()
        
        evalscript = f"""
        //VERSION=3
        function setup() {{
            return {{
                input: [{{
                    bands: [{bands_js}],
                    units: "DN"
                }}],
                output: {{
                    id: "default",
                    bands: {len(self.getBands())},
                    sampleType: "UINT16"
                }}
            }};
        }}

        function evaluatePixel(sample) {{
            return [{samples_js}];
        }}
        """

        request = SentinelHubRequest(
            data_folder="output/SentinelHub",
            evalscript=evalscript,
            input_data=[SentinelHubRequest.input_data(
                DataCollection.SENTINEL2_L1C,
                time_interval=(f"{self.ask_for_date()}", f"{self.ask_for_date()}"),
                )],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=self.config
        )

        response = request.get_data(save_data=True)


if __name__ == "__main__":
    downloader = SentinelHubDownloader()
    polygon_coords = [
        (19.03, 47.47),
        (19.10, 47.47),
        (19.10, 47.52),
        (19.03, 47.52),
        (19.03, 47.47)
    ]
    tiff_path = downloader.download(polygon_coords)
    print(f"Letöltött")