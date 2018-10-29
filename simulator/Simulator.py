import csv
import random

class Agent:
    light_tp = .5
    light_fp = .5

    sign_tp = .5
    sign_fp = .5

    path = None  # [0, 1, 2, 3, 4, 5, ..., N]

    route = None  # [0, 1, 2, 1, 0, ..., N, ..., N]

    objects = None

    def __init__(self):
        pass

    def set_model(self, light, sign):
        self.light_tp = light
        self.light_fp = 1. - light

        self.sign_tp = sign
        self.sign_fp = 1. - sign

    def set_path(self, input_path):
        self.path = input_path

    def get_path(self):
        return self.path

    def set_route(self, input_route):
        self.route = input_route

    def get_route(self):
        return self.route

    def set_objects(self, objects):
        self.objects = objects

    def get_probability(self, object_name):
        if "Sign" in object_name:
            if random.randint(0, 10)/10. < self.sign_tp:
                return 1.
            else:
                return 0.
        if "Light" in object_name:
            if random.randint(0, 10)/10. < self.light_tp:
                return 1.
            else:
                return 0.
        pass

    def run(self):
        if self.path is None or self.route is None or self.objects is None:
            return None
        result = {}
        for current_step in self.route:
            current_step = int(current_step)
            if self.objects[current_step] in result:
                result[self.objects[current_step]] += self.get_probability(self.objects[current_step])
            else:
                result[self.objects[current_step]] = self.get_probability(self.objects[current_step])
        # for object_name in result.keys():
        #     result[object_name] = result[object_name] /
        return result


def get_objects_and_probabilities(data):
    pass


def get_data_from_route_file(path_to_route):
    output_path = range(26)
    return output_path


def get_objects_from_file(path_to_file):
    with open(path_to_file, 'r') as csvfile:
        data_reader = list(csv.reader(csvfile, delimiter=',', quotechar='"'))
        result = {i[0]: map(str, i[1:]) for i in zip(*data_reader) if i[0] in ('Number', 'Name')}
    return result


def run_simulation(path_to_route):
    objects_and_order = get_objects_from_file(path_to_route)

    # input_data = get_data_from_route_file(path_to_route)
    forward_agent = Agent()
    forward_agent.set_path(objects_and_order['Number'])
    forward_agent.set_route(objects_and_order['Number'])
    forward_agent.set_objects(objects_and_order['Name'])

    backward_agent = Agent()
    backward_agent.set_path(objects_and_order['Number'])
    backward_agent.set_route(objects_and_order['Number'][::-1])
    backward_agent.set_objects(objects_and_order['Name'])

    first_result = forward_agent.run()
    second_result = backward_agent.run()

    result = {}

    for object_name in first_result.keys():
        result[object_name] = (first_result[object_name] + second_result[object_name]) / 2.
    # print get_objects_and_probabilities(input_data)
    return result


if __name__ == "__main__":
    print run_simulation("data/Route.csv")