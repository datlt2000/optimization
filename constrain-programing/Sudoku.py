from ortools.sat.python import cp_model

def displaySudoku(sudoku):
    for row in sudoku:
        for col in row:
            print(col, end= " ")
        print("\n")

def initialSudoku():
    sudoku = []
    print("input sudoku matrix")
    for i in range(9):
        row = input("")
        sudoku.append(row.split(" "))
    
    for i in range(9):
        for j in range(9):
            sudoku[i][j] = int(sudoku[i][j])
    return sudoku

def initialModel(model, sudoku):
    sudoku_init = [[0 for i in range(9)] for j in range(9)]
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] != 0:
                sudoku_init[i][j] = model.NewIntVar(sudoku[i][j], sudoku[i][j], 'row: %i' %i)
            else:
                sudoku_init[i][j] = model.NewIntVar(1, 9, 'row: %i' %i)
    return sudoku_init

def solveSudoku(sudoku):
    model = cp_model.CpModel()
    x = initialModel(model, sudoku)

    # different in row
    for i in range(9):
        model.AddAllDifferent([x[i][j] for j in range(9)])

    #   different in column
    for j in range(9):
        model.AddAllDifferent([x[i][j] for i in range(9)])

    # Constraint in sector
    for row_idx in range(0, 9, 3):
        for col_idx in range(0, 9, 3):
            model.AddAllDifferent([x[row_idx + i][j] for j in range(col_idx, (col_idx + 3)) for i in range(3)])
    
    solver = cp_model.CpSolver()

    # Solving
    status = solver.Solve(model)

    print("==================")
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        for i in range(9):
            for j in range(9):
                print(solver.Value(x[i][j]), end=" ")
            print()
    else:
        print("Unfeasible Sudoku")

    

sudoku_to_solve = [[0, 0, 7, 5, 0, 0, 6, 0, 3],
                               [4, 3, 0, 0, 0, 6, 0, 0, 5],
                               [6, 0, 8, 1, 0, 9, 0, 2, 7],
                               [2, 0, 6, 4, 5, 0, 0, 0, 0],
                               [0, 0, 1, 0, 6, 0, 3, 4, 0],
                               [7, 0, 0, 0, 0, 8, 0, 5, 0],
                               [8, 0, 0, 7, 0, 0, 1, 3, 0],
                               [0, 7, 4, 0, 2, 0, 5, 9, 0],
                               [1, 0, 9, 3, 0, 5, 0, 0, 0]]

displaySudoku(sudoku_to_solve)
print("==================")
solveSudoku(sudoku_to_solve)

# sudoku = initialSudoku()
# solveSudoku(sudoku)