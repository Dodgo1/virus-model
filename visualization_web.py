import mesa
import main

COLORS = ["grey", "red", "pink", "green", "#c4c03b", "#c4423b"]
DATACOLLECTOR = "datacollector"


def agent_portrayal(agent: main.CovidAgent):
    style = {
        "Shape": "circle",
        "xAlign": 0.5,
        "yAlign": 0.5,
        "Filled": "true",
        "Layer": 0,
        "r": 1,
        "id": agent.id,
        "health_status": agent.health_status

    }
    if agent.health_status == main.HEALTH_STATUSES[2]:
        style["Color"] = COLORS[1]
        return style
    if agent.health_status == main.HEALTH_STATUSES[1]:
        style["Color"] = COLORS[2]
        return style
    if agent.health_status == main.HEALTH_STATUSES[3]:
        style["Color"] = COLORS[3]
        return style
    style["Color"] = COLORS[0]
    return style


model_params = {
    "map_size": (100, 100),
    "agent_move_distance": mesa.visualization.Slider(
        value=2,
        name="agents_move_distance",
        min_value=1,
        max_value=10,
        step=1,
    ),
    "illness_range": mesa.visualization.Slider(
        value=2,
        name="illness_range",
        min_value=1,
        max_value=10,
        step=1,
    ),
    "contracting_probability": mesa.visualization.Slider(
        value=0.5,
        name="contracting_probability",
        min_value=0.,
        max_value=1.,
        step=0.01,
    ),
    "incubation_time": mesa.visualization.Slider(
        value=2,
        name="incubation_time",
        min_value=1,
        max_value=10,
        step=1,
    ),
    "recovery_time": mesa.visualization.Slider(
        value=2,
        name="recovery_time",
        min_value=1,
        max_value=10,
        step=1,
    ),
    "death_probability": mesa.visualization.Slider(
        value=0.5,
        name="death_probability",
        min_value=0.,
        max_value=1.,
        step=0.01,
    ),
    "number_of_vaccinated": mesa.visualization.NumberInput(
        value=0,
        name="number_of_vaccinated",
    ),
    "agents_count": mesa.visualization.NumberInput(
        value=100,
        name="agents_count",
    ),
    "map_torus": mesa.visualization.Checkbox(
        name="map_torus",
        value=True
    )
}

grid = mesa.visualization.CanvasGrid(agent_portrayal, *model_params["map_size"], 1000, 1000)
chart1 = mesa.visualization.ChartModule(
    [{
        "Label": "population",
        "Color": "Red",
        "label": "population",
        "borderColor": "rgb(75, 192, 0)"
    }, {
        "Label": "deaths_count",
        "Color": "Red",
        "label": "deaths_count",
        "borderColor": "#000000"
    }, {
        "Label": "number_of_sick",
        "Color": "Red",
        "label": "number_of_sick",
        "borderColor": "#ff0000"
    }
    ],
    data_collector_name=DATACOLLECTOR
)
chart2 = mesa.visualization.ChartModule(
    [{
        "Label": "average_distance",
        "Color": "Red",
        "label": "average_distance",
        "borderColor": "#0000ff"
    }],
    data_collector_name=DATACOLLECTOR
)
chart3 = mesa.visualization.ChartModule(
    [{
        "Label": "average_number_of_infected_by_ill",
        "Color": "Red",
        "label": "average_number_of_infected_by_ill",
        "borderColor": "#00ff00"
    }, {
        "Label": "estimated_average_number_of_infected",
        "Color": "Red",
        "label": "estimated_average_number_of_infected",
        "borderColor": "#055000"
    }],
    data_collector_name=DATACOLLECTOR
)
chart4 = mesa.visualization.ChartModule(
    [{
        "Label": "number_of_infected",
        "Color": "Red",
        "label": "number_of_infected",
        "borderColor": "#000ff0"
    }],
    data_collector_name=DATACOLLECTOR
)

server = mesa.visualization.ModularServer(
    main.CovidModel, [grid, chart1, chart2, chart3, chart4], "Covid Model", model_params=model_params
)

server.port = 8080
server.launch(open_browser=False)
