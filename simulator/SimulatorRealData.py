import csv
import math

def binary_sort(sorted_list, key):
    start = 0
    end = len(sorted_list)
    while start <= end:
        mid = int((start + end) / 2)
        if key == sorted_list[mid]:
            print("\nEntered number %d is present at position: %d" % (key, mid))
            return -1.
        elif key < sorted_list[mid]:
            end = mid - 1
        elif key > sorted_list[mid]:
            start = mid + 1
    print("\nElement not found!")
    return -1.

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
        max_x = max(map(float, self.agents[0].get_observation()['x_gm']))
        min_x = min(map(float, self.agents[0].get_observation()['x_gm']))

        max_y = max(map(float, self.agents[0].get_observation()['y_gm']))
        min_y = min(map(float, self.agents[0].get_observation()['y_gm']))

        self.x_min = min_x
        self.y_min = min_y
        self.cell_size_x = (max_x - min_x) / float(self.cell_amnt_x)
        self.cell_size_y = (max_y - min_y) / float(self.cell_amnt_y)

        print "Square size: " + str(self.cell_size_x) + " x " + str(self.cell_size_y)


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


    def get_dst(self, cord1, cord2):
        dst = -1.
        if len(cord1) == len(cord2):
            dst = 0.
            for current_ind in range(len(cord1)):
                dst += pow(cord1[current_ind] - cord2[current_ind], 2)
            dst = math.sqrt(dst)
        return dst


    def get_agent_coord(self, agentRoute, current_time):
        time_index = self.get_nearest_time(agentRoute, current_time)
        return [float(agentRoute['x'][time_index]), float(agentRoute['y'][time_index])]

    def get_nearest_time(self, agent, current_time):
        found_time_index = self.binary_search(agent['grabMsec'], current_time)
        return found_time_index

    def binary_search(self, arr, item, low = 0, high = None):
        if high is None:
            high = len(arr)
        mid = low + (high-low) //2
        if high - low + 1 <= 0 or mid == high:
            return mid
        else:
            guess = long(arr[mid])
            if guess == item:
                return mid
            if item < guess:
                return self.binary_search(arr, item, low, mid)
            else:
                return self.binary_search(arr, item, (mid+1), high)

    def start_emulation(self, discrete_factor): # discrete_factor in milliseconds
        whole_time = len(self.agents[0].get_observation()['id'])
        total_result = []

        agentObservation = self.agents[0].get_observation()

        agentRoute = self.agents[0].getRoute()


        t_last = None
        coords_to_vehicle_ids = {}
        for t in range(whole_time):
            if t == 0:
                t_last = int(agentObservation['msec'][t])
            if int(agentObservation['msec'][t]) - t_last > discrete_factor or t == whole_time - 1:
                # UPDATE_MAP_HERE
                # Get total number of cars SO it's not local but global density. But local density intuitively seems to be more useful.
                # total_cars_num = float(len(set(agentObservation['id'])))
                current_result_to_add = {}
                for cur_cell in coords_to_vehicle_ids.keys():
                    current_result_to_add[cur_cell] = str(1. - float(len(set(coords_to_vehicle_ids[cur_cell])) / 10.))
                # add missing cells:
                # for x in range(self.cell_amnt_x):
                #     for y in range(self.cell_amnt_y):
                #         if not current_result_to_add.has_key(str([x, y])):
                #             current_result_to_add[str([x, y])] = str(1.)
                total_result.append(current_result_to_add)
                t_last = int(agentObservation['msec'][t])
                coords_to_vehicle_ids = {}

            # Logic goes here:

            if agentObservation['type'][t] == 'Vehicle': # a car is found!
                current_observation_coord = [float(agentObservation['x_gm'][t]), float(agentObservation['y_gm'][t])]
                current_agent_coord = self.get_agent_coord(agentRoute, long(agentObservation['msec'][t]))
                if self.get_dst(current_observation_coord, current_agent_coord) < 40.:
                    # print self.get_dst(current_observation_coord, current_agent_coord)
                    current_cell = str(self.get_cell(float(agentObservation['x_gm'][t]), float(agentObservation['y_gm'][t]))) # get cell where this car is located
                    if coords_to_vehicle_ids.has_key(current_cell): # Add this car to vehicle list of current cell if it was not there before
                        if agentObservation['id'][t] not in coords_to_vehicle_ids[current_cell]:
                            coords_to_vehicle_ids[current_cell].append(agentObservation['id'][t])
                        # else:
                        #     coords_to_vehicle_ids[current_cell].append(agentObservation['id'][t])
                    else:
                        coords_to_vehicle_ids[current_cell] = [agentObservation['id'][t]]

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

    observation = None

    route = None

    current_step = 0

    current_pos = None

    ind_to_col_observation = {}

    ind_to_col_route = {}

    important_observation_cols = ['msec', 'id', 'x_gm', 'y_gm', 'v', 'time_alive', 'type']
    important_route_cols = ['grabMsec', 'x', 'y']


    def __init__(self, observations_file, route_file):
        self.observation = {}
        self.route = {}
        for col in self.important_observation_cols:
            self.observation[col] = []
        with open(observations_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            isHeader = True
            for line in tsvreader:
                cur_ind = 0
                if isHeader:
                    isHeader = False
                    for head in line[:len(line)/2 + 1]:
                        if head != '':
                            self.ind_to_col_observation[cur_ind] = head
                            self.observation[head] = []
                            cur_ind += 1
                else:
                    for val in line:
                        if self.ind_to_col_observation.has_key(cur_ind):
                            col_name = self.ind_to_col_observation[cur_ind]
                            if col_name in self.important_observation_cols:
                                self.observation[col_name].append(val)
                        cur_ind += 1

        with open(route_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            current_line = 0
            for line in tsvreader:
                cur_ind = 0
                if current_line == 3:
                    for head in line:
                        if head != '':
                            self.ind_to_col_route[cur_ind] = head
                            self.route[head] = []
                            cur_ind += 1
                if current_line > 3:
                    line = filter(lambda el: el != '', line)
                    for val in line:
                        if self.ind_to_col_route.has_key(cur_ind):
                            col_name = self.ind_to_col_route[cur_ind]
                            if col_name in self.important_route_cols:
                                self.route[col_name].append(val)
                        cur_ind += 1
                current_line += 1

    def addObservation(self, path_to_file): # must NOT content header
        with open(path_to_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            for line in tsvreader:
                cur_ind = 0
                for val in line:
                    if self.ind_to_col_observation.has_key(cur_ind):
                        col_name = self.ind_to_col_observation[cur_ind]
                        if col_name in self.important_observation_cols:
                            self.observation[col_name].append(val)
                    cur_ind += 1

    def addRoute(self, path_to_file):
        with open(path_to_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            current_line = 0
            for line in tsvreader:
                if current_line > 3:
                    line = filter(lambda el: el != '', line)
                    cur_ind = 0
                    for val in line:
                        if self.ind_to_col_route.has_key(cur_ind):
                            col_name = self.ind_to_col_route[cur_ind]
                            if col_name in self.important_route_cols:
                                self.route[col_name].append(val)
                        cur_ind += 1
                current_line += 1

    def get_pos(self):
        return self.current_pos

    # def get_observation(self, t):
    #     1 - pow(1 - self.light_fp, t)
    #     1 - pow(1 - self.sign_fp_prob, t)

    # def set_model(self, light, sign):
    #     self.light_tp = light
    #     self.light_fp = 1. - light
    #
    #     self.sign_tp_prob = sign
    #     self.sign_fp_prob = 1. - sign

    def set_observation(self, input_observation):
        self.observation = input_observation

    def get_observation(self):
        return self.observation

    def getRoute(self):
        return self.route

    # def get_probability(self, object_name):
    #     if "Sign" in object_name:
    #         if random.randint(0, 10)/10. < self.sign_tp_prob:
    #             return 1.
    #         else:
    #             return 0.
    #     if "Light" in object_name:
    #         if random.randint(0, 10)/10. < self.light_tp:
    #             return 1.
    #         else:
    #             return 0.
    #     pass

    # def do_step(self):
    #     self.current_step %= len(self.observation['position'])
    #     self.step_complete += self.observation ['speed'][self.current_step]
    #     if self.step_complete >= 1:
    #         self.step_complete = 0.
    #         self.current_step += 1
    #     self.current_step %= len(self.observation['position'])
    #     self.current_pos = self.observation['position'][self.current_step]
    #     return self.observation['position'][self.current_step]


if __name__ == "__main__":
    agent1 = Agent("data/input/2/trm.105.002.ro.tsv", "data/input/2/trm.105.002.ego.trk.tsv")
    for current_file_num in range(3, 25):
        if current_file_num < 10:
            agent1.addObservation("data/input/trm.105/trm.105.00" + str(current_file_num) + ".ro.tsv")
            agent1.addRoute("data/input/out.trk.loc/trm.105.00" + str(current_file_num) + ".ego.trk.tsv")
        if current_file_num >= 10 and current_file_num < 100:
            agent1.addObservation("data/input/trm.105/trm.105.0" + str(current_file_num) + ".ro.tsv")
            agent1.addRoute("data/input/out.trk.loc/trm.105.0" + str(current_file_num) + ".ego.trk.tsv")
        if current_file_num >= 100:
            agent1.addObservation("data/input/trm.105/trm.105." + str(current_file_num) + ".ro.tsv")
            agent1.addRoute("data/input/out.trk.loc/trm.105." + str(current_file_num) + ".ego.trk.tsv")
    # agent2 = Agent("data/input/2/trm.105.002.ro.tsv")



    world = WorldMap([agent1], 45, 60)
    world.start_emulation(5000)
