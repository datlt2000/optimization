"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model


class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """ Print intermediate solutions. """

    def __init__(self, shifts, num_nurses, num_days, num_shifts, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_nurses = num_nurses
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        print('Solution %i' % self._solution_count)
        for d in range(self._num_days):
            print('Day %i' % d)
            for n in range(self._num_nurses):
                is_working = False
                for s in range(self._num_shifts):
                    if self.Value(self._shifts[(n, d, s)]):
                        is_working = True
                        print('  Nurse %i works shift %i' % (n, s))
                if not is_working:
                    print('  Nurse {} does not work'.format(n))
        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


class NurseScheduling:
    def __init__(self, num_nurses=4, num_shifts=3, num_days=3, solution_limit=5):
        self.num_nurses = num_nurses
        self.num_shifts = num_shifts
        self.num_days = num_days
        self.solution_limit = solution_limit
        self.all_nurses = range(self.num_nurses)
        self.all_shifts = range(self.num_shifts)
        self.all_days = range(self.num_days)
        self.model = None  # cp_model.CPModel: Model of problem
        self.shifts = {}  # cp_model.NewBoolVar: var in model
        self.solver = None  # cp_model.Solver
        self.solution_printer = None  # Call back class return result from solver

    def create_model(self):
        self.model = cp_model.CpModel()

    def create_var(self):
        # Creates shift variables.
        # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
        for n in self.all_nurses:
            for d in self.all_days:
                for s in self.all_shifts:
                    self.shifts[(n, d,
                                 s)] = self.model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    def add_constrain(self):
        # Each shift is assigned to exactly one nurse in the schedule period.
        for d in self.all_days:
            for s in self.all_shifts:
                self.model.Add(sum(self.shifts[(n, d, s)] for n in self.all_nurses) == 1)

        # Each nurse works at most one shift per day.
        for n in self.all_nurses:
            for d in self.all_days:
                self.model.Add(sum(self.shifts[(n, d, s)] for s in self.all_shifts) <= 1)

        # Try to distribute the shifts evenly, so that each nurse works
        # min_shifts_per_nurse shifts. If this is not possible, because the total
        # number of shifts is not divisible by the number of nurses, some nurses will
        # be assigned one more shift.
        min_shifts_per_nurse = (self.num_shifts * self.num_days) // self.num_nurses
        if self.num_shifts * self.num_days % self.num_nurses == 0:
            max_shifts_per_nurse = min_shifts_per_nurse
        else:
            max_shifts_per_nurse = min_shifts_per_nurse + 1
        for n in self.all_nurses:
            num_shifts_worked = []
            for d in self.all_days:
                for s in self.all_shifts:
                    num_shifts_worked.append(self.shifts[(n, d, s)])
            self.model.Add(min_shifts_per_nurse <= sum(num_shifts_worked))
            self.model.Add(sum(num_shifts_worked) <= max_shifts_per_nurse)

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
        self.solution_printer = NursesPartialSolutionPrinter(self.shifts, self.num_nurses,
                                                             self.num_days, self.num_shifts,
                                                             self.solution_limit)

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
    nurse_scheduler = NurseScheduling()
    nurse_scheduler.solve()


if __name__ == '__main__':
    main()
