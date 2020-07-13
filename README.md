# sumo-simulation
## Installation
  Import the desired scenario to the scenario folder
  Then
```
    virtualenv sumo_env
    source sumo_env/bin/activate
    pip install -r requirements.txt
    python setup.py build
    python setup.py install 
    pip install -e .
```
## Usage
```
  python src/run.py --nogui
```
