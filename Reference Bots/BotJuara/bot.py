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
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    # Get all available cells to shoot
    global targets
    targets = []
    for cell in opponent_map['Cells']:
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
            
    if state['Phase'] == 1:
        place_ships()
    else:
        fire_shot(state['OpponentMap'])


def output_shot(x, y, move=1):
    # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    target = pilih(opponent_map)
    output_shot(*target)
    return
    
def random(opponent_map):
    target = choice(targets)
    return target
    
def is_valid_cell(x, y):
    return x < map_size and y < map_size

def pilih(opponent_map):
    next_to_damaged_cell = get_cell_next_to_damaged(opponent_map)
    if next_to_damaged_cell != None:
        return next_to_damaged_cell
        
    next_to_missed_cell = get_cell_next_to_missed(opponent_map)
    if next_to_missed_cell != None:
        return next_to_missed_cell
        
def get_cell_next_to_damaged(opponent_map):
    damaged_cell = None
    
    for cell in opponent_map['Cells']:
        if cell['Damaged']:
            damaged_cell = (cell['X'], cell['Y'])
            break
    
    if damaged_cell == None:
        return None
    elif is_available((damaged_cell[0] + 1, damaged_cell[1])):
        return (damaged_cell[0] + 1, damaged_cell[1])
    elif is_available((damaged_cell[0], damaged_cell[1] + 1)):
        return (damaged_cell[0], damaged_cell[1] + 1)
    elif is_available((damaged_cell[0] - 1, damaged_cell[1])):
        return (damaged_cell[0] - 1, damaged_cell[1])
    elif is_available((damaged_cell[0], damaged_cell[1] - 1)):
        return (damaged_cell[0], damaged_cell[1] - 1)
    else: 
        return None
        
def get_cell_next_to_missed(opponent_map):
    missed_cell = None
    
    for cell in opponent_map['Cells']:
        if cell['Missed']:
            missed_cell = (cell['X'], cell['Y'])
            break
    
    if missed_cell == None:
        return None
    elif is_available((missed_cell[0] + 1, missed_cell[1] + 1)):
        return (missed_cell[0] + 1, missed_cell[1] + 1)
    elif is_available((missed_cell[0] - 1, missed_cell[1] + 1)):
        return (missed_cell[0] - 1, missed_cell[1] + 1)
    elif is_available((missed_cell[0] + 1, missed_cell[1] - 1)):
        return (missed_cell[0] + 1, missed_cell[1] - 1)
    elif is_available((missed_cell[0] - 1, missed_cell[1] - 1)):
        return (missed_cell[0] - 1, missed_cell[1] - 1)
    else: 
        return False
    
def is_available(cell):
    i = 0
    found = False
    while i < len(targets) and not found:
        if target[i] == cell:
            found = True
    return found
            
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
