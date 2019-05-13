import random
import csv

class WorldMap:
    objects = []
    pos_to_last_update_time = {}
    pos_to_state = {}
    agents = []
    current_time = 0
    map_damage_factor = 0.8
    map_damage_threshold = 0.6

    cell_amnt_x = 0
    cell_amnt_y = 0

    cell_size_x = 0
    cell_size_y = 0

    x_min = 0
    y_min = 0

    def __init__(self, agents, cell_num_x, cell_num_y):
        self.agents = agents
        self.cell_amnt_x = cell_num_x
        self.cell_amnt_y = cell_num_y
        self.set_cell_size()

    def set_cell_size(self):
        max_x = max(map(float, self.agents[0].get_route()['x_gm']))
        min_x = min(map(float, self.agents[0].get_route()['x_gm']))

        max_y = max(map(float, self.agents[0].get_route()['y_gm']))
        min_y = min(map(float, self.agents[0].get_route()['y_gm']))

        self.x_min = min_x
        self.y_min = min_y
        self.cell_size_x = (max_x - min_x) / float(self.cell_amnt_x)
        self.cell_size_y = (max_y - min_y) / float(self.cell_amnt_y)


    def get_cell(self, x, y):
        x -= self.x_min
        y -= self.y_min
        x_to_return = int(x / self.cell_size_x)
        y_to_return = int(y / self.cell_size_y)

        if x % self.cell_size_x == 0 and x_to_return != 0:
            x_to_return -= 1

        if y % self.cell_size_y == 0 and y_to_return != 0:
            y_to_return -= 1

        return [x_to_return, y_to_return]

    def start_emulation(self, discrete_factor): # discrete_factor in milliseconds
        whole_time = len(self.agents[0].get_route()['id'])
        total_result = []

        agentRoute = self.agents[0].get_route()
        t_last = None
        coords_to_vehicle_ids = {}
        for t in range(whole_time):
            if t == 0:
                t_last = int(agentRoute['msec'][t])
            if int(agentRoute['msec'][t]) - t_last > discrete_factor or t == whole_time - 1:
                # UPDATE_MAP_HERE
                # Get total number of cars SO it's not local but global density. But local density intuitively seems to be more useful.
                total_cars_num = float(len(set(agentRoute['id'])))
                current_result_to_add = {}
                for cur_cell in coords_to_vehicle_ids.keys():
                    current_result_to_add[cur_cell] = str(float(len(set(coords_to_vehicle_ids[cur_cell])) / total_cars_num))
                # add missing cells:
                for x in range(self.cell_amnt_x):
                    for y in range(self.cell_amnt_y):
                        if not current_result_to_add.has_key(str([x, y])):
                            current_result_to_add[str([x, y])] = str(0.)
                total_result.append(current_result_to_add)
                t_last = int(agentRoute['msec'][t])
                coords_to_vehicle_ids = {}

            # Logic goes here:

            if agentRoute['type'][t] == 'Vehicle': # a car is found!
                current_cell = str(self.get_cell(float(agentRoute['x_gm'][t]), float(agentRoute['y_gm'][t]))) # get cell where this car is located
                if coords_to_vehicle_ids.has_key(current_cell): # Add this car to vehicle list of current cell if it was not there before
                    if agentRoute['id'][t] not in coords_to_vehicle_ids[current_cell]:
                        coords_to_vehicle_ids[current_cell] = [agentRoute['id'][t]]
                    else:
                        coords_to_vehicle_ids[current_cell].append(agentRoute['id'][t])
                else:
                    coords_to_vehicle_ids[current_cell] = [agentRoute['id'][t]]

        with open('data/result/resultRealData', 'a') as result_file: # result_n | n - time
            result_file.write(str(total_result))


    def init_world(self):
        for x in range(10):
            for y in range(10):
                self.pos_to_state[str([x, y])] = 0.5

    def update_world(self):
        for current_pos in self.pos_to_state.keys():
            self.pos_to_state[current_pos] = round(self.pos_to_state[current_pos] * 0.9, 4)

    def update_pos(self, pos):
        self.pos_to_state[pos] = round(1. - self.pos_to_state[pos] * 0.9, 4)


class Agent:
    step_complete = 0.
    light_tp = .5
    light_fp = .5

    sign_tp_prob = .5
    sign_fp_prob = .5

    route = None

    current_step = 0

    current_pos = None

    important_cols = ['msec', 'id', 'x_gm', 'y_gm', 'v', 'time_alive', 'type']

    def __init__(self, path_to_file):
        self.route = {}
        for col in self.important_cols:
            self.route[col] = []
        ind_to_col = {}
        with open(path_to_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            isHeader = True
            for line in tsvreader:
                cur_ind = 0
                if isHeader:
                    isHeader = False
                    for head in line[:len(line)/2 + 1]:
                        if head != '':
                            ind_to_col[cur_ind] = head
                            self.route[head] = []
                            cur_ind += 1
                else:
                    for val in line:
                        if ind_to_col.has_key(cur_ind):
                            col_name = ind_to_col[cur_ind]
                            if col_name in self.important_cols:
                                self.route[col_name].append(val)
                        cur_ind += 1


    def get_pos(self):
        return self.current_pos

    def get_observation(self, t):
        1 - pow(1 - self.light_fp, t)
        1 - pow(1 - self.sign_fp_prob, t)

    def set_model(self, light, sign):
        self.light_tp = light
        self.light_fp = 1. - light

        self.sign_tp_prob = sign
        self.sign_fp_prob = 1. - sign

    def set_route(self, input_route):
        self.route = input_route

    def get_route(self):
        return self.route

    def get_probability(self, object_name):
        if "Sign" in object_name:
            if random.randint(0, 10)/10. < self.sign_tp_prob:
                return 1.
            else:
                return 0.
        if "Light" in object_name:
            if random.randint(0, 10)/10. < self.light_tp:
                return 1.
            else:
                return 0.
        pass

    def do_step(self):
        self.current_step %= len(self.route['position'])
        self.step_complete += self.route['speed'][self.current_step]
        if self.step_complete >= 1:
            self.step_complete = 0.
            self.current_step += 1
        self.current_step %= len(self.route['position'])
        self.current_pos = self.route['position'][self.current_step]
        return self.route['position'][self.current_step]


if __name__ == "__main__":
    agent1 = Agent("data/input/2/trm.105.002.ro.tsv")
    # agent2 = Agent("data/input/2/trm.105.002.ro.tsv")

    world = WorldMap([agent1], 10, 10)
    world.start_emulation(10)