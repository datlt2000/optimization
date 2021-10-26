"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model


class ShortestPathPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, nodes, num_node, limit, start, end):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._start = start
        self._end = end
        self._nodes = nodes
        self._num_node = num_node
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        print('Solution %i' % self._solution_count)
        i = self._start
        print("start: %i " % i)
        while True:
            if i == self._end:
                break
            for j in range(self._num_node):
                if self.Value(self._nodes[(i, j)]) == 1:
                    print("-> %i" % j)

        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


class ShortestPath:
    def __init__(self, num_node=4, edges=None, solution_limit=5, start=1, end=1):
        self.start = start
        self.end = end
        self.num_node = num_node
        self.matrix = self.convert_edge_to_matrix(num_node, edges)
        self.solution_limit = solution_limit
        self.all_node = range(1, self.num_node + 1)
        self.model = None  # cp_model.CPModel: Model of problem
        self.nodes_var = {}  # cp_model.NewBoolVar: var in model
        self.solver = None  # cp_model.Solver
        self.solution_printer = None  # Call back class return result from solver

    @staticmethod
    def convert_edge_to_matrix(num_node, edges):
        matrix = [[0 for i in range(num_node)] for j in range(num_node)]
        for i in range(edges):
            matrix[edges[0]][edges[1]] = edges[2]
        return matrix

    def create_model(self):
        self.model = cp_model.CpModel()

    def create_var(self):
        # Creates shift variables.
        # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
        for s in self.all_node:
            for t in self.all_node:
                if self.matrix[s][t] == 0:
                    self.nodes_var[(s, t)] = self.model.NewIntVar(0, 0, 'Edge_From_%i_To_%i' % (s, t))
                else:
                    self.nodes_var[(s, t)] = self.model.NewIntVar(0, 1, 'Edge_From_%i_To_%i' % (s, t))

    def add_constrain(self):
        # Each shift is assigned to exactly one nurse in the schedule period.
        for i in range(self.num_node):
            if i == self.start:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node)) == 1)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node)) == 0)
            elif i == self.end:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node)) == 0)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node)) == 1)
            else:
                self.model.Add(sum(self.nodes_var[(i, j)] for j in range(self.num_node)) == 1)
                self.model.Add(sum(self.nodes_var[(j, i)] for j in range(self.num_node)) == 1)

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
        self.solution_printer = ShortestPathPartialSolutionPrinter(self.nodes_var, self.num_node,
                                                                   self.solution_limit, self.start, self.end)

        self.solver.Solve(self.model, self.solution_printer)

    def print_result(self):
        # Statistics.
        print('\nStatistics')
        print('  - conflicts      : %i' % self.solver.NumConflicts())
        print('  - branches       : %i' % self.solver.NumBranches())
        print('  - wall time      : %f s' % self.solver.WallTime())
        print('  - solutions found: %i' % self.solution_printer.solution_count())


def main():
    # Creates the model.
    shortest_path = ShortestPath()
    shortest_path.solve()


if __name__ == '__main__':
    main()
