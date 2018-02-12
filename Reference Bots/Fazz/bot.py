#
#   This is Dilan.
#   Dilan is a bot that will beat you in the game of Battleships.
#   Dilan uses an algorithm called Lon*te Carlo developed by: Jon, Musang, and Izzan
#

import argparse
import json
import os
from random import choice

# Constants
CELL_UNKNOWN = 0
CELL_MISSED = 1
CELL_DAMAGED = 2

ACTION_SKIP = 0
ACTION_SHOOT = 1
ACTION_EXPLORE = 2

# Global vars
command_file = 'command.txt'
place_ship_file = 'place.txt'
game_state_file = 'state.json'
output_path = '.'
map_size = 0
opponent_map = None
pathway = {}
pathway_dist = []
ships = []


def main(player_key):
    global map_size
    global opponent_map
    global pathway
    global ships

    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    opponent_map = state['OpponentMap']['Cells']

    # Define pathway for seeking and ships placement
    if (map_size == 7):
        pathway[4] = [(2,3),(3,2),(3,4),(4,3)]
        pathway[3] = [(0,3),(1,2),(1,4),(2,1),(2,5),(3,0),(3,6),(4,1),(4,5),(5,2),(5,4),(6,3)]
        pathway[2] = [(0,1),(0,5),(1,0),(1,6),(5,0),(5,6),(6,1),(6,5)]
                    
        ships = [ 
            'Battleship 3 3 north', 
            'Carrier 1 1 east', 
            'Cruiser 4 3 east', 
            'Destroyer 5 5 east', 
            'Submarine 1 3 north']

    elif (map_size == 10):
        pathway[6] = [(3,4),(3,6),(4,3),(4,5),(5,4),(5,6),(6,5)]
        pathway[5] = [(2,3),(2,5),(2,7),(3,2),(4,7),(5,2),(6,7),(7,2),(7,4),(7,6)]
        pathway[4] = [(0,3),(0,5),(1,2),(1,4),(1,6),(1,8),(2,1),(3,0),(3,8),(4,1),(4,9),(5,0),(5,8),(6,1),(6,9),(7,8),(8,1),(8,3),(8,5),(8,7),(9,4),(9,6)]
        pathway[3] = [(0,1),(0,3),(0,7),(0,9),(1,0),(2,9),(7,0),(8,9),(9,0),(9,2),(9,8)] 
        
        ships = [ 
            'Battleship 1 2 east', 
            'Carrier 8 2 north', 
            'Cruiser 0 4 north', 
            'Destroyer 3 6 north', 
            'Submarine 4 4 east']
    else:
        pathway[8] = [(5,5),(5,7),(6,6),(6,8),(7,5),(7,7),(8,6),(8,8)]
        pathway[7] = [(3,5),(3,7),(4,4),(4,6),(4,8),(5,9),(6,4),(6,10),(7,3),(7,9),(8,4),(9,5),(9,7),(9,9),(10,6),(10,8)]
        pathway[6] = [(2,4),(2,6),(2,8),(2,10),(3,3),(3,9),(4,10),(5,3),(5,11),(6,2),(7,11),(8,2),(8,10),(9,3),(10,4),(10,10),(6,3),(6,5),(6,7),(6,9)]
        pathway[5] = [(0,4),(0,6),(0,8),(1,3),(1,5),(1,7),(1,9),(1,11),(2,2),(3,3),(3,9),(4,0),(4,2),(4,12),(5,1),(5,13),(6,0),(6,12),(7,1),(7,13),(8,0),(8,12),(9,1),(9,11),(9,13),(10,2),(10,12),(11,11),(12,2),(12,4),(12,6),(12,8),(12,10),(13,5),(13,7),(13,9)]
        pathway[4] = [(0,0),(0,2),(0,10),(0,12),(1,1),(1,13),(2,0),(2,12),(3,13),(10,0),(11,1),(11,13),(12,0),(12,12),(13,1),(13,3),(13,11),(13,13)]

        ships = ['Battleship 1 1 east', 
                'Carrier 10 6 north', 
                'Cruiser 6 9 north', 
                'Destroyer 12 2 east', 
                'Submarine 0 4 north']

    # Move
    if state['Phase'] == 1:
        place_ships()
    else:
        seek()


def get_cell(x, y):
    for cell in opponent_map:
        if cell['X'] == x and cell['Y'] == y:
            return cell;
    return None


def get_cell_status(x, y):
    cell = get_cell(x, y)
    if cell['Missed']:
        return CELL_MISSED
    elif cell['Damaged']:
        return CELL_DAMAGED
    else:
        return CELL_UNKNOWN


