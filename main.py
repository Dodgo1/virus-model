import random
import matplotlib.pyplot as plt
import mesa
import numpy as np
from matplotlib.animation import FuncAnimation

HEALTH_STATUSES = ["healthy", "developing", "ill", "immune", "dead"]


class CovidModel(mesa.Model):
    """ Main class for the model object """
    agent_move_distance: int
    illness_range: int
    contracting_probability: float  # from 0.0 to 1.0
    incubation_time: int
    recovery_time: int
    death_probability: float  # from 0.0 to 1.0
    # --------------------------------
    agents_count: int
    map_size: tuple
    map_torus: bool
    grid: mesa.space.MultiGrid

    @staticmethod
    def get_random_cell(map_size):
        """ Simple util function to get a random cell from a grid """
        return random.choice(range(map_size[0])), random.choice(range(map_size[1]))

    def get_random_agent(self):
        """ Simple util function to get a random agent from a scheduler """
        return random.choice(self.schedule.agents)

    def get_average_distance_between_agents(self):
        """ Method called by the Datacollector for getting average number of cells between agents on the grid,
        needed for graphs,exporting data, etc."""
        if len(self.schedule.agents) < 2:
            return 0
        distances = []
        for agent in self.schedule.agents:
            distances.append(agent.get_closest_neighbour_distance())
        return sum(distances) / len(distances)

    def get_average_number_of_infected(self):
        """ Method called by the Datacollector for getting average number of agents infected by one sick agent,
        needed for graphs,exporting data, etc."""
        infected_counters = [agent.infected_counter for agent in self.schedule.agents if
                             agent.health_status == HEALTH_STATUSES[2]]
        if len(infected_counters) == 0:
            return 0
        return sum(infected_counters) / len(infected_counters)

    def get_number_of_infected(self):
        """ Method called by the Datacollector for getting number of agents infected in current step,
        needed for graphs,exporting data, etc."""
        infected_counters = 0
        for agent in self.schedule.agents:
            infected_counters += agent.infected_counter
        return infected_counters

    def get_number_of_ill(self):
        """ Method called by the Datacollector for getting current number of ill and developing agents on the grid,
        needed for graphs,exporting data, etc."""
        ill_counter = 0
        for agent in self.schedule.agents:
            if agent.health_status not in [HEALTH_STATUSES[1], HEALTH_STATUSES[2]]:
                continue
            ill_counter += 1
        return ill_counter

    def estimate_average_number_of_infected(self):
        """ Method called by the Datacollector estimating r0 - basic reproduction number of the virus,
        needed for graphs,exporting data, etc."""
        return len(self.grid.get_neighbors(self.get_random_agent().pos, moore=True, include_center=True,
                                           radius=self.illness_range)) * self.contracting_probability

    def __init__(self,
                 agent_move_distance: int,
                 illness_range: int,
                 contracting_probability: float,  # from 0.0 to 1.0
                 incubation_time: int,
                 recovery_time: int,
                 death_probability: float,  # from 0.0 to 1.0
                 # --------------------------------
                 agents_count: int,
                 map_size: tuple,
                 map_torus: bool,
                 number_of_vaccinated:int,
                 ):
        super().__init__()
        self.img = None
        self.agent_move_distance = agent_move_distance * 2
        self.illness_range = illness_range
        self.contracting_probability = contracting_probability
        self.incubation_time = incubation_time
        self.recovery_time = recovery_time
        self.death_probability = death_probability
        # --------------------------------
        self.map_torus = map_torus
        self.agents_count = agents_count
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(*map_size, map_torus)
        self.deaths_counter = 0
        self.map_size = map_size

        for index in range(self.agents_count):  # place agents on the grid
            health_status = HEALTH_STATUSES[0]
            if index < number_of_vaccinated:  # if vaccinated were given, place them first and put rest as healthy
                health_status = HEALTH_STATUSES[3]
            agent = CovidAgent(
                unique_id=index,
                model=self,
                health_status=health_status,
            )
            self.schedule.add(agent)
            self.grid.place_agent(agent, self.get_random_cell(map_size))

        self.datacollector = mesa.DataCollector(
            model_reporters={  # data collector allows for easy data extraction for web visualization
                "population": lambda m: m.schedule.get_agent_count(),
                "deaths_count": lambda m: m.deaths_counter,
                "average_distance": lambda m: m.get_average_distance_between_agents(),
                "number_of_infected": lambda m: m.get_number_of_infected(),
                "average_number_of_infected_by_ill": lambda m: m.get_average_number_of_infected(),
                "number_of_sick": lambda m: m.get_number_of_ill(),
                "estimated_average_number_of_infected": lambda m: m.estimate_average_number_of_infected()
            },
        )

        self.get_random_agent().get_infected() # place one random developing agent

    def step(self):
        """ Main step function of model """
        self.schedule.step()
        self.datacollector.collect(self)

    def get_ndarray(self):
        """ Method for representing grid as numpy ndarray - values correspond to health statuses"""
        arr = np.zeros(shape=self.map_size)
        for agent in self.schedule.agents:
            x, y = agent.pos
            arr[x][y] = HEALTH_STATUSES.index(agent.health_status) + 1  # +1 because 0 is an empty cell
        return arr

    def display_map_plot(self):
        """ Method displaying a matplotlib plot of the model grid, no need for calling steps - does it automatically """
        fig, ax = plt.subplots()
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        self.img = plt.imshow(self.get_ndarray(), cmap="viridis")
        _ = FuncAnimation(fig=fig, func=self._frame, frames=10, interval=30)
        plt.show()

    def _frame(self, _):
        """ Callback private method used in FuncAnimation for updating graph and calling step"""
        self.step()
        return self.img.set(data=self.get_ndarray())


