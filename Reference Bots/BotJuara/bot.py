import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0
targets = []


def main(player_key):
    global map_size
    global targets
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']

    if state['Phase'] == 1:
        place_ships()
    else:
        # Get all available cells to shoot
        targets = []
        for cell in state['OpponentMap']['Cells']:
            if not cell['Damaged'] and not cell['Missed']:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        fire_shot(state['OpponentMap'])


def output_shot(x, y):
    move = 1# 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    target = cross_alg(opponent_map)
    output_shot(*target)
    return

def random():
    target = choice(targets)
    return target

def is_valid_cell(x, y):
    return x < map_size and y < map_size

def cross_alg(opponent_map):
    n = 2

    next_to_damaged_cell = get_cell_next_to_damaged(opponent_map)
    if next_to_damaged_cell != None:
        return next_to_damaged_cell

    while n > 1:
        next_to_missed_cell = get_cell_next_to_missed(opponent_map, n)
        if next_to_missed_cell == None:
            n -= 1
        else:
            return next_to_missed_cell

    return random()

###Danger Zone
def get_cell(opponent_map, cell_coor):
    for cell in opponent_map['Cells']:
        if (cell['X'] == cell_coor[0]) and (cell['Y'] == cell_coor[1]):
            return cell
    return False

def is_damaged_cell(opponent_map, cell):
    if is_valid_cell(cell[0], cell[1]):
        if get_cell(opponent_map, cell)['Damaged']:
            return True
    return False

def is_missed_cell(opponent_map, cell):
    if is_valid_cell(cell[0], cell[1]):
        if get_cell(opponent_map, cell)['Missed']:
            return True
    return False

def is_available_cell(cell):
    if is_valid_cell(cell[0], cell[1]):
        if (cell[0], cell[1]) in targets:
            return True
    return False

### 1: North, 2: South, 3: East, 4: West
def identify_cell_damaged(opponent_map, damaged_cell):
    # North & South
    if is_damaged_cell(opponent_map, (damaged_cell[0], damaged_cell[1] + 1)) or is_damaged_cell(opponent_map, (damaged_cell[0], damaged_cell[1] - 1)):
        target_cell = identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] + 1), 1)
        if (target_cell != None):
            return target_cell
        else:
            return identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] - 1), 2)
    #East & West
    elif is_damaged_cell(opponent_map, (damaged_cell[0] + 1, damaged_cell[1])) or is_damaged_cell(opponent_map, (damaged_cell[0] - 1, damaged_cell[1])):
        target_cell = identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] + 1), 3)
        if (target_cell != None):
            return target_cell
        else:
            return identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] - 1), 4)
    else:
        return False

def identify_ship_damaged(opponent_map, damaged_cell, direction):
    current_cell = damaged_cell
    if (direction == 1):
        while(is_damaged_cell(opponent_map, current_cell)):
            current_cell = (current_cell[0], current_cell[1] + 1)
        if is_missed_cell(opponent_map, current_cell):
            return None
        elif is_available_cell(current_cell):
            return current_cell
    elif (direction == 2):
        while(is_damaged_cell(opponent_map, current_cell)):
            current_cell = (current_cell[0], current_cell[1] - 1)
        if is_missed_cell(opponent_map, current_cell):
            return None
        elif is_available_cell(current_cell):
            return current_cell
    elif (direction == 3):
        while(is_damaged_cell(opponent_map, current_cell)):
            current_cell = (current_cell[0] + 1, current_cell[1])
        if is_missed_cell(opponent_map, current_cell):
            return None
        elif is_available_cell(current_cell):
            return current_cell
    elif (direction == 4):
        while(is_damaged_cell(opponent_map, current_cell)):
            current_cell = (current_cell[0] - 1, current_cell[1])
        if is_missed_cell(opponent_map, current_cell):
            return None
        elif is_available_cell(current_cell):
            return current_cell


