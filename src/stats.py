from __future__ import absolute_import
from __future__ import print_function

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

import pandas as pd

import traci

from src.util import (
    DATA_DIR,
)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

LOGGER = logging.getLogger(__name__)


class Stat:
    def __init__(self, model:str, binary, config:str):
        self.simulation_finished = False
        self.simulation_started = False
        self.model = Path(model)
        self.sumoBinary = binary
        self.config = Path(config)

        date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        self.outpath = DATA_DIR/Path(f"{date}-results.csv")
        self.registered = set()
        self.results = pd.DataFrame({"Step":[]})

    def start(self):
        traci.start([self.sumoBinary, "-c", str(self.model), "--tripinfo-output", str(self.config)])
        self.simulation_started = True

    def stop(self):
        if self.simulation_finished == True:
            traci.close(False)
            sys.stdout.flush()
        else:
            LOGGER.warning("The simulation has not yet terminated, traci cannot be stopped")

    def run(self):
        self.start()
        assert self.simulation_started
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_results = self.getStats()
            self.results.append(step_results)
        self.simulation_finished = True
        self.stop()

    def get_data(self):
        assert self.simulation_started

    def set_outpath(self, outpath:str):
        self.outpath = Path(outpath)

    def _save_data(self):
        self.results.to_csv(self, str(self.outpath), index=False)

class SubscriptionStat(Stat):
    def __init__(self, model:str, binary, config:str):
        super().__init__(model, binary, config)

    def subscribe_cars(self, cars):
        assert self.simulation_started
        LOGGER.debug("Subscribing cars")
        for c in cars:
            traci.vehicle.subscribe(c)

    def get_subscriptions(self, cars):
        assert self.simulation_started
        LOGGER.debug("Getting subscriptions")
        for c in cars:
            traci.vehicle.getSubscriptionResults(c)

class FullCoordStat(Stat):
    def __init__(self, model:str, binary, config:str):
        super().__init__(model, binary, config)
        self.results = pd.DataFrame({"Step":[], "ID":[], "Type":[], "Latitude":[], "Longitude":[]})
        self.outpath = DATA_DIR / Path("all_coordinates_results.csv")

    def get_data(self):
        super().get_data()

        all_vehicles = set(traci.vehicle.getIDList())
        step_results = pd.DataFrame({"Step":[], "ID":[], "Type":[], "Latitude":[], "Longitude":[]})
        for v in all_vehicles:
            type = traci.vehicle.getTypeID(v)
            x, y = traci.vehicle.getPosition(v)
            lon, lat = traci.simulation.convertGeo(x, y)
            step_results.append(pd.DataFrame({"Step": [traci.simulation.getTime()], "ID": [v],
                                              "Type": [type], "Latitude": [lat], "Longitude": [lon]}))
        return step_results




