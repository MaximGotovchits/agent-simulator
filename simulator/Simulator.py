import random
import ast


class WorldMap:
    objects = []
    pos_to_last_update_time = {}
    pos_to_state = {}
    agents = []
    current_time = 0
    map_damage_factor = 0.8
    map_damage_threshold = 0.6

    def __init__(self, agents):
        self.agents = agents

    def start_emulation(self):
        whole_time = 20
        total_result = []

        for t in range(whole_time):
            collisions = {}
            positions_to_agents = {}
            agent_num = 1

            if t == 0:
                self.init_world()
            else:
                self.update_world()
            current_record = {}

            for curr_pos in self.pos_to_state:
                current_record[curr_pos] = str(self.pos_to_state[curr_pos])
            total_result.append(current_record)

            for current_agent in self.agents:
                self.update_pos(str(current_agent.get_pos()))
                current_pos = current_agent.do_step()
                print "agent_" + str(agent_num) + " at pos: " + str(current_pos) + " at time: " + str(t)
                if positions_to_agents.has_key(str(current_pos)):
                    if len(positions_to_agents[str(current_pos)]) > 1:
                        collisions[current_pos] = positions_to_agents[str(current_pos)]
                        print "Collision at " + str(current_pos) + " between " + \
                              str(len(positions_to_agents[str(current_pos)])) + " agents"
                agent_num += 1
            self.current_time += 1
        with open('data/result/result', 'a') as result_file: # result_n | n - time
            result_file.write(str(total_result))

        # print str(self.pos_to_state)

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

    def __init__(self, path_to_file):
        self.route = {'speed': [], 'position': []}
        with open(path_to_file, 'r') as agent_data:
            for line in agent_data:
                line_list = line.split(" ")
                if len(line_list) == 3:
                    self.route['position'].append([int(line_list[0]), int(line_list[1])])
                    self.route['speed'].append(float(line_list[2]))
        self.current_pos = self.route['position'][0]

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
    agent1 = Agent("data/agent1")
    agent2 = Agent("data/agent2")

    world = WorldMap([agent1, agent2])
    world.start_emulation()