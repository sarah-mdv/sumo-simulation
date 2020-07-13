# sumo-simulation
* How to run
  - Import the desired scenario to the scenario folder
  - run:
 ```
    virtualenv sumo_env
    source sumo_env/bin/activate
    pip install -r requirements.txt
    python setup.py build
    python setup.py install 
    pip install -e .
    python src/run.py
    ```
