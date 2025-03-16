import instrumentation_behaverify as beha
import instrumentation_BT_to_PN as btpn

def behaverify_comparison(parameters):
    results={
        "behaverify":[],
        "PN_tina":[],
        "PN_storm":[],
        "nodes":[]
    }
    sizes=range(parameters["sizes"].min,parameters["sizes"].max,parameters["sizes"].step)
    for i in sizes:
        raw_result=beha.extract_data(i)
        result=raw_result["runtime_verification"]
        results["behaverify"].append(result)

def dineros_composition(parameters):
    pass

def vacuum_cleaner(parameters):
    pass

experiments=[
    {
        "name":"behaverify_comparison",
        "function":behaverify_comparison,
        "parameters":{
            "sizes":{
                "min":10,
                "max":110,
                "step":20
            },
            "seeds":{
                "min":0,
                "max":20
            }
        },
        "model_checkers":["tina","storm","nuxmv"]
    },
    {
        "name":"dineros_composition",
        "function":dineros_composition,
        "parameters":{
            "scenario":("Application/Inputs/go_to_dock_groot.xml","")
        },
        "model_checkers":["tina","storm"]
    },
    {
        "name":"vacuum_cleaner",
        "function":vacuum_cleaner,
        "parameters":{
            "versions":[
                ("Application/Inputs/go_to_dock_groot.xml",""),
                ("Application/Inputs/big_bt_groot.xml","")
            ]
        },
        "model_checkers":["tina","storm"]
    }
]

def main():
    pass

if __name__ == "__main__":
    pass