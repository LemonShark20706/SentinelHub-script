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