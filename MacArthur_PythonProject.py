import pygame
import random
import os
import time


def load_image(name, colorkey):
    image = pygame.image.load(name).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        elif colorkey == -2:
            image.set_alpha(80)
        elif colorkey == -3:
            image.set_alpha(125)
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    image.set_colorkey(colorkey)
    return image

def write(words, color, x, y, size):
    font = pygame.font.Font(None, size)
    text = font.render(words, 1, color)
    text_x = x
    text_y = y
    screen.blit(text, (text_x, text_y))

def draw_all():
    screen.blit(back_image, (480, 120))
    board.render()
    map_sprites.draw(screen)
    for i in range(len(all_buildings)):
        building_sprites.sprites()[i].rect.x = all_buildings[i]['pos_x']
        building_sprites.sprites()[i].rect.y = all_buildings[i]['pos_y']
    for i in range(len(all_units)):
        unit_sprites.sprites()[i].rect.x = all_units[i]['pos_x']
        unit_sprites.sprites()[i].rect.y = all_units[i]['pos_y']
    building_sprites.draw(screen)
    unit_sprites.draw(screen)
    for i in range(len(unit_sprites.sprites())):
        if all_units[i]['MP'] > 0 and player == all_units[i]['team']:
            screen.blit(yellow, (all_units[i]['pos_x'] // 60 * 60, all_units[i]['pos_y'] // 60 * 60))
        pygame.draw.rect(screen, (255, 0, 0),
                         (all_units[i]['pos_x'] // 60 * 60 + 3, all_units[i]['pos_y'] // 60 * 60,
                          int(all_units[i]['HP'] / all_units[i]['maxHP'] * 54), 4), 0)
    screen.blit(next_image, (1320, 0))
    screen.blit(money_image, (0, 660))
    write(str(resources[f'money{player}']), (255, 255, 0), 5, 665, 40)
    write('+' + str(resources[f'+money{player}']), (255, 255, 0), 150, 665, 25)
    screen.blit(prod_image, (240, 660))
    write(str(resources[f'prod{player}']), (255, 150, 0), 245, 665, 40)
    write('+' + str(resources[f'+prod{player}']), (255, 150, 0), 390, 665, 25)
    screen.blit(food_image, (480, 660))
    write(str(resources[f'food{player}']), (0, 255, 0), 485, 665, 40)
    needFood = 0
    for j in range(len(all_units)):
        if player == all_units[j]['team']:
            needFood += all_units[j]['price_f']
    if resources[f'+food{player}'] - needFood >= 0:
        write('+' + str(resources[f'+food{player}'] - needFood), (0, 255, 0), 630, 665, 25)
    else:
        write(str(resources[f'+food{player}'] - needFood), (0, 255, 0), 630, 665, 25)
    if player == 1:
        screen.blit(eng_image, (1320, 180))
    elif player == 2:
        screen.blit(fr_image, (1320, 180))

def drawStartFon():
    image = load_image("data/ArishaFon2.png", colorkey=None)
    screen.blit(image, (0, 0))
    image = load_image("data/Logo2.png", colorkey=-1)
    screen.blit(image, (40, 110))
    image = load_image("data/startButton.png", colorkey=None)
    screen.blit(image, (60, 300))
    image = load_image("data/titButton.png", colorkey=None)
    screen.blit(image, (60, 370))
    image = load_image("data/exitButton.png", colorkey=None)
    screen.blit(image, (60, 440))

def unit_add(n):
    unit_image = load_image(all_units[n]['name'], colorkey=-1)
    if 'Tower' not in all_units[n]['name']:
        unit_image = pygame.transform.scale(unit_image, (50, 50))
    unit = pygame.sprite.Sprite(unit_sprites)
    unit.image = unit_image
    unit.rect = unit.image.get_rect()
    unit.rect.x = all_units[n]['pos_x']
    unit.rect.y = all_units[n]['pos_y']

def build_add(n):
    building_image = load_image(all_buildings[n]['name'], colorkey=-1)
    building = pygame.sprite.Sprite(building_sprites)
    building.image = building_image
    building.rect = building.image.get_rect()
    building.rect.x = all_buildings[n]['pos_x']
    building.rect.y = all_buildings[n]['pos_y']

def poln(i, name):
    pol = 0
    for j in range(len(all_units)):
        if (all_buildings[i]['pos_x'], all_buildings[i]['pos_y']) == (
        all_units[j]['pos_x'] - 5, all_units[j]['pos_y'] - 5):
            all_buildings[i]['occupation'] = 1
            if all_buildings[i]['team'] != all_units[j]['team']:
                unteam = all_units[j]['team']
                buteam = all_buildings[i]['team']
                all_buildings[i]['team'] = unteam
                if unteam in [1, 2]:
                    resources[f'+money{unteam}'] += all_buildings[i]['+money']
                    resources[f'+prod{unteam}'] += all_buildings[i]['+prod']
                    resources[f'+food{unteam}'] += all_buildings[i]['+food']
                if buteam in [1, 2]:
                    resources[f'+money{buteam}'] -= all_buildings[i]['+money']
                    resources[f'+prod{buteam}'] -= all_buildings[i]['+prod']
                    resources[f'+food{buteam}'] -= all_buildings[i]['+food']
                if 'City' in name:
                    city_image = load_image(f"data/City{all_units[j]['team']}.png", colorkey=-1)
                    building_sprites.sprites()[i].image = city_image
            pol = 1
            break
    if pol == 0:
        all_buildings[i]['occupation'] = 0

def factor(attacker, defender):
    k = 1
    p = 0
    at_name = all_units[attacker]['name'][5:-4]
    def_name = all_units[defender]['name'][5:-4]
    unitBiom = game_map[all_units[attacker]['pos_y'] // 60][all_units[attacker]['pos_x'] // 60]
    if at_name[-1] == '2':
        at_name = at_name[:-1]
    if def_name[-1] == '2':
        def_name = def_name[:-1]
    at_team = all_units[attacker]['team']
    if 'water' in unitBiom:
        print('Водичка')
        if 'Admiral' in at_name:
            k *= 3
        elif at_name not in ['Medic', 'Dragon', 'Fighter', 'Apostle', 'Caravel', 'Frigate', 'Turtle', 'Aircraft', 'Bismarck']:
            k *= 0.6
    elif 'desert' in unitBiom and 'Varu' in at_name:
        k *= 1.3
    for i in range(len(all_buildings)):
        if (all_buildings[i]['pos_x'] // 60, all_buildings[i]['pos_y'] // 60) == (all_units[defender]['pos_x'] // 60, all_units[defender]['pos_y'] // 60):
            if 'Gradoboy' in at_name:
                k *= 1.3
        if (all_buildings[i]['pos_x'] // 60, all_buildings[i]['pos_y'] // 60) == (all_units[attacker]['pos_x'] // 60, all_units[attacker]['pos_y'] // 60):
            p += all_buildings[i]['damage+']
    if 'Antiair' in at_name and def_name in ['Dragon', 'Fighter']:
        k *= 4
    if 'Inquisitor' in at_name and def_name in ['Dragon', 'Varu', 'Mamluk', 'Cock']:
        k *= 1.7
    if def_name in ['Dragon', 'Fighter'] and at_name not in ['Archer', 'Catapult', 'Medic', 'Dragon', 'Antiair',
                                                             'Gradoboy', 'WTF', 'Inquisitor', 'Fighter',
                                                             'Tower', 'Frigate', 'Aircraft']:
        k, p = 0, 0
    if at_team in [1, 2]:
        needFood = 0
        for j in range(len(all_units)):
            if player == all_units[j]['team']:
                needFood += all_units[j]['price_f']
        if resources[f'+food{at_team}'] - needFood < 0:
            if resources[f'food{at_team}'] <= 0:
                if 'Hussar' not in at_name:
                    k *= 0.4
                else:
                    k *= 0.2
                print('Голодомор')
            else:
                if 'Hussar' not in at_name:
                    k *= 0.7
                else:
                    k *= 0.9
                print('Прорвёмся')
    print(k, p)
    return k, p

def moveChun(n):
    chun_x = all_units[n]['pos_x'] // 60
    chun_y = all_units[n]['pos_y'] // 60
    able_to_move = []
    able_to_attack = []
    if "Bismarck" in all_units[n]['name']:
        for i in range(len(all_units)):
            if i != n:
                def_x = all_units[i]['pos_x'] // 60
                def_y = all_units[i]['pos_y'] // 60
                if abs(def_x - chun_x) <= 1 and abs(def_y - chun_y) <= 1 and all_units[i]['team'] != 3:
                    all_units[i]['HP'] -= 45
                    print('Атака пулемётов')
                if abs(def_x - chun_x) <= all_units[n]['range'] and abs(def_y - chun_y) <= all_units[n]['range'] and\
                        abs(def_x - chun_x) + abs(def_y - chun_y) > 0 and all_units[i]['team'] != 3:
                    able_to_attack.append(i)
        if len(able_to_attack) > 0:
            all_units[random.choice(able_to_attack)]['HP'] -= all_units[n]['damage']
            print('Атака тяжёлых орудий')
    for i in range(max(0, chun_y - all_units[n]['move']), min(10, chun_y + all_units[n]['move']) + 1):
        for j in range(max(0, chun_x - all_units[n]['move']), min(21, chun_x + all_units[n]['move']) + 1):
            if ('water' in game_map[i][j] and 'Bismarck' in all_units[n]['name']) or 'Telega' in all_units[n]['name']:
                occup = 0
                for k in range(len(all_units)):
                    if (all_units[k]['pos_y'] // 60, all_units[k]['pos_x'] // 60) == (i, j):
                        occup = 1
                        break
                if occup == 0:
                    able_to_move.append((i, j))
    print(able_to_move)
    if len(able_to_move) > 0:
        chun_move = random.choice(able_to_move)
        all_units[n]['pos_x'] = chun_move[1] * 60 + 5
        all_units[n]['pos_y'] = chun_move[0] * 60 + 5


class Board:
    biom = ["grass", "grass", "desert", "grass", "water", "grass", "grass", "water", "grass", "water", "desert", "grass"]
    create_or_not = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.cell_size = 60

    def set_view(self, cell_size):
        self.cell_size = cell_size

    def render(self):
        for i in range(self.height):
            if self.create_or_not == 0:
                game_map.append([])
            for j in range(self.width):
                if self.create_or_not == 0:
                    game_map[i].append(random.choice(self.biom))
        for i in range(self.height):
            for j in range(self.width):
                if self.create_or_not == 0:
                    if i < self.height - 1 and j < self.width - 1:
                        if game_map[i][j] == game_map[i + 1][j + 1] and \
                                game_map[i][j] != "grass":
                            game_map[i][j + 1] = game_map[i][j]
                    if 0 < i < self.height - 1 and 0 < j < self.width - 1:
                        if game_map[i - 1][j] == game_map[i + 1][j] and \
                                game_map[i - 1][j] != "grass":
                            game_map[i][j] = game_map[i - 1][j]
                        if game_map[i][j - 1] == game_map[i][j + 1] and \
                                game_map[i][j - 1] != "grass":
                            game_map[i][j] = game_map[i][j - 1]
                    if (i == 0 and j == 0) or (i == self.height - 1 and j == self.width - 1):
                        game_map[i][j] = "grass"
                    map_image = load_image(f"data/{game_map[i][j]}.png", colorkey=None)
                    map_image = pygame.transform.scale(map_image, (60, 60))
                    map = pygame.sprite.Sprite(map_sprites)
                    map.image = map_image
                    map.rect = map.image.get_rect()
                    map.rect.x = j * 60
                    map.rect.y = i * 60
        self.create_or_not = 1

    def get_click(self, mouse_pos):
        global move, unitNumber, stady_of_game, cityNumber, player

        cord = (mouse_pos[0] // self.cell_size, mouse_pos[1] // self.cell_size)
        su = 0
        for i in range(len(all_buildings)):
            if (cord[0] * self.cell_size, cord[1] * self.cell_size) == (all_buildings[i]['pos_x'], all_buildings[i]['pos_y']):
                poln(i, all_buildings[i]['name'])
                if all_buildings[i]['occupation'] == 0 and move == 0 and all_buildings[i]['team'] == player:
                    if 'City' in all_buildings[i]['name']:
                        stady_of_game = 2
                    elif 'Ship' in all_buildings[i]['name']:
                        stady_of_game = 4
                    cityNumber = i
                    break
        for i in range(len(all_units)):
            if move == 0 and all_units[i]['MP'] > 0 and\
                    cord == (all_units[i]['pos_x'] // 60, all_units[i]['pos_y'] // 60)\
                    and all_units[i]['team'] == player:
                move = 1
                su = -1
                unitNumber = i
                print('Выбрано')
                break
            elif move == 1\
                    and cord != (all_units[i]['pos_x'] // self.cell_size, all_units[i]['pos_y'] // self.cell_size):
                MP = min(all_units[unitNumber]['move'], all_units[unitNumber]['MP'])
                if abs(cord[0] - all_units[unitNumber]['pos_x'] // self.cell_size) <= MP \
                    and abs(cord[1] - all_units[unitNumber]['pos_y'] // self.cell_size) <= MP\
                    and cord[0] <= 21 and cord[1] <= 10:
                    su += 1
            elif move == 1 and (cord[0], cord[1]) == (all_units[i]['pos_x'] // self.cell_size,
                                    all_units[i]['pos_y'] // self.cell_size) and all_units[unitNumber]['MP'] > 0 and\
                    abs(all_units[i]['pos_x'] // 60 - all_units[unitNumber]['pos_x'] // 60) <= all_units[unitNumber]['range'] and\
                    abs(all_units[i]['pos_y'] // 60 - all_units[unitNumber]['pos_y'] // 60) <= all_units[unitNumber]['range'] and\
                    i != unitNumber and\
                        ((all_units[i]['team'] != all_units[unitNumber]['team'] and "Medic" not in all_units[unitNumber]['name'])
                         or (all_units[i]['team'] == all_units[unitNumber]['team'] and "Medic" in all_units[unitNumber]['name'])):
                fact = factor(unitNumber, i)
                if fact[0] != 0:
                    all_units[i]['HP'] -= int(all_units[unitNumber]['damage'] * fact[0] + fact[1])
                    if all_units[i]['HP'] > all_units[i]['maxHP']:
                        all_units[i]['HP'] = all_units[i]['maxHP']
                    all_units[unitNumber]['MP'] = 0
                    print('Совершена атака')
                    if all_units[i]['HP'] <= 0:
                        name = all_units[unitNumber]['name'][5:-4]
                        if name[-1] == '2':
                            name = name[:-1]
                        if name in ["Knight", "Horseman", "Hussar", "Tank"]:
                            all_units[unitNumber]['MP'] = 2
                        elif "Cock" in name:
                            all_units[unitNumber]['HP'] += 15
                            all_units[unitNumber]['maxHP'] += 15
                        if "Bismarck" in all_units[i]['name']:
                            if player == 1:
                                presUnits['Fighter'] += 1
                            elif player == 2:
                                presUnits['Fighter2'] += 1
                        elif "Telega" in all_units[i]['name']:
                            if player == 1:
                                presUnits['Inquisitor'] += 1
                            elif player == 2:
                                presUnits['Inquisitor2'] += 1
                        unit_sprites.sprites()[i].kill()
                        del all_units[i]
                        if name not in ['Archer', 'Catapult', 'Dragon', 'Gradoboy', 'Antiair', 'WTF', 'Frigate', 'Antiair', 'Inquisitor', 'Fighter']:
                            su = len(all_units)
                        print('Убит')
                        if i < unitNumber:
                            unitNumber -= 1
                        for key in bossNumbers:
                            if i < bossNumbers[key]:
                                bossNumbers[key] -= 1
                                print('OK')
                    else:
                        name = all_units[unitNumber]['name'][5:-4]
                        if name[-1] == '2':
                            name = name[:-1]
                        if name not in ['Archer', 'Catapult', 'Antiair', 'Gradoboy', 'Fighter', 'WTF', 'Tower', 'Medic', 'Dragon', 'Inquisitor', 'Frigate', 'Aircraft']:
                            print(name)
                            if fact[0] != 0 and 'Telega' not in all_units[i]['name'] and 'Medic' not in all_units[i]['name']:
                                fact = factor(i, unitNumber)
                                all_units[unitNumber]['HP'] -= int(all_units[i]['damage'] * fact[0] + fact[1]) // 2
                    if all_units[unitNumber]['HP'] <= 0:
                        unit_sprites.sprites()[unitNumber].kill()
                        print('Обосрался')
                        del all_units[unitNumber]
                        for key in bossNumbers:
                            if unitNumber < bossNumbers[key]:
                                bossNumbers[key] -= 1
                                print('OK')
                move = 0
                break
        if su == len(all_units):
            name = all_units[unitNumber]['name'][5:-4]
            if name[-1] == '2':
                name = name[:-1]
            if (name in ['Caravel', 'Frigate', 'Turtle', 'Aircraft'] and "water" in game_map[cord[1]][cord[0]]) or\
                                        name not in ['Caravel', 'Frigate', 'Turtle', 'Aircraft']:
                all_units[unitNumber]['MP'] -= max(abs(cord[0] - (all_units[unitNumber]['pos_x'] // 60)),
                                                abs(cord[1] - (all_units[unitNumber]['pos_y'] // 60)))
                all_units[unitNumber]['pos_x'], all_units[unitNumber]['pos_y'] = cord[0] * self.cell_size + 5,\
                                                                     cord[1] * self.cell_size + 5
                print('Ход сделан')
            move = 0
        elif 0 <= su < len(all_units):
            move = 0
        return cord


class cityChose:
    def get_click(self, mouse_pos):
        global unitNumber, move, stady_of_game, cityNumber, player, level_of_chose

        chosedUnit = ""
        if 1125 <= mouse_pos[0] and mouse_pos[1] <= 630:
            if 30 < mouse_pos[1] <= 90:
                if level_of_chose == 1:
                    if stady_of_game == 2:
                        chosedUnit = "data/Liver.png"
                    elif stady_of_game == 4:
                        chosedUnit = "data/Caravel.png"
                elif level_of_chose == 2 and stady_of_game == 2:
                    chosedUnit = "data/Admiral.png"
                elif level_of_chose == 3 and stady_of_game == 2:
                    if player == 1 and presUnits['Inquisitor'] > 0:
                        chosedUnit = "data/Inquisitor.png"
                        presUnits['Inquisitor'] -= 1
                    elif player == 2 and presUnits['Inquisitor2'] > 0:
                        chosedUnit = "data/Inquisitor.png"
                        presUnits['Inquisitor2'] -= 1
            elif 90 < mouse_pos[1] <= 150:
                if level_of_chose == 1:
                    if stady_of_game == 2:
                        chosedUnit = "data/Builder.png"
                    elif stady_of_game == 4:
                        chosedUnit = "data/Frigate.png"
                elif level_of_chose == 2 and stady_of_game == 2:
                    chosedUnit = "data/Hussar.png"
                elif level_of_chose == 3 and stady_of_game == 2:
                    if player == 1 and presUnits['Fighter'] > 0:
                        chosedUnit = "data/Fighter.png"
                        presUnits['Fighter'] -= 1
                    elif player == 2 and presUnits['Fighter2'] > 0:
                        chosedUnit = "data/Fighter.png"
                        presUnits['Fighter2'] -= 1
            elif 150 < mouse_pos[1] <= 210:
                if level_of_chose == 1:
                    if stady_of_game == 2:
                        chosedUnit = "data/Swordman.png"
                    elif stady_of_game == 4:
                        chosedUnit = "data/Turtle.png"
                elif level_of_chose == 2 and stady_of_game == 2:
                    chosedUnit = "data/Dragon.png"
            elif 210 < mouse_pos[1] <= 270 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Archer.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Antiair.png"
            elif 270 < mouse_pos[1] <= 330 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Horseman.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Gradoboy.png"
            elif 330 < mouse_pos[1] <= 390 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Knight.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Cock.png"
            elif 390 < mouse_pos[1] <= 450 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Catapult.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Mamluk.png"
            elif 450 < mouse_pos[1] <= 510 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Scout.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Apostle.png"
            elif 510 < mouse_pos[1] <= 570 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Medic.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/Varu.png"
            elif 570 < mouse_pos[1] <= 630 and stady_of_game == 2:
                if level_of_chose == 1:
                    chosedUnit = "data/Enginer.png"
                elif level_of_chose == 2:
                    chosedUnit = "data/WTF.png"
            stady_of_game = 1
            level_of_chose = 1
        elif 1125 <= mouse_pos[0] and mouse_pos[1] > 630:
            level_of_chose += 1
            if (level_of_chose > 4 and stady_of_game == 2) or (level_of_chose > 2 and stady_of_game == 4):
                level_of_chose = 1
        elif 120 < mouse_pos[0] < 140 and 540 < mouse_pos[1] < 560:
            if stady_of_game == 2:
                chosedUnit = "data/Tank.png"
            elif stady_of_game == 4:
                chosedUnit = "data/Aircraft.png"
            stady_of_game = 1
            level_of_chose = 1
        else:
            stady_of_game = 1
            level_of_chose = 1
        if all_buildings[cityNumber]['team'] == 2 and chosedUnit != "":
            chosedUnit = chosedUnit[:-4] + '2' + chosedUnit[-4:]
        if chosedUnit != "":
            for i in range(len(all_units_kinds)):
                if all_units_kinds[i]['name'][5:-4] in chosedUnit and\
                        resources[f'money{player}'] - all_units_kinds[i]['price_m'] >= 0\
                        and resources[f'prod{player}'] - all_units_kinds[i]['price_p'] >= 0:
                    resources[f'money{player}'] -= all_units_kinds[i]['price_m']
                    resources[f'prod{player}'] -= all_units_kinds[i]['price_p']
                    if "WTF" in all_units_kinds[i]['name'][5:-4]:
                        HP = random.randint(40, 220)
                        MP = random.randint(1, 4)
                        all_units.append(
                            {'name': chosedUnit, 'pos_x': all_buildings[cityNumber]['pos_x'] + 5,
                             'pos_y': all_buildings[cityNumber]['pos_y'] + 5,
                             'damage': random.randint(10, 90), 'HP': HP,
                             'move': MP, 'range': random.randint(1, 2),
                             'maxHP': HP, 'team': all_buildings[cityNumber]['team'], 'MP': 0, 'startMP': MP,
                             'price_m': all_units_kinds[i]['price_m'], 'price_p': all_units_kinds[i]['price_p'],
                             'price_f': all_units_kinds[i]['price_f']})
                    else:
                        all_units.append(
                            {'name': chosedUnit, 'pos_x': all_buildings[cityNumber]['pos_x'] + 5, 'pos_y': all_buildings[cityNumber]['pos_y'] + 5,
                             'damage': all_units_kinds[i]['damage'], 'HP': all_units_kinds[i]['HP'], 'move': all_units_kinds[i]['move'],
                             'range': all_units_kinds[i]['range'], 'maxHP': all_units_kinds[i]['maxHP'],
                             'team': all_buildings[cityNumber]['team'], 'MP': 0, 'startMP': all_units_kinds[i]['startMP'],
                             'price_m': all_units_kinds[i]['price_m'], 'price_p': all_units_kinds[i]['price_p'],
                             'price_f': all_units_kinds[i]['price_f']})
                    unit_add(-1)
                    move = 0
                    print('Юнит создан')
                    break
        return cord


class buildChose:
    def get_click(self, mouse_pos):
        global unitNumber, move, stady_of_game, cityNumber, player, level_of_chose

        chosedBuilding = ""
        if 1125 <= mouse_pos[0] and mouse_pos[1] <= 630:
            if 30 < mouse_pos[1] <= 90:
                if level_of_chose == 1:
                    if stady_of_game == 3:
                        chosedBuilding = "data/Tower.png"
                    elif stady_of_game == 6:
                        chosedBuilding = "data/Market.png"
            elif 90 < mouse_pos[1] <= 150:
                if level_of_chose == 1:
                    if stady_of_game == 3:
                        chosedBuilding = "data/Wall.png"
                    elif stady_of_game == 6:
                        chosedBuilding = "data/Workshop.png"
            elif 150 < mouse_pos[1] <= 210:
                if level_of_chose == 1:
                    if stady_of_game == 3:
                        chosedBuilding = "data/Shipyard.png"
                    elif stady_of_game == 6:
                        chosedBuilding = "data/Bank.png"
            elif 210 < mouse_pos[1] <= 270:
                if level_of_chose == 1 and stady_of_game == 6:
                    chosedBuilding = "data/Factory.png"
            elif 270 < mouse_pos[1] <= 330:
                if level_of_chose == 1 and stady_of_game == 6:
                    chosedBuilding = "data/Farm.png"
            elif 330 < mouse_pos[1] <= 390:
                if level_of_chose == 1 and stady_of_game == 6:
                    chosedBuilding = "data/Mill.png"
            elif 390 < mouse_pos[1] <= 450:
                if level_of_chose == 1 and stady_of_game == 6:
                    chosedBuilding = "data/Shipmayak.png"
            stady_of_game = 1
            level_of_chose = 1
        elif 1125 <= mouse_pos[0] and mouse_pos[1] > 630:
            level_of_chose += 1
            if level_of_chose > 2:
                level_of_chose = 1
        else:
            stady_of_game = 1
            level_of_chose = 1
        if chosedBuilding != "":
            move = 0
            can_build = 0
            x = all_units[unitNumber]['pos_x'] // 60
            y = all_units[unitNumber]['pos_y'] // 60
            map_around_unit = []
            if y > 0:
                map_around_unit.append(game_map[y - 1][x])
            if y < 10:
                map_around_unit.append(game_map[y + 1][x])
            if x > 0:
                map_around_unit.append(game_map[y][x - 1])
            if x < 21:
                map_around_unit.append(game_map[y][x + 1])
            for i in range(len(all_buildings)):
                if 'City' in all_buildings[i]['name'] and all_units[unitNumber]['team'] == all_buildings[i]['team']:
                    if abs(all_units[unitNumber]['pos_x'] // 60 - all_buildings[i]['pos_x'] // 60) <= 1 and\
                            abs(all_units[unitNumber]['pos_y'] // 60 - all_buildings[i]['pos_y'] // 60) <= 1:
                        can_build = 1
            for i in range(len(all_buildings)):
                if all_units[unitNumber]['pos_x'] // 60 == all_buildings[i]['pos_x'] // 60 and \
                        all_units[unitNumber]['pos_y'] // 60 == all_buildings[i]['pos_y'] // 60:
                    can_build = 0
                    break
            for i in range(len(all_units)):
                if all_units[unitNumber]['pos_x'] // 60 == all_units[i]['pos_x'] // 60 and \
                        all_units[unitNumber]['pos_y'] // 60 == all_units[i]['pos_y'] // 60 and \
                        'Tower' in all_units[i]['name']:
                    can_build = 0
                    break
            if can_build == 1 and (("Ship" in chosedBuilding and "water" in game_map[y][x] and\
                                    map_around_unit.count("data/water.png") != len(map_around_unit)) or\
                                   ("Ship" not in chosedBuilding and "water" not in game_map[y][x])):
                if 'Tower' in chosedBuilding and resources[f'money{player}'] - all_units_kinds[-1]['price_m'] >= 0\
                        and resources[f'prod{player}'] - all_units_kinds[-1]['price_p'] >= 0:
                    resources[f'money{player}'] -= all_units_kinds[-1]['price_m']
                    resources[f'prod{player}'] -= all_units_kinds[-1]['price_p']
                    all_units.append({'name': chosedBuilding, 'pos_x': all_units[unitNumber]['pos_x'] - 5,
                                     'pos_y': all_units[unitNumber]['pos_y'] - 5,
                         'damage': all_units_kinds[-1]['damage'], 'HP': all_units_kinds[-1]['HP'],
                         'move': all_units_kinds[-1]['move'], 'range': all_units_kinds[-1]['range'],
                         'maxHP': all_units_kinds[-1]['maxHP'], 'team': player, 'MP': 0, 'startMP': all_units_kinds[-1]['startMP'],
                         'price_m': all_units_kinds[-1]['price_m'], 'price_p': all_units_kinds[-1]['price_p'],
                             'price_f': all_units_kinds[-1]['price_f'] })
                    unit_add(-1)
                    for sprite in unit_sprites.sprites():
                        if unit_sprites.sprites().index(sprite) == unitNumber:
                            sprite.kill()
                            break
                    for key in bossNumbers:
                        if unitNumber < bossNumbers[key]:
                            bossNumbers[key] -= 1
                            print('OK')
                    del all_units[unitNumber]
                    move = 0
                else:
                    for i in range(len(all_buildings_kinds)):
                        if all_buildings_kinds[i]['name'][5:-4] in chosedBuilding and\
                                        resources[f'money{player}'] - all_buildings_kinds[i]['price_m'] >= 0\
                                        and resources[f'prod{player}'] - all_buildings_kinds[i]['price_p'] >= 0:
                            resources[f"+money{player}"] += all_buildings_kinds[i]['+money']
                            resources[f"+prod{player}"] += all_buildings_kinds[i]['+prod']
                            resources[f"+food{player}"] += all_buildings_kinds[i]['+food']
                            resources[f"money{player}"] -= all_buildings_kinds[i]['price_m']
                            resources[f"prod{player}"] -= all_buildings_kinds[i]['price_p']
                            all_buildings.append(
                                {'name': chosedBuilding, 'pos_x': all_units[unitNumber]['pos_x'] - 5, 'pos_y': all_units[unitNumber]['pos_y'] - 5,
                                'occupation': 0, 'team': player, 'damage+': all_buildings_kinds[i]['damage+'], '+money': all_buildings_kinds[i]['+money'],
                                 '+prod': all_buildings_kinds[i]['+prod'], '+food': all_buildings_kinds[i]['+food'],
                                 'price_m': all_buildings_kinds[i]['price_m'], 'price_p': all_buildings_kinds[i]['price_p']})
                            build_add(-1)
                            all_units[unitNumber]['MP'] = 0
                            for sprite in unit_sprites.sprites():
                                if unit_sprites.sprites().index(sprite) == unitNumber:
                                    sprite.kill()
                                    print('Город создан')
                                    break
                            for key in bossNumbers:
                                if unitNumber < bossNumbers[key]:
                                    bossNumbers[key] -= 1
                                    print('OK')
                            del all_units[unitNumber]
                            break
                print('Постройка объекта окончена')
        return cord


pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"
size = 1365, 700
screen = pygame.display.set_mode(size)

unit_sprites = pygame.sprite.Group()
map_sprites = pygame.sprite.Group()
building_sprites = pygame.sprite.Group()
titres_sprites = pygame.sprite.Group()
titres_image = load_image("data/Titres3.png", colorkey=None)
titres = pygame.sprite.Sprite(titres_sprites)
titres.image = titres_image
titres.rect = titres.image.get_rect()
titres.rect.x = -10
titres.rect.y = 300
next_image = load_image("data/nextMoveButton.png", colorkey=None)
money_image = load_image("data/goldLine1.png", colorkey=None)
prod_image = load_image("data/prodLine1.png", colorkey=None)
food_image = load_image("data/foodLine1.png", colorkey=None)
eng_image = load_image("data/England.png", colorkey=None)
fr_image = load_image("data/France.png", colorkey=None)
telWin_image = load_image("data/bismarckChallenge.png", colorkey=None)
bisWin_image = load_image("data/bismarckChallenge2.png", colorkey=None)
back_image = load_image("data/Background_B.png", colorkey=None)
yellow = load_image("data/yellowSQ.jpg", colorkey=-3)
red = load_image("data/redSQ.jpg", colorkey=-3)
red = pygame.transform.scale(red, (60, 60))

all_units = [{'name': "data/Liver.png", 'pos_x': 5, 'pos_y': 5, 'damage': 0, 'HP': 30, 'move': 1, 'range': 0, 'maxHP': 30, 'team': 1, 'MP': 1, 'startMP': 1, 'price_m': 10, 'price_p': 2, 'price_f': 1},
            {'name': "data/Swordman.png", 'pos_x': 65, 'pos_y': 5, 'damage': 48, 'HP': 154, 'move': 1, 'range': 1, 'maxHP': 154, 'team': 1, 'MP': 1, 'startMP': 1, 'price_m': 5, 'price_p': 0, 'price_f': 1},
            {'name': "data/Liver2.png", 'pos_x': 185, 'pos_y': 185, 'damage': 0, 'HP': 30, 'move': 1, 'range': 0, 'maxHP': 30, 'team': 2, 'MP': 1, 'startMP': 1, 'price_m': 10, 'price_p': 2, 'price_f': 1},
            {'name': "data/Swordman2.png", 'pos_x': 1205, 'pos_y': 605, 'damage': 48, 'HP': 154, 'move': 1, 'range': 1, 'maxHP': 154, 'team': 2, 'MP': 1, 'startMP': 1, 'price_m': 5, 'price_p': 0, 'price_f': 1}]
all_units_kinds = [{'name': "data/Liver.png", 'pos_x': 0, 'pos_y': 0, 'damage': 0, 'HP': 30, 'move': 1, 'range': 0, 'maxHP': 30, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 10, 'price_p': 2, 'price_f': 1},
                   {'name': "data/Builder.png", 'pos_x': 0, 'pos_y': 0, 'damage': 0, 'HP': 30, 'move': 1, 'range': 0, 'maxHP': 30, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 4, 'price_p': 1, 'price_f': 1},
                   {'name': "data/Swordman.png", 'pos_x': 0, 'pos_y': 0, 'damage': 46, 'HP': 158, 'move': 1, 'range': 1, 'maxHP': 158, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 5, 'price_p': 0, 'price_f': 1},
                   {'name': "data/Archer.png", 'pos_x': 0, 'pos_y': 0, 'damage': 42, 'HP': 124, 'move': 1, 'range': 1, 'maxHP': 124, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 5, 'price_p': 0, 'price_f': 1},
                   {'name': "data/Horseman.png", 'pos_x': 0, 'pos_y': 0, 'damage': 50, 'HP': 136, 'move': 2, 'range': 1, 'maxHP': 136, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 7, 'price_p': 1, 'price_f': 1},
                   {'name': "data/Knight.png", 'pos_x': 0, 'pos_y': 0, 'damage': 54, 'HP': 150, 'move': 2, 'range': 1, 'maxHP': 150, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 8, 'price_p': 1, 'price_f': 1},
                   {'name': "data/Catapult.png", 'pos_x': 0, 'pos_y': 0, 'damage': 60, 'HP': 112, 'move': 1, 'range': 2, 'maxHP': 112, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 9, 'price_p': 2, 'price_f': 1},
                   {'name': "data/Scout.png", 'pos_x': 0, 'pos_y': 0, 'damage': 28, 'HP': 80, 'move': 3, 'range': 1, 'maxHP': 80, 'team': 0, 'MP': 3, 'startMP': 3, 'price_m': 4, 'price_p': 0, 'price_f': 1},
                   {'name': "data/Medic.png", 'pos_x': 0, 'pos_y': 0, 'damage': -30, 'HP': 80, 'move': 2, 'range': 1, 'maxHP': 80, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 8, 'price_p': 2, 'price_f': 2},
                   {'name': "data/Enginer.png", 'pos_x': 0, 'pos_y': 0, 'damage': 0, 'HP': 30, 'move': 1, 'range': 0, 'maxHP': 30, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 8, 'price_p': 4, 'price_f': 2},
                   {'name': "data/Admiral.png", 'pos_x': 0, 'pos_y': 0, 'damage': 20, 'HP': 120, 'move': 2, 'range': 1, 'maxHP': 120, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 7, 'price_p': 3, 'price_f': 1},
                   {'name': "data/Hussar.png", 'pos_x': 0, 'pos_y': 0, 'damage': 48, 'HP': 132, 'move': 2, 'range': 1, 'maxHP': 132, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 9, 'price_p': 4, 'price_f': 2},
                   {'name': "data/Dragon.png", 'pos_x': 0, 'pos_y': 0, 'damage': 50, 'HP': 180, 'move': 1, 'range': 1, 'maxHP': 180, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 12, 'price_p': 0, 'price_f': 4},
                   {'name': "data/Antiair.png", 'pos_x': 0, 'pos_y': 0, 'damage': 23, 'HP': 100, 'move': 2, 'range': 2, 'maxHP': 100, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 9, 'price_p': 3, 'price_f': 2},
                   {'name': "data/Gradoboy.png", 'pos_x': 0, 'pos_y': 0, 'damage': 50, 'HP': 110, 'move': 1, 'range': 2, 'maxHP': 110, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 10, 'price_p': 3, 'price_f': 1},
                   {'name': "data/Cock.png", 'pos_x': 0, 'pos_y': 0, 'damage': 46, 'HP': 148, 'move': 1, 'range': 1, 'maxHP': 148, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 6, 'price_p': 2, 'price_f': 1},
                   {'name': "data/Mamluk.png", 'pos_x': 0, 'pos_y': 0, 'damage': 40, 'HP': 160, 'move': 1, 'range': 1, 'maxHP': 160, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 8, 'price_p': 2, 'price_f': 1.5},
                   {'name': "data/Apostle.png", 'pos_x': 0, 'pos_y': 0, 'damage': 48, 'HP': 126, 'move': 2, 'range': 1, 'maxHP': 126, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 7, 'price_p': 0, 'price_f': 1},
                   {'name': "data/Varu.png", 'pos_x': 0, 'pos_y': 0, 'damage': 46, 'HP': 180, 'move': 1, 'range': 1, 'maxHP': 180, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 10, 'price_p': 3, 'price_f': 3.5},
                   {'name': "data/WTF.png", 'pos_x': 0, 'pos_y': 0, 'damage': 45, 'HP': 130, 'move': 2, 'range': 2, 'maxHP': 130, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 10, 'price_p': 5, 'price_f': 2},
                   {'name': "data/Inquisitor.png", 'pos_x': 0, 'pos_y': 0, 'damage': 40, 'HP': 110, 'move': 2, 'range': 1, 'maxHP': 110, 'team': 0, 'MP': 2, 'startMP': 2, 'price_m': 0, 'price_p': 0, 'price_f': 2.5},
                   {'name': "data/Fighter.png", 'pos_x': 0, 'pos_y': 0, 'damage': 55, 'HP': 100, 'move': 3, 'range': 1, 'maxHP': 100, 'team': 0, 'MP': 3, 'startMP': 3, 'price_m': 0, 'price_p': 0, 'price_f': 4},
                   {'name': "data/Tank.png", 'pos_x': 0, 'pos_y': 0, 'damage': 200, 'HP': 300, 'move': 5, 'range': 1, 'maxHP': 300, 'team': 0, 'MP': 5, 'startMP': 5, 'price_m': 0, 'price_p': 0, 'price_f': 10},
                   {'name': "data/Aircraft.png", 'pos_x': 0, 'pos_y': 0, 'damage': 120, 'HP': 240, 'move': 1, 'range': 4, 'maxHP': 240, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 0, 'price_p': 0, 'price_f': 9},
                   {'name': "data/Caravel.png", 'pos_x': 0, 'pos_y': 0, 'damage': 56, 'HP': 180, 'move': 1, 'range': 1, 'maxHP': 180, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 9, 'price_p': 6, 'price_f': 3},
                   {'name': "data/Frigate.png", 'pos_x': 0, 'pos_y': 0, 'damage': 64, 'HP': 165, 'move': 1, 'range': 2, 'maxHP': 165, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 11, 'price_p': 9, 'price_f': 3},
                   {'name': "data/Turtle.png", 'pos_x': 0, 'pos_y': 0, 'damage': 26, 'HP': 194, 'move': 1, 'range': 1, 'maxHP': 194, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 9, 'price_p': 9, 'price_f': 2},
                   {'name': "data/Tower.png", 'pos_x': 0, 'pos_y': 0, 'damage': 40, 'HP': 200, 'move': 0, 'range': 1, 'maxHP': 200, 'team': 0, 'MP': 1, 'startMP': 1, 'price_m': 0, 'price_p': 0, 'price_f': 2.5}]
# Тип юнита, местоположение по оси X, местоположение по Y, урон, HP, перемещение, дальность атаки,
# максимальное здоровье, сторона, очки передвижения
all_buildings = []
all_buildings_kinds = [{'name': "data/City.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 6, '+money': 2, '+prod': 2, '+food': 1, 'price_m': 0, 'price_p': 0},
                       {'name': "data/Wall.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 10, '+money': 0, '+prod': 0, '+food': 0, 'price_m': 0, 'price_p': 0},
                       {'name': "data/Shipyard.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 6, '+money': 1, '+prod': 1, '+food': 0, 'price_m': 0, 'price_p': 0},
                       {'name': "data/Market.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 1.5, '+prod': 0, '+food': 0, 'price_m': 0, 'price_p': 15},
                       {'name': "data/Workshop.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 0, '+prod': 1.5, '+food': 0, 'price_m': 15, 'price_p': 0},
                       {'name': "data/Bank.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 2.5, '+prod': 0, '+food': 0, 'price_m': 0, 'price_p': 30},
                       {'name': "data/Factory.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 0, '+prod': 2.5, '+food': 0, 'price_m': 30, 'price_p': 0},
                       {'name': "data/Farm.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 0, '+prod': 0, '+food': 3, 'price_m': 8, 'price_p': 8},
                       {'name': "data/Mill.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 0.5, '+prod': 0.5, '+food': 3, 'price_m': 15, 'price_p': 15},
                       {'name': "data/Shipmayak.png", 'pos_x': 0, 'pos_y': 0, 'occupation': 0, 'team': 0, 'damage+': 3, '+money': 1, '+prod': 0, '+food': 1, 'price_m': 0, 'price_p': 15}]

resources = {'money1': 5, 'money2': 5, 'prod1': 5, 'prod2': 5, 'food1': 5, 'food2': 5,
             '+money1': 0, '+money2': 0, '+prod1': 0, '+prod2': 0, '+food1': 0, '+food2': 0}

bossNumbers = {"Telega": 0, "Bismarck": 0}
presUnits = {'Inquisitor': 0, 'Inquisitor2': 0, 'Fighter': 0, 'Fighter2': 0}
telegaChar = {'name': "data/Telega.png", 'pos_x': 305, 'pos_y': 305, 'damage': 0, 'HP': 500, 'move': 2, 'range': 3, 'maxHP': 500, 'team': 3, 'MP': 1, 'startMP': 1, 'price_m': 0, 'price_p': 0, 'price_f': 0}
bismarckChar = {'name': "data/Bismarck.png", 'pos_x': 305, 'pos_y': 305, 'damage': 80, 'HP': 400, 'move': 1, 'range': 3, 'maxHP': 400, 'team': 3, 'MP': 1, 'startMP': 1, 'price_m': 0, 'price_p': 0, 'price_f': 0}

game_map = []
for i in range(len(all_units)):
    unit_add(i)

board = Board(22, 11)
city_chose = cityChose()
build_chose = buildChose()
running = True

cord = (0, 0)
stady_of_game = 0
level_of_chose = 1
move = 0
clock = pygame.time.Clock()
unitNumber = 0
cityNumber = 0
player = 1
titres_y = 300
chalWindow = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if stady_of_game == 0:
                if 360 >= event.pos[0] >= 60 and 350 >= event.pos[1] >= 300:
                    stady_of_game = 1
                elif 360 >= event.pos[0] >= 60 and 420 >= event.pos[1] > 370:
                    stady_of_game = 7
                elif 360 >= event.pos[0] >= 60 and 490 >= event.pos[1] > 440:
                    running = False
            elif stady_of_game == 1:
                chalWindow = 0
                if event.pos[0] < 1320:
                    cord = board.get_click(event.pos)
                    if move == 0:
                        for i in range(len(all_buildings)):
                            poln(i, all_buildings[i]['name'])
                elif event.pos[0] >= 1320 and event.pos[1] <= 180:
                    move = 0
                    resources[f'money{player}'] += resources[f'+money{player}']
                    resources[f'prod{player}'] += resources[f'+prod{player}']
                    needFood = 0
                    for j in range(len(all_units)):
                        if player == all_units[j]['team']:
                            needFood += all_units[j]['price_f']
                    resources[f'food{player}'] += (resources[f'+food{player}'] - needFood)
                    player += 1
                    if player > 2:
                        player = 1
                        minus = 0
                        ilyaBis = 0
                        bisNumber = 0
                        for j in range(len(all_units)):
                            if all_units[j - minus]['name'][5:-4] in ['Telega', 'Bismarck']:
                                ilyaBis = 1
                                chun = all_units[j - minus]['name'][5:-4]
                        if ilyaBis == 1:
                            print('Bismarck in motion')
                            moveChun(bossNumbers[f"{chun}"])
                        elif ilyaBis == 0:
                            chance = random.randint(1, 20)
                            if 1 <= chance <= 2:
                                if chance == 1:
                                    all_units.append(telegaChar.copy())
                                    chun = telegaChar['name'][5:-4]
                                elif chance == 2:
                                    all_units.append(bismarckChar.copy())
                                    chun = bismarckChar['name'][5:-4]
                                able_to_create = []
                                for i1 in range(11):
                                    for j1 in range(22):
                                        if ('water' in game_map[i1][j1] and 'Bismarck' in all_units[-1]['name']) \
                                                or 'Telega' in all_units[-1]['name']:
                                            occup = 0
                                            for k1 in range(len(all_units)):
                                                if (all_units[k1]['pos_y'] // 60, all_units[k1]['pos_x'] // 60) == (i1, j1):
                                                    occup = 1
                                                    break
                                            if occup == 0:
                                                able_to_create.append((i1, j1))
                                if len(able_to_create) > 0:
                                    chun_create_cord = random.choice(able_to_create)
                                    all_units[-1]['pos_x'] = chun_create_cord[1] * 60 + 5
                                    all_units[-1]['pos_y'] = chun_create_cord[0] * 60 + 5
                                    chalWindow = 1
                                    bossNumbers[f"{chun}"] = len(all_units) - 1
                                    unit_add(-1)
                                else:
                                    del all_units[-1]
                        for j in range(len(all_units)):
                            name = all_units[j - minus]['name'][5:-4]
                            if name[-1] == '2':
                                name = name[:-1]
                            all_units[j - minus]['MP'] = all_units[j - minus]['startMP']
                            if 'desert' in game_map[all_units[j - minus]['pos_y'] // 60][
                                    all_units[j - minus]['pos_x'] // 60] and name not in ['Dragon', 'Fighter']:
                                all_units[j - minus]['HP'] -= 6
                                if 'Mamluk' in name:
                                    all_units[j - minus]['HP'] += 12
                                    if all_units[j - minus]['HP'] > all_units[j - minus]['maxHP']:
                                        all_units[j - minus]['HP'] = all_units[j - minus]['maxHP']
                            if all_units[j - minus]['HP'] <= 0:
                                unit_sprites.sprites()[j - minus].kill()
                                del all_units[j - minus]
                                minus += 1
                                for key in bossNumbers:
                                    if j - minus < bossNumbers[key]:
                                        bossNumbers[key] -= 1
                    print('Следующий ход')
                    if move == 0:
                        for i in range(len(all_buildings)):
                            poln(i, all_buildings[i]['name'])
            elif stady_of_game == 2 or stady_of_game == 4:
                cord = city_chose.get_click(event.pos)
            elif stady_of_game == 3 or stady_of_game == 6:
                cord = build_chose.get_click(event.pos)
            elif stady_of_game == 5:
                running = False
                break
            elif stady_of_game == 7:
                stady_of_game = 0
                titres_y = 300
        if stady_of_game != 7:
            if move == 1 and "Liver" in all_units[unitNumber]['name'] and\
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 3\
                and "water" not in game_map[all_units[unitNumber]['pos_y'] // 60][all_units[unitNumber]['pos_x'] // 60]:
                can_build = 1
                for i in range(len(all_buildings)):
                    if all_units[unitNumber]['pos_x'] // 60 == all_buildings[i]['pos_x'] // 60 and\
                        all_units[unitNumber]['pos_y'] // 60 == all_buildings[i]['pos_y'] // 60:
                        can_build = 0
                        break
                    if 'City' in all_buildings[i]['name']:
                        if abs(all_units[unitNumber]['pos_x'] // 60 - all_buildings[i]['pos_x'] // 60) < 3 and \
                                abs(all_units[unitNumber]['pos_y'] // 60 - all_buildings[i]['pos_y'] // 60) < 3:
                            can_build = 0
                            break
                move = 0
                if can_build == 1:
                    resources[f"+money{player}"] += all_buildings_kinds[0]['+money']
                    resources[f"+prod{player}"] += all_buildings_kinds[0]['+prod']
                    resources[f"+food{player}"] += all_buildings_kinds[0]['+food']
                    all_buildings.append({'name': f"data/City{player}.png", 'pos_x': all_units[unitNumber]['pos_x'] - 5,
                                        'pos_y': all_units[unitNumber]['pos_y'] - 5, 'occupation': 0,
                                          'team': all_units[unitNumber]['team'], 'damage+': all_buildings_kinds[0]['damage+'],
                                          '+money': all_buildings_kinds[0]['+money'], '+prod': all_buildings_kinds[0]['+prod'],
                                          '+food': all_buildings_kinds[0]['+food'], 'price_m': 0, 'price_p': 0})
                    build_add(-1)
                    for sprite in unit_sprites.sprites():
                        if unit_sprites.sprites().index(sprite) == unitNumber:
                            sprite.kill()
                            print('Город создан')
                            break
                    for key in bossNumbers:
                        if unitNumber < bossNumbers[key]:
                            bossNumbers[key] -= 1
                            print('OK')
                    del all_units[unitNumber]
            elif move == 1 and "Enginer" in all_units[unitNumber]['name'] and\
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                move = 0
                stady_of_game = 3
            elif move == 1 and "Builder" in all_units[unitNumber]['name'] and\
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                move = 0
                stady_of_game = 6
            elif event.type == pygame.MOUSEBUTTONDOWN and 4 <= event.button <= 5 and stady_of_game in [2, 3, 4, 6]:
                if stady_of_game == 2:
                    last = 4
                else:
                    last = 2
                if event.button == 4:
                    level_of_chose += 1
                    if level_of_chose > last:
                        level_of_chose = 1
                elif event.button == 5:
                    level_of_chose -= 1
                    if level_of_chose < 1:
                        level_of_chose = last
            if stady_of_game != 5 and stady_of_game != 7:
                screen.fill((0, 0, 0))
            if stady_of_game == 1:
                draw_all()
                if move == 1:
                    unx, uny = all_units[unitNumber]['pos_x'] // 60, all_units[unitNumber]['pos_y'] // 60
                    MP = min(all_units[unitNumber]['move'], all_units[unitNumber]['MP'])
                    image = load_image("data/blueSQ.jpg", colorkey=-2)
                    image = pygame.transform.scale(image, (60, 60))
                    for j in range(max(0, uny - MP), min(11, uny + MP + 1)):
                        for k in range(max(0, unx - MP), min(22, unx + MP + 1)):
                            screen.blit(image, (k * 60, j * 60))
                    for j in range(len(all_units)):
                        if abs(all_units[j]['pos_x'] // 60 - all_units[unitNumber]['pos_x'] // 60) <= all_units[unitNumber]['range'] and\
                            abs(all_units[j]['pos_y'] // 60 - all_units[unitNumber]['pos_y'] // 60) <= all_units[unitNumber]['range'] and\
                                j != unitNumber and\
                            ((all_units[j]['team'] != all_units[unitNumber]['team'] and "Medic" not in all_units[unitNumber]['name'])
                             or (all_units[j]['team'] == all_units[unitNumber]['team'] and "Medic" in all_units[unitNumber]['name'])):
                            screen.blit(red, (all_units[j]['pos_x'] // 60 * 60, all_units[j]['pos_y'] // 60 * 60))
                if chalWindow == 1:
                    if 'Telega' in chun:
                        screen.blit(telWin_image, (340, 160))
                    elif 'Bismarck' in chun:
                        screen.blit(bisWin_image, (340, 160))
            elif stady_of_game == 2:
                draw_all()
                image = load_image(f"data/Chose{level_of_chose}.png", colorkey=None)
                screen.blit(image, (1125, 0))
                if level_of_chose == 1:
                    for i in range(10):
                        write(str(all_units_kinds[i]['price_m']), (255, 255, 0), 1332, i * 60 + 34, 30)
                        write(str(all_units_kinds[i]['price_p']), (255, 150, 0), 1332, i * 60 + 52, 30)
                        write(str(all_units_kinds[i]['price_f']), (0, 255, 0), 1332, i * 60 + 70, 30)
                elif level_of_chose == 2:
                    for i in range(10, 20):
                        write(str(all_units_kinds[i]['price_m']), (255, 255, 0), 1332, (i - 10) * 60 + 34, 30)
                        write(str(all_units_kinds[i]['price_p']), (255, 150, 0), 1332, (i - 10) * 60 + 52, 30)
                        write(str(all_units_kinds[i]['price_f']), (0, 255, 0), 1332, (i - 10) * 60 + 70, 30)
                elif level_of_chose == 3:
                    if player == 1:
                        write(str(presUnits['Inquisitor']), (255, 255, 255), 1325, 37, 40)
                        write(str(presUnits['Fighter']), (255, 255, 255), 1325, 97, 40)
                    elif player == 2:
                        write(str(presUnits['Inquisitor2']), (255, 255, 255), 1325, 37, 40)
                        write(str(presUnits['Fighter2']), (255, 255, 255), 1325, 97, 40)
                    write(str(all_units_kinds[-8]['price_f']), (0, 255, 0), 1325, 62, 40)
                    write(str(all_units_kinds[-7]['price_f']), (0, 255, 0), 1325, 122, 40)
            elif stady_of_game == 3:
                draw_all()
                image = load_image(f"data/enginerChose{level_of_chose}.png", colorkey=None)
                screen.blit(image, (1125, 0))
                if level_of_chose == 1:
                    write(str(all_units_kinds[-1]['price_f']), (0, 255, 0), 1320, 50, 40)
                    for i in range(1, 3):
                        write('+' + str(all_buildings_kinds[i]['+money']), (255, 255, 0), 1325, i * 60 + 34, 30)
                        write('+' + str(all_buildings_kinds[i]['+prod']), (255, 150, 0), 1325, i * 60 + 52, 30)
                        write('+' + str(all_buildings_kinds[i]['+food']), (0, 255, 0), 1325, i * 60 + 70, 30)
            elif stady_of_game == 4:
                draw_all()
                image = load_image(f"data/portChose{level_of_chose}.png", colorkey=None)
                screen.blit(image, (1125, 0))
                if level_of_chose == 1:
                    for i in range(-4, -1):
                        write(str(all_units_kinds[i]['price_m']), (255, 255, 0), 1332, (i + 4) * 60 + 34, 30)
                        write(str(all_units_kinds[i]['price_p']), (255, 150, 0), 1332, (i + 4) * 60 + 52, 30)
                        write(str(all_units_kinds[i]['price_f']), (0, 255, 0), 1332, (i + 4) * 60 + 70, 30)
            elif stady_of_game == 6:
                draw_all()
                image = load_image(f"data/buildChose{level_of_chose}.png", colorkey=None)
                screen.blit(image, (1125, 0))
                if level_of_chose == 1:
                    for i in range(3, len(all_buildings_kinds)):
                        write(str(all_buildings_kinds[i]['price_m']), (255, 255, 0), 1292, (i - 3) * 60 + 37, 40)
                        write(str(all_buildings_kinds[i]['price_p']), (255, 150, 0), 1292, (i - 3) * 60 + 62, 40)
                        write('+' + str(all_buildings_kinds[i]['+money']), (255, 255, 0), 1330, (i - 3) * 60 + 36, 25)
                        write('+' + str(all_buildings_kinds[i]['+prod']), (255, 150, 0), 1330, (i - 3) * 60 + 54, 25)
                        write('+' + str(all_buildings_kinds[i]['+food']), (0, 255, 0), 1330, (i - 3) * 60 + 72, 25)
            elif stady_of_game == 0:
                drawStartFon()
            all_livers = []
            all_cities = []
            for i in range(len(all_units)):
                if 'Liver' in all_units[i]['name']:
                    all_livers.append(all_units[i].copy())
            for i in range(len(all_buildings)):
                if 'City' in all_buildings[i]['name'] or 'Shipyard' in all_buildings[i]['name']:
                    all_cities.append(all_buildings[i].copy())
            if len(all_livers) > 0:
                team = all_livers[0]['team']
                count_teammates = 0
                for i in range(len(all_livers)):
                    if all_livers[i]['team'] == team:
                        count_teammates += 1
                if count_teammates == len(all_livers):
                    liver_winner = team
                else:
                    liver_winner = -1
            else:
                liver_winner = 0
            if len(all_cities) > 0:
                team = all_cities[0]['team']
                count_teammates = 0
                for i in range(len(all_cities)):
                    if all_cities[i]['team'] == team:
                        count_teammates += 1
                if count_teammates == len(all_cities):
                    city_winner = team
                else:
                    city_winner = -1
            else:
                city_winner = 0
            if liver_winner != -1 and city_winner != -1:
                if (liver_winner == city_winner) and liver_winner != -1:
                    image = load_image(f"data/Win{liver_winner}.png", colorkey=None)
                    screen.blit(image, (0, 0))
                    stady_of_game = 5
                elif liver_winner > 0 and city_winner == 0:
                    image = load_image(f"data/Win{liver_winner}.png", colorkey=None)
                    screen.blit(image, (0, 0))
                    stady_of_game = 5
                elif liver_winner == 0 and city_winner > 0:
                    image = load_image(f"data/Win{city_winner}.png", colorkey=None)
                    screen.blit(image, (0, 0))
                    stady_of_game = 5
                elif len(all_livers) == 0 and len(all_cities) == 0:
                    image = load_image("data/Win0.png", colorkey=None)
                    screen.blit(image, (0, 0))
                    stady_of_game = 5
    for key in resources:
        if '+' not in key and resources[key] < 0:
            resources[key] = 0
    if stady_of_game == 7:
        screen.fill((0, 0, 0))
        titres_sprites.sprites()[0].rect.y = titres_y
        titres_sprites.draw(screen)
        titres_y -= 1
        if titres_y < -800:
            drawStartFon()
            stady_of_game = 0
            titres_y = 300
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
