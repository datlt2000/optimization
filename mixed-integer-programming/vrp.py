from ortools.linear_solver import pywraplp

N = 5
K = 3
d = [
    [0, 25, 16, 7, 38, 29],
    [17, 0, 26, 32, 11, 44],
    [25, 55, 0, 12, 18, 9],
    [10, 15, 26, 0, 38, 20],
    [14, 24, 23, 47, 0, 21],
    [21, 25, 35, 15, 6, 0]
]
# create model
solver = pywraplp.Solver.CreateSolver('SCIP')

# Variables.
x = []
for i in range(N + 1):
    x.append([])
    for j in range(N + 1):
        x[i].append([])
        for k in range(K):
            x[i][j].append(solver.IntVar(0, 1, 'x[{}][{}][{}]'.format(i, j, k)))

y = []
for i in range(N):
    y.append([])
    for k in range(K):
        y[i].append(solver.IntVar(0, 1, 'y[{}][{}]'.format(i, k)))

u = []
for i in range(N):
    u.append([])
    for k in range(K):
        u[i].append(solver.IntVar(1, N, 'u[{}][{}]'.format(i, k)))

# Constraints
for k in range(K):
    solver.Add(sum(x[0][i][k] for i in range(1, N + 1)) == 1)
for k in range(K):
    solver.Add(sum(x[i][0][k] for i in range(1, N + 1)) == 1)

# 2: If point i is served by vehicle k, we have the followings:
for i in range(1, N + 1):
    for k in range(K):
        solver.Add(sum(x[i][j][k] for j in range(N + 1)) == y[i - 1][k])
for i in range(1, N + 1):
    for k in range(K):
        solver.Add(sum(x[j][i][k] for j in range(N + 1)) == y[i - 1][k])

# 3: Each point must be served by at least one vehicle
for i in range(1, N + 1):
    solver.Add(sum(x[j][i][k] for k in range(K)
                   for j in range(N + 1)) == 1)

# 4: MLZ
for i in range(1, N + 1):
    for j in range(1, N + 1):
        if j != i:
            for k in range(K):
                solver.Add(u[i - 1][k] - u[j - 1][k] + N * x[i][j][k] <= N - 1)

# 5: Ban loop
for i in range(N + 1):
    for k in range(K):
        solver.Add(x[i][i][k] == 0)

# Objective
for k in range(K):
    solver.Minimize(sum(d[i][j] * x[i][j][k]
                        for i in range(N + 1) for j in range(N + 1) for k in range(K)))
# Solve
status = solver.Solve()

# Print solution
if status == pywraplp.Solver.FEASIBLE or status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    for k in range(K):
        print("-- Vehicle {} --".format(k))
        l = []
        start = 0
        while True:
            l.append(start)
            print("Point {}".format(start))
            for i in range(N + 1):
                if x[start][i][k].solution_value() == 1:
                    start = i
                    break
            if i == 0:
                break
        print("Point 0")
        print("++ Visiting order: {} ++".format(l + [0]))
        s = d[l[-1]][0]
        for i in range(1, len(l)):
            s += d[l[i - 1]][l[i]]
        print("++ Distance: {} ++\n".format(s))
