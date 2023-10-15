import io
import json
import numpy as np
import pandas as pd

from prediction.markov import MarkovContinous
from .performance import Performance

from pathlib import Path
MAIN_FOLDER = Path(__file__).parent.parent.resolve()

 
def get_IC_through_time_maintenance(maintenance_scenario, time_hoziron=50):

    response = {}
    response['LL_prediction'] = {}
    response['ALG_prediction'] = {}
    
    path = MAIN_FOLDER / 'database/markov.json'
    with open(path, "r") as file:
        thetas = json.load(file)
    
    path = MAIN_FOLDER / 'database/ActionsEffects.json'
    with open(path, "r") as file:
        maintenance_data = json.load(file)
    
    markov_LL = MarkovContinous(3, 1)
    markov_LL.theta = thetas['LL']
    
    markov_ALG = MarkovContinous(3, 1)
    markov_ALG.theta = thetas['ALG']
    
    performance_LL = Performance(markov_LL, extract_indicator('LL', maintenance_data))
    performance_ALG = Performance(markov_ALG, extract_indicator('ALG', maintenance_data))

    response['LL_prediction']['Time'] = list(range(0, time_hoziron + 1))
    response['LL_prediction']['IC'] = list(performance_LL.get_IC_over_time(time_hoziron,
                                                       initial_IC = 1,
                                                       actions_schedule=maintenance_scenario,
                                                       number_of_samples=1000))
    
    response['ALG_prediction']['Time'] = list(range(0, time_hoziron + 1))
    response['ALG_prediction']['IC'] = list(performance_ALG.get_IC_over_time(time_hoziron,
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