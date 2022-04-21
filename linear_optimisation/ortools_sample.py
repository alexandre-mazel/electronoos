# from https://towardsdatascience.com/introduction-to-linear-programming-in-python-9261e7eb44b

import ortools # pip install ortools

from ortools.linear_solver import pywraplp

# Create a solver using the GLOP backend
solver = pywraplp.Solver('Maximize army power', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)


"""
Imagine you are a strategist recruiting an army. You have:

    Three resources: food, wood, and gold
    Three units: swordsmen, bowmen, and horsemen.

Horsemen are stronger than bowmen, 
who are in turn stronger than swordsmen.
(cf power below)
"""

# Create the variables we want to optimize, and their range
swordsmen = solver.IntVar(0, solver.infinity(), 'swordsmen')
bowmen = solver.IntVar(0, solver.infinity(), 'bowmen')
horsemen = solver.IntVar(0, solver.infinity(), 'horsemen')

# ressource limits:
# 1 swordman = 60 food + 20 wood
# 1 bowman = 80 food + 10 wood + 40 gold
# 1 horsman = 140 food + 100 gold

solver.Add(swordsmen*60 + bowmen*80 + horsemen*140 <= 1200) # Food
solver.Add(swordsmen*20 + bowmen*10 <= 800) # Wood
solver.Add(bowmen*40 + horsemen*100 <= 600) # Gold

# power of each one:
# 1 swordman = 70
# 1 bowman = 95
# 1 horsmane = 230

solver.Maximize(swordsmen*70 + bowmen*95 + horsemen*230)

status = solver.Solve()

# If an optimal solution has been found, print results
if status == pywraplp.Solver.OPTIMAL:
  print('================= Solution =================')
  print(f'Solved in {solver.wall_time():.2f} milliseconds in {solver.iterations()} iterations')
  print()
  print(f'Optimal power = {solver.Objective().Value()} power')
  print('Army:')
  print(f' - Swordsmen = {swordsmen.solution_value()}')
  print(f' - Bowmen = {bowmen.solution_value()}')
  print(f' - Horsemen = {horsemen.solution_value()}')
else:
  print('The solver could not find an optimal solution.')