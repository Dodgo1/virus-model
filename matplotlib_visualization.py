from main import CovidModel

a = CovidModel(
    agent_move_distance=2,
    agents_count=1000,
    map_torus=True,
    map_size=(100,100),
    recovery_time=3,
    illness_range=2,
    contracting_probability=1,
    incubation_time=2,
    number_of_vaccinated=0,
    death_probability=0.3
)

a.display_map_plot()

