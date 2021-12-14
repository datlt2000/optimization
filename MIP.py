import math
import time

from ortools.linear_solver import pywraplp
from data import read_dataset
import matplotlib.pyplot as plt


class JobScheduling:
    def __init__(self, position=None, num_staff=None):
        self.num_staff = num_staff
        self.position = position
        self.num_customer = len(position)
        self.y = {}  # IntVar
        self.x = {}  # IntVar
        self.solver = None  # Ortool Solver
        self.objective = None  # Ortool objective
        self.obj = 0

    def create_solver(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_var(self):
        # Creates variables.

        # MTZ constrain
        for i in range(self.num_customer):
            self.y[i] = self.solver.IntVar(1, self.num_customer + 2, 'y[{}]'.format(i))

        # x[k, i, j] = 1 if k move from customer i to j
        for k in range(self.num_staff):
            for i in range(self.num_customer):
                for j in range(self.num_customer):
                    self.x[k, i, j] = self.solver.IntVar(0, 1, 'z[{}][{}]'.format(k, i))

        # objective
        self.obj = self.solver.IntVar(0, self.solver.infinity(), "obj")

    def add_constrain(self):
        # every customer must be visited one time
        for i in range(1, self.num_customer):
            self.solver.Add(sum(self.x[k, i, j] for j in range(self.num_customer) for k in range(self.num_staff)) == 1)

        # if staff k visit i, he must move from i
        for i in range(1, self.num_customer):
            # self.solver.Add(sum(self.x[j, i] for j in range(self.num_customer)) == 1)
            for k in range(self.num_staff):
                self.solver.Add(sum(self.x[k, j, i] for j in range(self.num_customer)) == sum(
                    self.x[k, i, j] for j in range(self.num_customer)))

        # after work every staff go back office
        for k in range(self.num_staff):
            self.solver.Add(sum(self.x[k, 0, i] for i in range(1, self.num_customer)) == sum(
                self.x[k, i, 0] for i in range(1, self.num_customer)))

        # MTZ sub tour constrain
        for i in range(1, self.num_customer):
            for j in range(1, self.num_customer):
                if i != j:
                    self.solver.Add(self.y[i] - self.y[j] + self.num_customer * sum(
                        self.x[k, i, j] for k in range(self.num_staff)) <= self.num_customer - 1)

        # 5: Ban loop
        for i in range(self.num_customer):
            for k in range(self.num_staff):
                self.solver.Add(self.x[k, i, i] == 0)

        # Objective
        for k in range(self.num_staff):
            self.solver.Add(
                sum(self.x[k, i, j] * (
                        self.distince(self.position[i + 1], self.position[j + 1]) + self.position[j + 1]['d'])
                    for i in range(self.num_customer) for j in range(self.num_customer)) <= self.obj)

    @staticmethod
    def distince(f, t):
        return math.sqrt(math.pow(f['x'] - t['x'], 2) + math.pow(f['y'] - t['y'], 2))

    def set_objective(self):
        self.solver.Minimize(self.obj)

    def solve(self):
        self.create_solver()
        self.create_var()
        self.add_constrain()
        self.set_objective()
        print("solving")
        print("-------------------")
        start_time = time.time()
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            s = self.print_result()
        else:
            s = "cannot solve"
            print("cannot solve")
        end_time = time.time() - start_time
        s += "Solve time: {t} s\n".format(t=end_time)
        print("Solve time: %s s" % end_time)
        return s

    @staticmethod
    def visualize(data, position):
        for i in data:
            x = []
            y = []
            for j in i:
                x.append(position[j + 1]['x'])
                y.append(position[j + 1]['y'])
            plt.plot(x, y)
        plt.show()

    def print_result(self):
        # Statistics.
        s = "IP solution: \n"
        s += "Cost: {obj:.3f}\n".format(obj=self.solver.Objective().Value())
        edges_list = [-1] * self.num_customer
        for i in range(self.num_customer):
            for j in range(1, self.num_customer):
                for k in range(self.num_staff):
                    if self.x[k, i, j].solution_value() == 1:
                        edges_list[j] = i

        routing = [[0]] * self.num_staff
        for i in range(self.num_staff):
            s += 'Path: ' + str(0)
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
            s += '-->' + str(0) + '\n'
            print(s)
        self.visualize(routing, self.position)
        return s


def main():
    file_name = "P/a.vrp"
    # path = input("path to file: ")
    print("reading data ...")
    print("-----------------")
    data = read_dataset(file_name)
    print(data)
    # Creates the solver.
    shortest_path = JobScheduling(position=data, num_staff=4)
    s = shortest_path.solve()
    s += 'end \n -----------------\n'
    with open("./result/vrp.txt", 'a') as f:
        f.write(file_name + '\n')
        f.write(s)
    print("end")
    print("------------------")


if __name__ == '__main__':
    main()
