from ortools.linear_solver import pywraplp


class ShortestPath:
    def __init__(self, edges=None, v=None, start=1, end=1):
        self.start = start
        self.end = end
        self.num_node = len(v)
        self.edges = edges
        self.all_node = v
        self.nodes_var = {}  # IntVar: var in solver
        self.solver = None
        self.objective = None

    def create_solver(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_var(self):
        # Creates variables.
        for (s, t) in self.edges:
            self.nodes_var[(s, t)] = self.solver.IntVar(0, 1, 'Edge_From_%i_To_%i' % (s, t))
        for i in range(self.num_node):
            self.nodes_var[i] = self.solver.IntVar(0, self.num_node, "y[%i]" % i)

    def add_constrain(self):
        for i in range(self.num_node):
            if i == self.start:
                self.solver.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) == 1)
                self.solver.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 0)
            elif i == self.end:
                self.solver.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) == 0)
                self.solver.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 1)
            else:
                self.solver.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) - sum(
                    self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 0)
                self.solver.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) <= 1)
                self.solver.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) <= 1)

        for (s, t) in self.edges:
            self.solver.Add(self.nodes_var[t] - self.nodes_var[s] - self.nodes_var[(s, t)] >= 0)

    def set_objective(self):
        self.objective = self.solver.Objective()
        for (i, j) in self.edges:
            self.objective.SetCoefficient(self.nodes_var[(i, j)], self.edges[(i, j)])
        self.objective.SetMinimization()

    def solve(self):
        self.create_solver()
        self.create_var()
        self.add_constrain()
        self.set_objective()
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            self.print_result()
        else:
            print("cannot solve")

    def print_result(self):
        # Statistics.
        print("IP solution:")
        print("Cost: %8.3f" % (self.objective.Value()))
        edges_list = list()
        edges_dict = dict()
        for (i, j) in self.edges:
            if self.nodes_var[(i, j)].solution_value() == 1:
                edges_dict[i] = (j, self.edges[(i, j)])

        u = self.start
        s = 'Path: ' + str(u + 1)
        while u != self.end:
            v, c = edges_dict[u]
            edges_list.append("\t%3d -> %3d: %6.3f" % (u + 1, v + 1, c))
            u = v
            s += ' -> ' + str(u + 1)
        print(s)
        print("Edges:")
        for e in edges_list:
            print(e)
        print("_________________________________________________\n")


def read_data(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    data = dict()
    data['V'] = set()
    data['E'] = dict()
    for line in lines[1:]:
        i, j, c = line.split(';')
        data['V'].add(int(i) - 1)
        data['V'].add(int(j) - 1)
        data['E'][int(i) - 1, int(j) - 1] = float(c)
    data['s'] = min(data['V'])
    data['t'] = max(data['V'])
    return data


def main():
    path = "../data/Bai1_25_l_1.txt"
    # path = input("path to file: ")
    data = read_data(path)
    # Creates the solver.
    shortest_path = ShortestPath(edges=data["E"], v=data["V"], start=data["s"], end=data["t"])
    shortest_path.solve()


if __name__ == '__main__':
    main()