def choose_cell():
    return choice(pathway_dist)


def create_pathway_dist():
    global pathway_dist
    for score, cells in zip(pathway.keys(), pathway.values()):
        pathway_dist.extend(cells * score)


def seek():
    global pathway

    # Remove missed cells and find an unfinished exploration
    explore_found = False
    for cells in pathway.values():
        for cell in cells:
            target = explore(*cell)
            if target == (-1, -1):
                cells.remove(cell)
            elif get_cell_status(*cell) == CELL_DAMAGED:
                output_shot(*target)
                explore_found = True
                break
        if explore_found:
            break

    # Seek new cell to explore
    if not explore_found:
        create_pathway_dist()
        choice = choose_cell()
        target = explore(*choice)
        while target == (-1, -1):
            choice = choose_cell()
            target = explore(*choice)
        output_shot(*target)


def explore(x, y):
    if get_cell_status(x, y) == CELL_UNKNOWN:
        return (x, y)
    elif get_cell_status(x, y) == CELL_MISSED:
        return (-1, -1)
    else:
        x_found, y_found, action = explore_surrounding(x, y)
        if action == ACTION_SKIP:
            return (-1, -1)
        elif action == ACTION_SHOOT:
            return (x_found, y_found)
        else:
            if y_found == y:
                return explore_horizontal(x, y)
            else:
                return explore_vertical(x, y)


def explore_vertical(x, y):
    up_len = 0
    up_status = CELL_DAMAGED
    down_len = 0
    down_status = CELL_DAMAGED

    curr_y = y
    while up_status == CELL_DAMAGED and curr_y < map_size - 1:
        curr_y += 1
        up_len += 1
        up_status = get_cell_status(x, curr_y)

    curr_y = y
    while down_status == CELL_DAMAGED and curr_y > 0:
        curr_y -= 1
        down_len += 1
        down_status = get_cell_status(x, curr_y)

    if up_status == CELL_UNKNOWN and down_status == CELL_UNKNOWN:
        if up_len <= down_len:
            return (x, y + up_len)
        else:
            return (x, y - down_len)
    elif up_status == CELL_UNKNOWN:
        return (x, y + up_len)
    elif down_status == CELL_UNKNOWN:
        return (x, y - down_len)
    else:
        return (-1, -1)


def explore_horizontal(x, y):
    right_len = 0
    right_status = CELL_DAMAGED
    left_len = 0
    left_status = CELL_DAMAGED

    curr_x = x
    while right_status == CELL_DAMAGED and curr_x < map_size - 1:
        curr_x += 1
        right_len += 1
        right_status = get_cell_status(curr_x, y)

    curr_x = x
    while left_status == CELL_DAMAGED and curr_x > 0:
        curr_x -= 1
        left_len += 1
        left_status = get_cell_status(curr_x, y)

    if right_status == CELL_UNKNOWN and left_status == CELL_UNKNOWN:
        if right_len <= left_len:
            return (x + right_len, y)
        else:
            return (x - left_len, y)
    elif right_status == CELL_UNKNOWN:
        return (x + right_len, y)
    elif left_status == CELL_UNKNOWN:
        return (x - left_len, y)
    else:
        return (-1, -1)


def explore_surrounding(x, y):
    if (x > 0):
        if get_cell_status(x - 1, y) == CELL_UNKNOWN:
            return (x - 1, y, ACTION_SHOOT)
        elif get_cell_status(x - 1, y) == CELL_DAMAGED:
            return (x - 1, y, ACTION_EXPLORE)

    if (x < map_size - 1):
        if get_cell_status(x + 1, y) == CELL_UNKNOWN:
            return (x + 1, y, ACTION_SHOOT)
        elif get_cell_status(x + 1, y) == CELL_DAMAGED:
            return (x + 1, y, ACTION_EXPLORE)

    if (y > 0):
        if get_cell_status(x, y - 1) == CELL_UNKNOWN:
            return (x, y - 1, ACTION_SHOOT)
        elif get_cell_status(x, y - 1) == CELL_DAMAGED:
            return (x, y - 1, ACTION_EXPLORE)

    if (y < map_size - 1):
        if get_cell_status(x, y + 1) == CELL_UNKNOWN:
            return (x, y + 1, ACTION_SHOOT)
        elif get_cell_status(x, y + 1) == CELL_DAMAGED:
            return (x, y + 1, ACTION_EXPLORE)

    return (-1, -1, ACTION_SKIP)


def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west
         
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
