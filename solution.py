assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

# find out the diagonal boxes
dialg1 = [i+j for i, j in zip([r for r in rows], [c for c in cols])]
dialg2 = [i+j for i, j in zip([r for r in rows], [c for c in cols][::-1])]

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

units = dict()
for s in boxes:
    units[s] = []
    for u in unitlist:
        if s in u:
            units[s] += [u]
    # make sure to add the diagonal boxed to units if nessesary
    if s in dialg1:
        units[s] += [dialg1]
    if s in dialg2:
        units[s] += [dialg2]

# units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
# print(units['B2'])


peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def removetwinvalues(twinboxes, values):
    """
    @brief      take twin boxed and and build the either units and then
    eliminate the values from peers

    @param      twinboxes  list
    @param      values     dict

    @return     dict
    """
    if twinboxes[0][0] == twinboxes[1][0]:
        rcboxes = cross(twinboxes[0][0], cols)
    else:
        rcboxes = cross(rows, twinboxes[0][1])

    # print(rcboxes)
    units = dict((s, [u for u in square_units if s in u]) for s in twinboxes)
    # totalunits = rcboxes + units[twinboxes[0]][0] + units[twinboxes[1]][0]
    totalunits = rcboxes
    totalunits = list(set(totalunits))
    totalunits.remove(twinboxes[0])
    totalunits.remove(twinboxes[1])
    totalunits = list(set(totalunits))
    for r in totalunits:
        for c in values[twinboxes[0]]:
            if len(values[r]) > 1:
                values[r] = values[r].replace(c, '')
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins

    for row in row_units:
        for index, key in enumerate(row):
            if len(values[row[index]]) is not 2:
                continue
            for j in range(index+1, len(row)):
                if values[row[index]] == values[row[j]]:
                    # print([row[index], row[j]])
                    values = removetwinvalues([row[index], row[j]], values)
                    # display(values)


    for col in column_units:
        for index, key in enumerate(col):
            if len(values[col[index]]) is not 2:
                continue
            for j in range(index+1, len(col)):
                if values[col[index]] == values[col[j]]:
                    # print([col[index], col[j]])
                    values = removetwinvalues([col[index], col[j]], values)
                    # display(values)
    return values

    # Eliminate the naked twins as possibilities for their peers


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)
    sol = search(values)

    if sol:
        return sol
    return False

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
