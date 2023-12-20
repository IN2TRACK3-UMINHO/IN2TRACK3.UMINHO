import io
import json
import numpy as np
import pandas as pd

from ams.prediction.markov import MarkovContinous
from ams.performance.performance import Performance

from pathlib import Path
MAIN_FOLDER = Path(__file__).parent.parent.resolve()

 
def get_IC_through_time_maintenance(maintenance_scenario, time_hoziron=50):
    path = MAIN_FOLDER / 'database/markov.json'
    with open(path, "r") as file:
        indicators = json.load(file)
    
    path = MAIN_FOLDER / 'database/ActionsEffects.json'
    with open(path, "r") as file:
        maintenance_data = json.load(file)
    
    response = {}
    
    for indicator in indicators:
        response[indicator] = {}
    
        markov_indicator = MarkovContinous(3, 1)
        markov_indicator.theta = indicators[indicator]['theta']

        performance_indicator = Performance(markov_indicator, 
                                            extract_indicator(indicator, maintenance_data))

        response[indicator]['Time'] = list(range(0, time_hoziron + 1))
        response[indicator]['IC'] = list(performance_indicator.get_IC_over_time(time_hoziron,
                                                           initial_IC = 1,
                                                           actions_schedule=maintenance_scenario,
                                                           number_of_samples=1000))

    return response

def extract_indicator(indicator, actions):
    final_data = []

    for data in actions:
        # Extract the indicator if it exists
        pi_data = data.get(indicator)
        if pi_data is None:
            continue
        
        # Create the new dictionary with the desired structure
        extracted_data = {
            "name": data.get("name"),
        }
        
        if "time_of_reduction" in pi_data:
            extracted_data["time_of_reduction"] = pi_data["time_of_reduction"]
        
        if "reduction_rate" in pi_data:
            extracted_data["reduction_rate"] = pi_data["reduction_rate"]
        
        if "improvement" in pi_data:
            extracted_data["improvement"] = pi_data["improvement"]
        
        extracted_data["cost"] = data.get("cost")
        
        final_data.append(extracted_data)
    return final_data