from __future__ import absolute_import
from __future__ import print_function

from pathlib import Path
import math
import logging
from datetime import datetime
import optparse

EARTH_RADIUS = 6371

LOGGER = logging.getLogger(__name__)

SRC_DIR = Path(__file__).parent.resolve()
DATA_DIR = SRC_DIR / Path("data")
LOG_DIR = SRC_DIR / Path("logs")
SIM_DIR = SRC_DIR / Path("scenario")

MIN_SIMULATION_STEPS = 10000

def _setup_logger(log_level: int) -> None:
    """
    Setting up logger such that a console handler forwards log statements to
    the console which match LOG_LEVEL (CL argument) and file handler which logs
    all messages independent of their log level.
    """
    logger = logging.getLogger(__package__)
    console_handler = logging.StreamHandler()
    date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    log_path = LOG_DIR / Path(f"{date}.log")
    if not log_path.parent.exists():
        log_path.parent.mkdir(parents=True)
    file_handler = logging.FileHandler(str(log_path))

    # set the log level of the LOGGER to debug such that no messages are discarded
    logger.setLevel(logging.DEBUG)
    # what is print in the console should match the level specified by -v{v}
    console_handler.setLevel(log_level)
    # in the file we want all log messages again
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s- %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

#Parameters two points in radians
#Return the distance between the two points in meters)
def distance(lat_1, lon_1, lat_2, lon_2):
    lat1 = math.radians(lat_1)
    lat2 = math.radians(lat_2)
    lon1 = math.radians(lon_1)
    lon2 = math.radians(lon_2)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    sin_lat = math.sin(delta_lat / 2)
    sin_lon = math.sin(delta_lon / 2)
    a = sin_lat * sin_lat + math.cos(lat1)*math.cos(lat2) * sin_lon * sin_lon
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = EARTH_RADIUS * c
    d = 1000 * d
    return d
