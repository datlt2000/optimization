from ortools.linear_solver import pywraplp
import numpy as np


class MinimumLatencyProblem:
    def __init__(self, data=None, v=None):
        self.num_node = len(v)
        self.data = data
        self.all_node = v
        self.x = dict()  # IntVar: x[i, j] = 1 if move from i to j else 0
        self.y = dict()  # IntVar: y[i, j, k] = 1 if move from i, j in step k
        self.solver = None
        self.objective = None

    def create_solver(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_var(self):
        # Creates variables.
        for i in self.all_node:
            for k in range(1, self.num_node + 1):
                self.x[i, k] = self.solver.IntVar(0, 1, "x[%d, %d]" % (i, k))
        for i in self.all_node:
            for j in self.all_node:
                for k in range(1, self.num_node):
                    if j == i:
                        self.y[i, j, k] = self.solver.IntVar(0, 0, "y[%d, %d, %d]" % (i, j, k))
                    else:
                        self.y[i, j, k] = self.solver.IntVar(0, 1, "y[%d, %d, %d]" % (i, j, k))

    def add_constrain(self):
        # every node have 1 coming edge
        ct1 = dict()
        for i in self.all_node:
            ct1[i] = self.solver.Constraint(1, 1, "ct1[%d]" % i)
            for k in range(1, self.num_node + 1):
                ct1[i].SetCoefficient(self.x[i, k], 1)

        # every node have 1 outing edge
        ct2 = dict()
        for k in range(1, self.num_node + 1):
            ct2[k] = self.solver.Constraint(1, 1, "ct2[%d]" % k)
            for i in self.all_node:
                ct2[k].SetCoefficient(self.x[i, k], 1)

        # every node is visited in 1 step
        ct4 = dict()
        for i in self.all_node:
            for k in range(1, self.num_node):
                ct4[i, k] = self.solver.Constraint(0, 0, "ct4[%d, %d]" % (i, k))
                ct4[i, k].SetCoefficient(self.x[i, k], -1)
                for j in self.all_node:
                    if j != i:
                        ct4[i, k].SetCoefficient(self.y[i, j, k], 1)

        ct5 = dict()
        for i in self.all_node:
            for k in range(1, self.num_node):
                ct5[i, k] = self.solver.Constraint(0, 0, "ct5[%d, %d]" % (i, k))
                ct5[i, k].SetCoefficient(self.x[i, k + 1], -1)
                for j in self.all_node:
                    if j != i:
                        ct5[i, k].SetCoefficient(self.y[j, i, k], 1)

    def set_objective(self):
        self.objective = self.solver.Objective()
        for k in range(1, self.num_node):
            for i in self.all_node:
                for j in self.all_node:
                    if j != i:
                        self.objective.SetCoefficient(self.y[i, j, k], (self.num_node - k) * self.data[i, j])

    def solve(self):
        self.create_solver()
        self.create_var()
        self.add_constrain()
        self.set_objective()
        print('solving')
        status = self.solver.Solve()
        if status in [pywraplp.Solver.FEASIBLE, pywraplp.Solver.OPTIMAL]:
            self.print_result()
        else:
            print("cannot solve")

    def print_result(self):
        print("IP solution:")
        print("Cost: %8.3f" % (self.objective.Value()))
        path = list()
        edges_list = list()
        for k in range(1, self.num_node + 1):
            for i in self.all_node:
                if self.x[i, k].solution_value() == 1:
                    path.append(i)
                    if k > 1:
                        u = path[k - 2]
                        v = i
                        edges_list.append("\t%3d -> %3d: %6.3f" % (u, v, self.data[u, v]))
        s = 'Path: ' + ' -> '.join([str(v) for v in path])
        print(s)
        print('Edges:')
        for e in edges_list:
            print(e)
        print("_________________________________________________\n")
        return path, edges_list

def read_data(file_name, start, end):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    coordinates = dict()
    data = dict()
    data['V'] = set()
    for line in lines[start:end]:
        i, x, y = line.split(' ')
        coordinates[int(i)] = np.array([float(x), float(y)])
        data['V'].add(int(i))
    data['C'] = np.zeros((len(data['V']) + 1, len(data['V']) + 1))
    for i in data['V']:
        for j in data['V']:
            data['C'][i, j] = np.sqrt(((coordinates[i] - coordinates[j]) ** 2).sum())
    return data


def main():
    path = "../data/Bai2_dj38.tsp"
    # path = input("path to file: ")
    data = read_data(path, start=10, end=48)
    # Creates the solver.
    shortest_path = MinimumLatencyProblem(data=data["C"], v=data["V"])
    shortest_path.solve()


if __name__ == '__main__':
    main()
