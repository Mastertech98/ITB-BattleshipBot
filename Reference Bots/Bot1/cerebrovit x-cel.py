import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0
move_type = {
    "SeekerMissile":7,
    "CrossShot":6,
    "DiagonalCrossShot":5,
    "CornerShot":4,
    "DoubleShot(Vertical)":3,
    "DoubleShot(Horizontal)":2
}


def main(player_key):
    global map_size
    global opponent_ships
    global our_ships
    global energy
    global shield
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    opponent_ships = state['OpponentMap']['Ships']
    if state['Phase'] == 1:
        place_ships()
    else:
        our_ships = state['PlayerMap']['Owner']['Ships']
        energy = state['PlayerMap']['Owner']['Energy']
        shield = state['PlayerMap']['Owner']['Shield']
        fire_shot(state['OpponentMap']['Cells'])

def search_weapon(type, weapons):
    for weapon in weapons:
        if weapon["WeaponType"]==type and energy>=weapon["EnergyRequired"]:
            return move_type[type]
        else:
            move = 1
    return move

def search_ship(type):
    for ship in our_ships:
        if ship["ShipType"]==type:
            return ship

def output_shot(x, y):
    submarine = search_ship("Submarine")
    cruiser = search_ship("Cruiser")
    battleship = search_ship("Battleship")
    carrier = search_ship("Carrier")
    destroyer = search_ship("Destroyer")
    if not submarine["Destroyed"]:
        move = search_weapon("SeekerMissile",submarine["Weapons"])
    elif not cruiser["Destroyed"]:
        move = search_weapon("CrossShot",cruiser["Weapons"])
    elif not battleship["Destroyed"]:
        move = search_weapon("DiagonalCrossShot",battleship["Weapons"])
    elif not carrier["Destroyed"]:
        move = search_weapon("CornerShot",carrier["Weapons"])
    elif not destroyer["Destroyed"]:
        move = search_weapon("DoubleShot(Vertical)",destroyer["Weapons"])
    else:
        move = 1
    coord = is_got_hit()
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        if coord[0]==-1 or shield["Active"] or shield["CurrentCharges"]<=4:
            f_out.write('{},{},{}'.format(move, x, y))
        else:
            f_out.write('{},{},{}'.format(8, coord[0], coord[1]))
        f_out.write('\n')
    pass

def is_got_hit():
    for ship in our_ships:
        if not ship["Destroyed"]:
            for body_cell in ship["Cells"]:
                if body_cell["Hit"]:
                    return (body_cell['X'],body_cell['Y'])
    return (-1, -1)

def search_point(x, y, opponent_map):
    for cell in opponent_map:
        if cell['X']==x and cell['Y']==y:
            return cell

def array_points(ax, ay, var, vertical):
    x=ax
    y=ay
    is_two = 0
    up = 0
    temp = 0
    start = 0
    if vertical==0:
        lp = []
        lp.append([x, y])
        while y < map_size:
            x+=2
            if x>map_size-1:
                is_two+=1
                if is_two == 1:
                    temp+=1
                    y+=1
                else:
                    y+=var-1
                    is_two = 0 
                if y%2 == 1:
                    x=ax+1
                else:
                    x=ax
            if x< map_size and y<map_size :
                lp.append([x, y])
        return lp
    else:
        lp = []
        lp.append([x, y])
        while x < map_size:
            y+=2
            if y>map_size-1:
                x+=var
                y=ay
            if x< map_size and y<map_size :
                lp.append([x, y])
        return lp

def destroyed_ship():
    var = 0
    for ship in opponent_ships:
        if ship['ShipType']=='Carrier' and not ship['Destroyed'] and var <=5:
            var = 5
        elif ship['ShipType']=='Battleship' and not ship['Destroyed'] and var <=4:
            var = 4
        elif (ship['ShipType']=='Cruiser' or ship['ShipType']=='Submarine') and not ship['Destroyed'] and var <=3:
            var = 3
        elif ship['ShipType']=='Destroyer' and not ship['Destroyed'] and var <=2:
            var = 2
    return var

def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    targets = []
    x = 0
    y = 0
    var = destroyed_ship()
    for cell in opponent_map:
        if cell['Damaged']:
            left_cell = {"Damaged":False, "ShieldHit":False}
            right_cell = {"Damaged":False, "ShieldHit":False}
            top_cell = {"Damaged":False, "ShieldHit":False}
            bot_cell = {"Damaged":False, "ShieldHit":False}
            if cell['X']-1 >=0:
                left_cell = search_point(cell['X']-1, cell['Y'],opponent_map)
            if cell['X']+1 < map_size:
                right_cell = search_point(cell['X']+1, cell['Y'],opponent_map)
            if cell['Y']+1 < map_size:
                top_cell = search_point(cell['X'], cell['Y']+1,opponent_map)
            if cell['Y']-1 >=0:
                bot_cell = search_point(cell['X'], cell['Y']-1,opponent_map)
            if left_cell['Damaged'] or right_cell['Damaged']:
                sbx = [1,-1]
                sby = [0,0]
            elif top_cell['Damaged'] or bot_cell['Damaged']:
                sbx = [0,0]
                sby = [1,-1]
            else:
                sbx = [1,-1,0,0]
                sby = [0,0,1,-1]
            for i in range(0, len(sbx)):
                tx = cell['X']+sbx[i]
                ty = cell['Y']+sby[i]
                if tx >= 0 and ty >=0 and tx < map_size and ty < map_size:
                    next_cell = search_point(tx, ty, opponent_map)
                    if not next_cell['Damaged'] and not next_cell['Missed']:
                        target = tx, ty
                        output_shot(*target)
                        return
    while (var > 0):
        var = destroyed_ship()
        lp = []
        lp = array_points(x, y, var, 0)
        for i in range(0,len(lp)):
            next_cell = search_point(lp[i][0], lp[i][1], opponent_map)
            if not next_cell['Damaged'] and not next_cell['Missed']:
                valid_cell = next_cell['X'], next_cell['Y']
                target = valid_cell
                output_shot(*target)
                return
        y+=2

def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west
    if map_size == 14:
        ships = ['Carrier 12 12 south',
                 'Battleship 0 0 north',
                 'Submarine 1 12 east',
                 'Cruiser 13 0 north',
                 'Destroyer 6 7 east'
                 ]
    elif map_size == 10:
        ships = ['Carrier 8 8 south',
                 'Battleship 0 0 north',
                 'Submarine 1 8 east',
                 'Cruiser 9 0 north',
                 'Destroyer 5 5 east'
                 ]
    else:
        ships = ['Carrier 5 5 south',
                 'Battleship 0 0 north',
                 'Submarine 1 5 east',
                 'Cruiser 6 0 north',
                 'Destroyer 2 3 east'
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
