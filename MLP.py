import math

from ortools.linear_solver import pywraplp
from data import read_dataset


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
            self.y[i] = self.solver.IntVar(1, self.num_customer + 1, 'y[{}]'.format(i))

    def add_constrain(self):
        # every customer must be visited one time
        for i in range(1, self.num_customer):
            self.solver.Add(sum(self.x[i, j] for j in range(self.num_customer)) == 1)
            self.solver.Add(sum(self.x[j, i] for j in range(self.num_customer)) == 1)

        # after work every staff go back office
        self.solver.Add(sum(self.x[0, i] for i in range(1, self.num_customer)) == sum(
            self.x[i, 0] for i in range(1, self.num_customer)))

        # number of staff constrain
        self.solver.Add(sum(self.x[0, i] for i in range(1, self.num_customer)) <= self.num_staff)

        # MTZ sub tour constrain
        for i in range(self.num_customer):
            for j in range(self.num_customer):
                self.solver.Add(self.y[j] - self.y[i] >= self.num_customer * self.x[i, j] + 1 - self.num_customer)

    @staticmethod
    def distince(f, t):
        return math.sqrt(math.pow(f['x'] - t['x'], 2) + math.pow(f['y'] - t['y'], 2))

    def set_objective(self):
        self.objective = self.solver.Objective()
        for i in range(0, self.num_customer):
            for j in range(0, self.num_customer):
                self.objective.SetCoefficient(self.x[(i, j)], self.distince(self.position[i+1], self.position[j+1]))
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

    def print_result(self):
        # Statistics.
        print("IP solution:")
        print("Cost: %8.3f" % (self.objective.Value()))
        edges_list = [0]*(self.num_customer + 1)
        for i in range(1, self.num_customer + 1):
            for j in range(1, self.num_customer + 1):
                if self.x[(i, j)].solution_value() == 1:
                    edges_list[j] = i

        for i in range(self.num_staff):
            s = 'Path: ' + str(0)
            n = 0
            done = True
            while not done:
                done = True
                for j in range(1, self.num_customer):
                    if edges_list[j] == n:
                        s += ' --> ' + str(edges_list[j])
                        n = edges_list[j]
                        done = False
                        break
            print(s)


def main():
    fine_name = "P/P-n16-k8.vrp"
    # path = input("path to file: ")
    print("reading data ...")
    print("-----------------")
    data = read_dataset(fine_name)
    print(data)
    # Creates the solver.
    shortest_path = JobScheduling(position=data, num_staff=5)
    shortest_path.solve()
    print("end")
    print("------------------")


if __name__ == '__main__':
    main()
