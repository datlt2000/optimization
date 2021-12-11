import random
from copy import deepcopy


class HillClimbing(object):

    def __init__(self, problem, type='greedy'):
        self.problem = problem
        self.type = type
        self.problem_solver(problem.initial_state())

    def problem_solver(self, initial_state):
        number_of_expanded_nodes = 0
        number_of_visited_nodes = 0
        best_state_found = False
        current_state = initial_state
        last_state = initial_state
        number_of_attempts = 5
        attempts = 0
        while not best_state_found:
            number_of_expanded_nodes = number_of_expanded_nodes + 1
            neighbors = self.problem.successor(current_state)
            number_of_visited_nodes = number_of_visited_nodes + len(neighbors)
            if self.type == 'greedy':
                current_state = self.find_neighbor_in_greedy_way(current_state, neighbors)
                best_state_found = True if last_state == current_state else False
            elif self.type == 'stochastic':
                current_state = self.find_neighbor_in_stochastic_way(current_state, neighbors)
                best_state_found = True if last_state == current_state else False
            elif self.type == 'random_restart':
                current_state = self.find_neighbor_in_greedy_way(current_state, neighbors)
                if last_state == current_state:
                    if attempts < number_of_attempts:
                        best_state_found = True
                    attempts = attempts + 1
            elif self.type == 'first_choice':
                current_state = self.find_neighbor_in_first_choice_way(current_state, neighbors)
                best_state_found = True if last_state == current_state else False
            if self.problem.heuristic(current_state) == 0:
                best_state_found = True
            last_state = current_state
        print("Type of hill climbing: " + str(self.type))
        print("Last state: " + str(current_state))
        print("Number of visited nodes: " + str(number_of_visited_nodes))
        print("Number of expanded nodes: " + str(number_of_expanded_nodes))

    def find_neighbor_in_greedy_way(self, current_state, neighbors):
        best_neighbor = current_state
        best_heuristic = self.problem.heuristic(current_state)
        for neighbor in neighbors:
            heuristic = self.problem.heuristic(neighbor)
            if heuristic < best_heuristic:
                best_heuristic = heuristic
                best_neighbor = neighbor
        return best_neighbor

    def find_neighbor_in_stochastic_way(self, current_state, neighbors):
        valuable_neighbors = []
        for neighbor in neighbors:
            if self.problem.heuristic(neighbor) < self.problem.heuristic(current_state):
                valuable_neighbors.append(neighbor)
        return random.choice(valuable_neighbors) if len(valuable_neighbors) > 0 else current_state

    def find_neighbor_in_first_choice_way(self, current_state, neighbors):
        best_heuristic = self.problem.heuristic(current_state)
        for neighbor in neighbors:
            heuristic = self.problem.heuristic(neighbor)
            if heuristic < best_heuristic:
                return neighbor
        return current_state


class Problem(object):

    def __init__(self, graph, number_of_colors=3):
        self.graph = graph
        self.number_of_colors = number_of_colors

    def initial_state(self):
        node_colors = {}
        for g in self.graph:
            node_colors[g] = 1
        return node_colors

    def heuristic(self, node_colors):
        score = 0
        all_neighbors = self.find_all_neighbors()
        for i in all_neighbors:
            if node_colors[i[0]] == node_colors[i[1]]:
                score = score + 1
        return score

    def successor(self, current_state):
        all_neighbors = self.find_all_neighbors()
        num_of_neighbors = {}
        neighbors = []
        for i in current_state:
            num_of_neighbors[i] = 0
        for neighbor in all_neighbors:
            if current_state[neighbor[0]] == current_state[neighbor[1]]:
                num_of_neighbors[neighbor[0]] = num_of_neighbors[neighbor[0]] + 1
                num_of_neighbors[neighbor[1]] = num_of_neighbors[neighbor[1]] + 1
        worst_node = max(num_of_neighbors, key=num_of_neighbors.get)
        for i in range(1, self.number_of_colors + 1):
            temp_state = deepcopy(current_state)
            if temp_state[worst_node] != i:
                temp_state[worst_node] = i
                neighbors.append(temp_state)
        return neighbors

    def find_all_neighbors(self):
        all_neighbors = []
        for i in self.graph:
            for j in graph[i]:
                all_neighbors.append((i, j))
        return all_neighbors


def read_data(file_path='../data/graphColoring.txt'):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    v = set()
    pp, ee, num_node, num_edge = lines[5].split(' ')
    edge = dict()
    for i in range(1, int(num_node) + 1):
        edge[i] = []
    for line in lines[6:]:
        e, i, j = line.split(' ')
        if e == 'e':
            v.add(int(i))
            v.add(int(j))
            edge[int(i)].append(int(j))
    return edge


if __name__ == '__main__':
    # file_path = '../data/graphColoring.txt'
    file_path = input("file path: ")
    graph = read_data(file_path)
    # num_color = 3
    num_color = int(input("how many color: "))
    p = Problem(graph, num_color)
    hc = HillClimbing(p, 'first_choice')