# def identify_ship_damaged(opponent_map, damaged_cell, direction):
#     if (direction == 1):
#         if is_damaged_cell(opponent_map, damaged_cell):
#             return identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] + 1), 1)
#         elif is_missed_cell(opponent_map, damaged_cell):
#             return None
#         elif is_available_cell(damaged_cell):
#             return damaged_cell
#     elif (direction == 2):
#         if is_damaged_cell(opponent_map, damaged_cell):
#             return identify_ship_damaged(opponent_map, (damaged_cell[0], damaged_cell[1] - 1), 2)
#         elif is_missed_cell(opponent_map, damaged_cell):
#             return None
#         elif is_available_cell(damaged_cell):
#             return damaged_cell
#     elif (direction == 3):
#         if is_damaged_cell(opponent_map, damaged_cell):
#             return identify_ship_damaged(opponent_map, (damaged_cell[0] + 1, damaged_cell[1]), 3)
#         elif is_missed_cell(opponent_map, damaged_cell):
#             return None
#         elif is_available_cell(damaged_cell):
#             return damaged_cell
#     elif (direction == 4):
#         if is_damaged_cell(opponent_map, damaged_cell):
#             return identify_ship_damaged(opponent_map, (damaged_cell[0] - 1, damaged_cell[1]), 4)
#         elif is_missed_cell(opponent_map, damaged_cell):
#             return None
#         elif is_available_cell(damaged_cell):
#             return damaged_cell
###

def get_cell_next_to_damaged(opponent_map):
    damaged_cell = None

    for cell in opponent_map['Cells']:
        if cell['Damaged']:
            damaged_cell = (cell['X'], cell['Y'])
            target_cell = identify_cell_damaged(opponent_map, damaged_cell)
            if (target_cell == False):
                if (damaged_cell[0] + 1, damaged_cell[1]) in targets:
                    return (damaged_cell[0] + 1, damaged_cell[1])
                elif (damaged_cell[0], damaged_cell[1] + 1) in targets:
                    return (damaged_cell[0], damaged_cell[1] + 1)
                elif (damaged_cell[0] - 1, damaged_cell[1]) in targets:
                    return (damaged_cell[0] - 1, damaged_cell[1])
                elif (damaged_cell[0], damaged_cell[1] - 1) in targets:
                    return (damaged_cell[0], damaged_cell[1] - 1)
            elif (target_cell != None):
                return target_cell

    return None

def get_cell_next_to_missed(opponent_map, delta):
    missed_cell = None

    for cell in opponent_map['Cells']:
        if cell['Missed'] and is_missed_cell_valid((cell['X'], cell['Y']), delta):
            missed_cell = (cell['X'], cell['Y'])
            if (missed_cell[0] + delta, missed_cell[1] + delta) in targets:
                return (missed_cell[0] + delta, missed_cell[1] + delta)
            elif (missed_cell[0] - delta, missed_cell[1] + delta) in targets:
                return (missed_cell[0] - 1, missed_cell[1] + 1)
            elif (missed_cell[0] + delta, missed_cell[1] - delta) in targets:
                return (missed_cell[0] + delta, missed_cell[1] - delta)
            elif (missed_cell[0] - delta, missed_cell[1] - delta) in targets:
                return (missed_cell[0] - delta, missed_cell[1] - delta)

    return None

def is_missed_cell_valid(missed_cell, n):
    i = n
    while (i > 1):
        if (((missed_cell[0] + n, missed_cell[1]) in targets and (missed_cell[0] - n, missed_cell[1]) in targets and (missed_cell[0], missed_cell[1] + n) in targets and (missed_cell[0], missed_cell[1] - n) in targets) == False):
            return False
        else:
            i -= 1
    return True

# def is_missed_cell_valid(missed_cell, n):
#     if n == 0:
#         return True
#     else:
#         return (missed_cell[0] + n, missed_cell[1]) in targets and (missed_cell[0] - n, missed_cell[1]) in targets and (missed_cell[0], missed_cell[1] + n) in targets and (missed_cell[0], missed_cell[1] - n) in targets and is_missed_cell_valid(missed_cell, n - 1)


def get_damaged_and_missed_cell(opponent_map):
    # Get damaged cell which has the surrounding
    damaged = False
    missed = False
    damaged_cell = None
    missed_cell = None
    for cell in opponent_map['Cells']:
        if cell['Damaged'] and not damaged:
            damaged_cell = (cell['X'], cell['Y'])
            damaged = True
        if cell['Missed'] and not missed:
            missed_cell = (cell['X'], cell['Y'])
            missed = True
        if damaged and missed:
            break

def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    ships = ['Battleship 1 0 north',
             'Carrier 3 1 East',
             'Cruiser 4 2 north',
             'Destroyer 7 3 north',
             'Submarine 1 8 East'
             ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
