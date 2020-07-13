from __future__ import absolute_import
from __future__ import print_function

import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import pandas as pd

import traci

from src.utils import (
    DATA_DIR,
    SIM_DIR,
    MIN_SIMULATION_STEPS
)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

LOGGER = logging.getLogger(__name__)

class Stat:
    def __init__(self, model:str, binary, network:str):
        self.simulation_finished = False
        self.simulation_started = False
        self.model = SIM_DIR/Path(model)
        self.sumoBinary = binary
        self.network = DATA_DIR/Path(network)

        self.set_outpath("stat")
        self.registered = set()
        self.results = pd.DataFrame({"Step":[]})

        self.step = 0

    def start(self):
        traci.start([self.sumoBinary, "-c", str(self.model), "--tripinfo-output", str(self.network)])
        self.simulation_started = True

    def stop(self):
        LOGGER.debug("Stopping SUMO simulation")
        traci.close(False)
        sys.stdout.flush()

    def run(self):
        self.start()
        assert self.simulation_started
        while traci.simulation.getMinExpectedNumber() > 0 and not self.simulation_finished:
            traci.simulationStep()
            step_results = self.get_data()
            self.results = self.results.append(step_results, ignore_index=True)
            self.step += 1
        self.stop()
        self._save_data()

    def get_data(self):
        assert self.simulation_started

    def set_outpath(self, outpath:str):
        date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        self.outpath = DATA_DIR/Path(f"{date}-{outpath}-results.csv")

    def _save_data(self):
        LOGGER.debug(f"Saving data to {self.outpath}")
        self.results.to_csv(self.outpath, index=False)

class SubscriptionStat(Stat):
    def __init__(self, model:str, binary, network:str):
        super().__init__(model, binary, network)

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
    def __init__(self, model:str, binary, network:str):
        super().__init__(model, binary, network)
        self.results = pd.DataFrame({"Step":[], "ID":[], "Type":[], "Latitude":[], "Longitude":[]})
        self.set_outpath("all_coordinates_results")

    def get_data(self):
        super().get_data()

        all_vehicles = set(traci.vehicle.getIDList())
        step_results = pd.DataFrame({"Step":[], "ID":[], "Type":[], "Latitude":[], "Longitude":[]})
        if not all_vehicles:
            if self.step > MIN_SIMULATION_STEPS:
                self.simulation_finished = True
            return []
        for v in all_vehicles:
            type = traci.vehicle.getTypeID(v)
            x, y = traci.vehicle.getPosition(v)
            lon, lat = traci.simulation.convertGeo(x, y)
            step_results = step_results.append(pd.DataFrame({"Step": [traci.simulation.getTime()], "ID": [v],
                                              "Type": [type], "Latitude": [lat], "Longitude": [lon]}), ignore_index=True)
        return step_results

