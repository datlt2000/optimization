import math

from ortools.linear_solver import pywraplp
from data import read_dataset
import matplotlib.pyplot as plt


class JobScheduling:
    def __init__(self, position=None, num_staff=None):
        self.num_staff = num_staff
        self.position = position
        self.num_customer = len(position)
        self.x = {}  # IntVar
        self.y = {}  # IntVar
        self.solver = None  # Ortool Solver
        self.objective = None  # Ortool objective

    def create_solver(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_var(self):
        # Creates variables.

        # x[i, j] = 1 if any staff move from customer i to customer j
        # else x[i, j] = 0
        # customer 0 is office
        for i in range(self.num_customer):
            for j in range(self.num_customer):
                self.x[i, j] = self.solver.IntVar(0, 1, 'x[{}][{}]'.format(i, j))

        # MTZ constrain
        for i in range(self.num_customer):
            self.y[i] = self.solver.IntVar(1, self.num_customer + 2, 'y[{}]'.format(i))

    def add_constrain(self):
        # every customer must be visited one time
        for i in range(1, self.num_customer):
            self.solver.Add(sum(self.x[i, j] for j in range(self.num_customer)) == 1)

        for i in range(1, self.num_customer):
            self.solver.Add(sum(self.x[j, i] for j in range(self.num_customer)) == 1)

        # after work every staff go back office
        self.solver.Add(sum(self.x[0, i] for i in range(1, self.num_customer)) == sum(
            self.x[i, 0] for i in range(1, self.num_customer)))

        # number of staff constrain
        self.solver.Add(sum(self.x[0, i] for i in range(1, self.num_customer)) <= self.num_staff)

        # MTZ sub tour constrain
        for i in range(1, self.num_customer):
            for j in range(1, self.num_customer):
                if i != j:
                    self.solver.Add(self.y[i] - self.y[j] + self.num_customer * self.x[i, j] <= self.num_customer - 1)

        # 5: Ban loop
        for i in range(self.num_customer):
            self.solver.Add(self.x[i, i] == 0)

    @staticmethod
    def distince(f, t):
        return math.sqrt(math.pow(f['x'] - t['x'], 2) + math.pow(f['y'] - t['y'], 2))

    def set_objective(self):
        self.objective = self.solver.Objective()
        for i in range(0, self.num_customer):
            for j in range(0, self.num_customer):
                if i != j:
                    self.objective.SetCoefficient(self.x[i, j],
                                                  self.distince(self.position[i + 1], self.position[j + 1]))
        self.objective.SetMinimization()

    def solve(self):
        self.create_solver()
        self.create_var()
        self.add_constrain()
        self.set_objective()
        print("solving")
        print("-------------------")
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            self.print_result()
        else:
            print("cannot solve")

    @staticmethod
    def visualize(data, position):
        for i in data:
            x = []
            y = []
            for j in i:
                x.append(position[j+1]['x'])
                y.append(position[j+1]['y'])
            plt.plot(x, y)
        plt.show()

    def print_result(self):
        # Statistics.
        print("IP solution:")
        print("Cost: %8.3f" % (self.objective.Value()))
        edges_list = [-1] * self.num_customer
        for i in range(self.num_customer):
            for j in range(1, self.num_customer):
                if self.x[(i, j)].solution_value() == 1:
                    edges_list[j] = i

        routing = [[0]] * self.num_staff
        for i in range(self.num_staff):
            s = 'Path: ' + str(0)
            n = 0
            done = False
            while not done:
                done = True
                for j in range(1, self.num_customer):
                    if edges_list[j] == n:
                        routing[i].append(j)
                        s += ' --> ' + str(j)
                        if n == 0:
                            edges_list[j] = -1
                        n = j
                        done = False
                        break
            routing[i].append(0)
            s += '-->' + str(0)
            print(s)
        self.visualize(routing, self.position)


def main():
    fine_name = "A/A-n17-k4.vrp"
    # path = input("path to file: ")
    print("reading data ...")
    print("-----------------")
    data = read_dataset(fine_name)
    print(data)
    # Creates the solver.
    shortest_path = JobScheduling(position=data, num_staff=4)
    shortest_path.solve()
    print("end")
    print("------------------")


if __name__ == '__main__':
    main()
