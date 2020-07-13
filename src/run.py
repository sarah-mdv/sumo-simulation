from __future__ import absolute_import
from __future__ import print_function

import os
import sys

from src.util import(
    get_options,
)

from src.stats import (
    FullCoordStat
)
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    stats = FullCoordStat("MoSTScenario/scenario/most.sumocfg", sumoBinary)

    stats.run()
