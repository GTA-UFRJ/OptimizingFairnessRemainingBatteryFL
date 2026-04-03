import pickle
import os
from matplotlib import pyplot as plt
from matplotlib import patches 

def get_square(x,y,color):     
    x_left = x[0] - x[1]
    x_right = x[0] + x[1]
    y_bottom = y[0] - y[1]
    y_top = y[0] + y[1]
    print(x_left,x_right,y_bottom,y_top)
    rect = patches.Rectangle(
        xy=[x_left,y_bottom], 
        width=x_right-x_left,
        height=y_top-y_bottom,
        linewidth=1, 
        edgecolor=color,
        facecolor=color)
    lims = {
        "xmin":x_left,
        "xmax":x_right,
        "ymin":y_bottom,
        "ymax":y_top,
    }
    return rect, lims

def plot_squares(scenario_params:dict,lims, path_to_save):
    plt.style.use('guiaraujo.mplstyle')
    plt.tight_layout()
    fig, ax = plt.subplots(figsize=(12,9))
    for params in scenario_params.values():
        if params.get("square"):
            params["square"].set_label(params["name"])
            ax.add_patch(params["square"])
    ax.set_xlim(lims["xmin"]-(lims["xmax"]-lims["xmin"])/4,
                lims["xmax"]+(lims["xmax"]-lims["xmin"])/4)
    ax.set_ylim(lims["ymin"]-(lims["ymax"]-lims["ymin"])/4,
                lims["ymax"]+(lims["ymax"]-lims["ymin"])/4)
    #ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("Acurácia de teste do modelo global")
    ax.set_ylabel("Desvio padrão do nível de energia")
    ax.legend(loc="upper right")
    #ax.set_title("")
    #plt.show()
    plt.savefig(path_to_save, dpi=300, format='png')
    plt.close

if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    
    with open(os.path.join(my_dir,"processed/results.pkl"),'rb') as f:
        d = pickle.load(f)

    scenario_params = {
        "fixed_50_variable_0": {
            "name": "k=1 (50 épocas fixas)",
            "color": "red",
            "square": None,
        },
        #"fixed_25_variable_25": {
        #    "name": "k=0,5 (25 épocas fixas)",
        #    "color": "green",
        #    "square": None,
        #},
        "fixed_0_variable_50": {
            "name": "k=0 (0 épocas fixas)",
            "color": "blue",
            "square": None,
        },
    }

    lims = {
        "xmin":1e9,
        "xmax":0,
        "ymin":1e9,
        "ymax":0
    }
    for scenario, info in d.items():
        scenario_params[scenario]["square"], l = get_square(
            x=info["accuracy"], 
            y=info["fairness"], 
            color=scenario_params[scenario]["color"])
        if l["xmin"] < lims["xmin"] : lims["xmin"] = l["xmin"]
        if l["xmax"] > lims["xmax"] : lims["xmax"] = l["xmax"]
        if l["ymin"] < lims["ymin"] : lims["ymin"] = l["ymin"]
        if l["ymax"] > lims["ymax"] : lims["ymax"] = l["ymax"]

    plot_squares(scenario_params,lims, os.path.join(my_dir,"figures/acc_x_fairness.png"))