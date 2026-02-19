from sentinelhub.constants import CRS, MimeType, MosaickingOrder
from sentinelhub.data_collections import DataCollection
from sentinelhub.api.process import SentinelHubRequest
from sentinelhub.config import SHConfig
from sentinelhub.geometry import BBox
from shapely.geometry import Polygon
from typing import Union, Optional
from dotenv import load_dotenv
from datetime import datetime

import matplotlib.pyplot as plt
import tifffile as tiff 
import os

class SentinelHubDownloader:
    __slots__ = ["config"]

    def __init__(self):
        load_dotenv(".env")
        self.config = SHConfig()
        self.config.sh_client_id = os.getenv("SH_CLIENT_ID", "")
        self.config.sh_client_secret = os.getenv("SH_CLIENT_SECRET", "")

        if self.config.sh_client_id == "" or self.config.sh_client_secret == "":
            raise RuntimeError("Hiányzó Sentinel Hub hitelesítési adatok!")
    
    def getBands(self, bands: list[str] = ["B01","B02","B03","B04","B05","B06","B07", "B08","B8A","B09","B10","B11","B12"]) -> list[str]:
        return bands
    
    def getSample(self) -> str:
        return ", ".join([f"sample.{b}" for b in self.getBands()])

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
            input_data=[SentinelHubRequest.input_data(DataCollection.SENTINEL2_L1C)],
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