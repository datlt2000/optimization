from ortools.sat.python import cp_model


class ShortestPathPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, edges, nodes, num_node, limit, start, end):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._start = start
        self._end = end
        self._nodes = nodes
        self._num_node = num_node
        self._solution_count = 0
        self._solution_limit = limit
        self.edges = edges

    def on_solution_callback(self):
        self._solution_count += 1
        print('Solution %i' % self._solution_count)
        cost = 0
        edges_list = list()
        edges_dict = dict()
        for (i, j) in self.edges:
            if self.Value(self._nodes[(i, j)]) == 1:
                edges_dict[i] = (j, self.edges[(i, j)])

        u = self._start
        s = 'Path: ' + str(u + 1)
        while u != self._end:
            v, c = edges_dict[u]
            cost += c
            edges_list.append("\t%3d -> %3d: %6.3f" % (u + 1, v + 1, c))
            u = v
            s += ' -> ' + str(u + 1)
        print(s)
        print("cost: %i" %cost)
        print("Edges:")
        for e in edges_list:
            print(e)
        print("_________________________________________________\n")

        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


class ShortestPath:
    def __init__(self, edges=None, v=None, start=1, end=1, solution_limit=5):
        self.start = start
        self.end = end
        self.num_node = len(v)
        self.edges = edges
        self.all_node = v
        self.nodes_var = {}  # IntVar: var in solver
        self.solver = None
        self.model = None
        self.objective = None
        self.solution_printer = None
        self.solution_limit = solution_limit

    def create_model(self):
        self.model = cp_model.CpModel()

    def create_var(self):
        # Creates variables.
        for (s, t) in self.edges:
            self.nodes_var[(s, t)] = self.model.NewIntVar(0, 1, 'Edge_From_%i_To_%i' % (s, t))
        for i in range(self.num_node):
            self.nodes_var[i] = self.model.NewIntVar(0, self.num_node, "y[%i]" % i)

    def add_constrain(self):
        for i in range(self.num_node):
            if i == self.start:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) == 1)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 0)
            elif i == self.end:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) == 0)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 1)
            else:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) - sum(
                    self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) == 0)
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node) if (i, j) in self.edges) <= 1)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node) if (j, i) in self.edges) <= 1)

        for (s, t) in self.edges:
            self.model.Add(self.nodes_var[t] - self.nodes_var[s] - self.nodes_var[(s, t)] >= 0)

    def create_solver(self):
        # Creates the solver.
        self.solver = cp_model.CpSolver()

    def solve(self):
        self.create_model()
        self.create_var()
        self.add_constrain()
        self.create_solver()
        self.solver.parameters.linearization_level = 0
        # Enumerate all solutions.
        self.solver.parameters.enumerate_all_solutions = True
        # Display the first five solutions.
        self.solution_printer = ShortestPathPartialSolutionPrinter(self.edges, self.nodes_var, self.num_node,
                                                                   self.solution_limit, self.start, self.end)

        self.solver.Solve(self.model, self.solution_printer)
        self.print_result()

    def print_result(self):
        # Statistics.
        print('\nStatistics')
        print('  - conflicts      : %i' % self.solver.NumConflicts())
        print('  - branches       : %i' % self.solver.NumBranches())
        print('  - wall time      : %f s' % self.solver.WallTime())
        print('  - solutions found: %i' % self.solution_printer.solution_count())


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
