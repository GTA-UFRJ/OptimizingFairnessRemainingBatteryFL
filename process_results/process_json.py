import json
import os
import numpy as np
from utils import print_dict_struct
from scipy import stats
import pickle

def get_avg_and_error(array):
    array = np.array(array)
    return np.mean(array), stats.sem(array) * stats.t.ppf((1+0.95)/2., len(array)-1)  

def process_scenario(scenario_info:dict):
    scenario_results = {
        "acc_history": {},
        "accuracy":[],
        "fairness":[],
    }

    for run_info in scenario_info.values():
        if run_info is None:
            continue
        scenario_results["accuracy"].append(run_info["accuracy"])
        scenario_results["fairness"].append(run_info["fairness"])
        
        for round_index, acc in enumerate(run_info["acc_history"]):    
            if scenario_results["acc_history"].get(round_index) is None:
                scenario_results["acc_history"][round_index] = [acc]
            else:
                scenario_results["acc_history"][round_index].append(acc)

    scenario_results["accuracy"] = get_avg_and_error(scenario_results["accuracy"])
    scenario_results["fairness"] = get_avg_and_error(scenario_results["fairness"])
    scenario_results["acc_history"] = {
        k:get_avg_and_error(v) 
        for k,v in scenario_results["acc_history"].items()
    }

    return scenario_results

if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    
    with open(os.path.join(my_dir,"results.json"),'r') as f:
        d = json.load(f)

    results = {}
    for scenario, scenario_info in d.items():
        results[scenario] = process_scenario(scenario_info)
    print_dict_struct(results)

    with open(os.path.join(my_dir,"results.pkl"),'wb') as f:
        pickle.dump(results,f)
