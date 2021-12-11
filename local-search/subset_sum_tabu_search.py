from random import randint
import numpy as np


class SubsetSumTabuSearch:
    def __init__(self, n, k, A):
        self.n = n
        self.A = A
        self.k = k
        self.x = []
        self.stable = 0
        self.total = sum(A)
        self.min_value = min(A)
        self.x = np.zeros(n, dtype=int)
        self.x[:] = -1
        self.search_objective = 0

        self.best_solution = np.zeros_like(self.x)
        self.best_solution[:] = -1

        self.best_sol_search_obj = self.total

        self.last_improve_sol = np.zeros_like(self.x)
        self.last_improve_sol[:] = -1
        self.last_improve_sol_obj = self.total

        self.tabu = np.zeros_like(self.x)
        self.tbl = 4
        self.tbl_min = 3
        self.tbl_max = 5
        self.stable_limit = 30

        self.restart_freq = 100

        self.gen_random_solution()
        self.print_current_solution()

        self.it = 1
        self.max_it = 300

    def gen_random_solution(self):
        value = 0
        for i in range(self.n):
            self.x[i] = randint(0, 1)
            value += self.x[i] * A[i]

        self.search_objective = abs(value - self.k)

    def print_current_solution(self):
        print("---------------------------------------------------")
        S = list()
        for i in range(self.n):
            if self.x[i] == 1:
                S.append(i)

        print("S = ", S)
        print("Search objective value ", self.search_objective)

    def cal_search_value(self):
        value = 0
        for i in range(n):
            value += self.x[i] * A[i]
        self.search_objective = abs(value - self.k)
        return self.search_objective

    def search_next_solution(self):
        select_index = -1
        new_search_objective = self.total

        for i in range(n):
            if self.tabu[i] > 0:
                continue

            self.x[i] = 1 - self.x[i]
            objective_val = self.cal_search_value()
            if objective_val < new_search_objective:
                new_search_objective = objective_val
                select_index = i
            self.x[i] = 1 - self.x[i]
        return select_index, new_search_objective

    def search(self):
        while (self.it < self.max_it):
            self.it += 1
            if self.search_objective < self.best_sol_search_obj:
                self.best_sol_search_obj = self.search_objective
                for i in range(self.n):
                    self.best_solution[i] = self.x[i]
                self.stable = 0
            elif self.stable == self.stable_limit:
                print("Restore")
                self.search_objective = self.last_improve_sol_obj
                for i in range(self.n):
                    self.x[i] = self.last_improve_sol[i]

                self.stable = 0
            else:
                self.stable += 1

                # Restart
                if self.it % self.restart_freq == 0:
                    print("Restarted ")

                    # Sinh lời giải ngẫu nhiên
                    self.gen_random_solution()

                    # Update tabu
                    for i in range(self.n):
                        self.tabu[i] = 0

            old_search_objective = self.search_objective
            index, new_search_objective = self.search_next_solution()
            print("index = ", index, " new search objective = ", new_search_objective)

            # Move
            self.x[index] = 1 - self.x[index]
            self.search_objective = new_search_objective

            # Update tabu
            for i in range(n):
                if self.tabu[i] > 0:
                    self.tabu[i] -= 1

            self.tabu[index] = self.tbl

            if new_search_objective < old_search_objective:
                if self.tbl > self.tbl_min:
                    self.tbl -= 1
            else:
                if self.tbl < self.tbl_max:
                    self.tbl += 1

            # Update last improved solution
            if new_search_objective < old_search_objective:
                print("Improved")

                self.last_improve_sol_obj = new_search_objective
                for i in range(n):
                    self.last_improve_sol[i] = self.x[i]

                self.stable = 0
        self.print_best_solution()

    def print_best_solution(self):
        S = list()
        for i in range(n):
            if self.best_solution[i] == 1:
                S.append(A[i])

        print("\n Best solution :")
        print("S = ", S)
        print("Search objective value ", self.best_sol_search_obj)


def input_data():
    n = 0
    k = 0
    A = []
    print("Input")
    print("n = ", n)
    print("k = ", k)
    print("A = ", A)
    return n, k, A


def create_data():
    n = 9
    A = [-7, -3, -2, 5, 8, 3, 2, -1, 10]
    k = 0
    return n, k, A


if __name__ == '__main__':
    # n, k, A = input_data()
    n, k, A = create_data()
    print(k)
    tabu_search = SubsetSumTabuSearch(n, k, A)
    tabu_search.search()
