import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0


def main(player_key):
    global map_size
    global energy
    global state
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    energy = state['PlayerMap']['Owner']['Energy']
    if state['Phase'] == 1:
        place_ships()
    else:
        fire_shot(state['OpponentMap']['Cells'])


def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

def output_seeker(x, y):
    move = 7  # 8=fire seeker command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    targets = []
    adjecent = []
    priority = [(0,1), (0,4), (0,6), (0,8), (1,0), (1,5), (1,9), (3,0), (3,9), (4,1), (4,8), (5,0), (5,9), (8,0), (8,5), (8,9), (9,1), (9,4), (9,6), (9,8)]
    priority_2 = [(8,2), (7,3), (6,4), (5,5), (4,6), (3,4), (4,3), (5,2), (6,1), (7,6),(8,7),(6,7),(7,8)]
    seeker_targer = [(2,2), (2,7), (4,4), (7,2), (7,7)]
    list_ship = []
    sink = []
    targetss = []
    single = False
    parse_id = 0
    
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
    # heat seeker
    for Ship in state['PlayerMap']['Owner']['Ships']:
            if not Ship['Destroyed']:
                valid_ship = Ship['ShipType']
                list_ship.append(valid_ship)
    print(list_ship)
    if energy >= 36 and 'Submarine' in list_ship:
            print("!")
            x = state['Round'] // 19
            print(x)
            target = seeker_targer[x]
            output_seeker(*target)
    else:
        # 1 part hit
        for cell in opponent_map:
            parse_id = parse_id + 1
            if cell['Damaged']:
                print("damaged")
                print(cell['X'],",",cell['Y'])
                if state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] + 1]['Damaged'] :
                    double_up = cell['X'], cell['Y'] + 2
                    down_cell = cell['X'], cell['Y'] - 1
                    sink.append(double_up)
                    sink.append(down_cell)
                if state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] + map_size]['Damaged'] :
                    left_cell = cell['X'] - 1, cell['Y']
                    double_right = cell['X'] + 2, cell['Y']
                    sink.append(left_cell)
                    sink.append(double_right)
                if not(state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] + 1]['Damaged'] or state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] - 1]['Damaged'] or state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] + map_size]['Damaged'] or state['OpponentMap']['Cells'][cell['X']*10 + cell['Y'] - map_size]['Damaged']):
                    single = True
                    break
        print(sink)
        print(len(sink))
        if single:
            print("single")
            print(parse_id)
            id = 0
            for cell in opponent_map:
                id = id + 1
                if id == parse_id:
                    right_cell = cell['X'] + 1, cell['Y']
                    left_cell = cell['X'] - 1, cell['Y']
                    up_cell = cell['X'], cell['Y'] + 1
                    down_cell = cell['X'], cell['Y'] - 1
                    adjecent.append(right_cell)
                    adjecent.append(left_cell)
                    adjecent.append(up_cell)
                    adjecent.append(down_cell)
                    targetss = list(set(targets) & set(adjecent))
        else:
            print("pair")
            for cell in opponent_map:
                if cell['Damaged']:
                    # if 1 part got hit shoot the adjecent
                    right_cell = cell['X'] + 1, cell['Y']
                    left_cell = cell['X'] - 1, cell['Y']
                    up_cell = cell['X'], cell['Y'] + 1
                    down_cell = cell['X'], cell['Y'] - 1
                    adjecent.append(right_cell)
                    adjecent.append(left_cell)
                    adjecent.append(up_cell)
                    adjecent.append(down_cell)
                    targetss = list(set(targets) & set(adjecent) & set(sink))
        if len(targetss) > 0:
            print("!")
            print(targetss)
            target = choice(targetss)
        else:
            print("random")
            priority_target = list(set(targets) & set(priority_2))    
            if len(priority_target) > 0:
                print("priority 1")
                target = choice(priority_target)
            else:
                priority_target = list(set(targets) & set(priority))
                if len(priority_target) > 0:
                    print("priority 2")
                    target = choice(priority_target)
                else:
                    print("pure random")    
                    target = choice(targets)    
        output_shot(*target)
    return


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