class CovidAgent(mesa.Agent):
    """ Class representing agent of the covid model """

    def __init__(self, unique_id, model: CovidModel, health_status):
        super().__init__(unique_id, model)
        self.id = unique_id
        self.health_status = health_status
        self.incubation_timer = -1  # if -1 means didn't start
        self.recovery_timer = -1  # if -1 means didn't start
        self.model = model
        self.infected_counter = 0

    def get_closest_neighbour_distance(self):
        """ Returns number of cells to a closest neighbour, if there is on in same cell - returns 0 """
        distance = 0
        if self.model.schedule.get_agent_count() == 1:
            return 0
        while True:
            neighbors = self.model.grid.get_neighbors(
                self.pos,
                moore=True,
                include_center=True,
                radius=distance
            )
            if len(neighbors) - 1:  # remove self
                return distance
            distance += 1

    def die(self):
        """ Function used for killing an agent, updates model info and remove agent from grid and scheduler """
        self.health_status = HEALTH_STATUSES[4]
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)
        self.model.deaths_counter += 1

    def step(self):
        """ Step function of agent, takes care of development countdown and recovery countdown.
        Moves the agent on the grid and infects other agents """
        self.infected_counter = 0
        if self.incubation_timer != -1:
            self.incubation_timer -= 1

        if self.incubation_timer == -1 and self.health_status == HEALTH_STATUSES[1]:
            # end_developing(),start_recovery()
            self.recovery_timer = self.model.recovery_time
            self.health_status = HEALTH_STATUSES[2]

        if self.recovery_timer != -1:
            self.recovery_timer -= 1

        if self.recovery_timer == -1 and self.health_status == HEALTH_STATUSES[2]:  # end_recovery()
            if random.random() < self.model.death_probability:
                self.die()
            else:
                self.health_status = HEALTH_STATUSES[3]  # get_immunity()

        if HEALTH_STATUSES.index(self.health_status) < 2 or self.health_status == HEALTH_STATUSES[3]:
            self.move()

        if self.health_status == HEALTH_STATUSES[2]:
            self.infect()

    def move(self):
        """ Function used for moving the agent on the grid, uses variables defined in model """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=self.model.map_torus,
            radius=self.model.agent_move_distance
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def get_infected(self):
        """ Function which begins the process of incubation, later handled in step """
        self.health_status = HEALTH_STATUSES[1]
        self.incubation_timer = self.model.incubation_time

    def infect(self):
        """ Called in step(), infects other agents in range specified in model """
        neighbours = self.model.grid.get_neighbors(
            self.pos,
            moore=self.model.map_torus,
            radius=self.model.illness_range,
            include_center=True
        )
        for agent in neighbours:
            if agent.health_status != HEALTH_STATUSES[0]:
                return
            if random.random() < self.model.contracting_probability:
                agent.get_infected()
                self.infected_counter += 1
