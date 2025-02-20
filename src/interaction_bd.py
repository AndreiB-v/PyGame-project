import src.objects as obj
import src.utils as ut
import src.creatures as cr
import src.map as mp

import pygame as pg


def create_save(cur, dialogs, world, save_id):
    # ДО: сделать хп для игрока (player) и диалоги

    map_class = mp.Map(ut.screen, {'dream': 'location_one/loco1',
                                   'city': 'location_two/loco2'}[world])

    # Добавляем игрока по координатам из карты
    cur.execute('INSERT INTO players(health, x, y, direction) SELECT MAX(Id), ?, ?, ? FROM healths',
                (int(map_class.get_player_start_position()[0]),
                 int(map_class.get_player_start_position()[1]),
                 'right'))

    # Добавляем игрока в локацию
    cur.execute('INSERT INTO locations(player) SELECT MAX(Id) FROM players')  # id последнего добавленного игрока

    location_id = cur.execute('SELECT MAX(Id) FROM locations').fetchone()[0]

    for dialog in dialogs:
        # Добавляем диалоги с привязкой к локации
        cur.execute('''INSERT INTO dialogs(question, x, y, radius, location) VALUES(?, ?, ?, ?, ?)''',
                    (dialog['question'], dialog['x'], dialog['y'], dialog['radius'], location_id))

        # Добавляем ответы с привязкой к диалогу
        for answer in dialog['answers']:
            cur.execute('''INSERT INTO answers(dialog, answer)
                        SELECT MAX(Id), ? FROM dialogs''', (answer,))

    # Добавляем локацию в сохранение
    # print(world)
    cur.execute(f'''UPDATE saves SET {world} = ? WHERE id = ?''', (location_id, save_id))

    return location_id


def create_city_save(save_id, cur):
    cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                (10, 10, 0.2, 15))  # Здоровье игрока в сохранении

    # Сюда добавлять диалоги С НАЧАЛА СЮЖЕТА
    dialogs = [{'question': 'о, привет, сынок',
                'x': 3128 - 300,
                'y': 1512 + 60,
                'radius': 20,  # радиус активации
                'answers': ['куда ты так поздно?', 'и куда ты?']}, ]

    create_save(cur, dialogs, 'city', save_id)


@ut.create_connect
def create_dream_save(player, save_id, cur=None):
    dream_map = mp.Map(ut.screen, "location_one/loco1")

    cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                (player.health.current_health, player.health.max,
                 player.health.factor, player.health.indent))  # Здоровье игрока в сохранении

    # Сюда добавлять диалоги С НАЧАЛА СЮЖЕТА
    dialogs = [{'question': 'ох, спасибо, что помог с этим скелетом. пришлось бы убегать, если бы не ты',
                'x': int(dream_map.get_umiko_position()[0]),
                'y': int(dream_map.get_umiko_position()[1]),
                'radius': 20,  # радиус активации
                'answers': ['где я?']}]

    location_id = create_save(cur, dialogs, 'dream', save_id)

    skeletons = []
    for x, y in dream_map.get_all_monsters_pos():
        skeletons.append({'x': x, 'y': y})

    for skeleton in skeletons:
        cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                    (10, 10, 0.1, 15))  # Здоровье скелета в сохранении

        # Добавляем скелета с привязкой к хп
        cur.execute('''INSERT INTO skeletons(health, x, y, direction, location)
                    SELECT MAX(Id), ?, ?, ?, ? FROM healths''',
                    (skeleton['x'], skeleton['y'], 'right', location_id))


def get_save(location_id, groups, cur):
    # Заполняем диалоги
    dialogs = []
    for dialog in cur.execute('''SELECT id, question, x, y, radius FROM dialogs WHERE location=?''',
                              (location_id,)).fetchall():
        answers = cur.execute('''SELECT answer FROM answers WHERE dialog=?''', (dialog[0],)).fetchall()
        dialogs.append(obj.Dialog(*list(dialog[1:]) + [i[0] for i in answers]))

    # Инициализируем игрока
    x, y, direction, hp = cur.execute('''SELECT x, y, direction, (SELECT current_health FROM healths WHERE id=health)
    FROM players WHERE id=(SELECT player FROM locations WHERE id=?)''', (location_id,)).fetchone()
    player = cr.Player(groups['creatures_group'], (x, y), groups['platforms_group'], groups['deadly_layer'], hp=hp)
    player.direction = direction

    return dialogs, player


@ut.create_connect
def get_dream_save(save_id, cur=None):
    location_id = cur.execute('SELECT dream FROM saves WHERE id=?', (save_id,)).fetchone()[0]
    dream_map = mp.Map(ut.screen, "location_one/loco1")
    map_groups = dream_map.get_groups()

    groups = {'background_layer': map_groups[0],  # Бэкграунд
              'platforms_group': map_groups[1],  # Группа платформ
              'deadly_layer': map_groups[2],  # Смертельные блоки
              'creatures_group': pg.sprite.Group()}  # Все существа

    cr.Yumiko(groups['creatures_group'], dream_map.get_umiko_position(),
              groups['platforms_group'], groups['deadly_layer'])

    obj.Background(ut.load_image("images/background.png"), 0, 0, groups['background_layer'])
    dialogs, player = get_save(location_id, groups, cur)

    player.plot_double_jump = {1: True, 0: False}[
        cur.execute('SELECT double_jump FROM saves WHERE id = ?', (save_id,)).fetchone()[0]]

    skeletons = []
    for x, y, direction, hp in cur.execute('''SELECT x, y, direction, (SELECT current_health 
    FROM healths WHERE id=health) FROM skeletons WHERE location=?''', (location_id,)).fetchall():
        enemy = cr.Enemy(groups['creatures_group'], (x, y), groups['platforms_group'], groups['deadly_layer'], hp=hp)
        enemy.direction = direction
        skeletons.append(enemy)

    return groups, dialogs, player, skeletons, None


@ut.create_connect
def get_city_save(save_id, cur=None):
    location_id = cur.execute('SELECT city FROM saves WHERE id=?', (save_id,)).fetchone()[0]
    city_map = mp.Map(ut.screen, "location_two/loco2")
    map_groups = city_map.get_groups()

    groups = {'back_photo': pg.sprite.Group(),
              'background_layer': map_groups[0],  # Бэкграунд
              'platforms_group': map_groups[1],  # Группа платформ
              'deadly_layer': map_groups[2],  # Смертельные блоки
              'creatures_group': pg.sprite.Group()}  # Все существа

    cr.Mother(groups['creatures_group'], city_map.get_mother(),
              groups['platforms_group'], groups['deadly_layer'])

    # Создаём дождь
    rain = []
    for _ in range(1000):
        rain.append(obj.Drop(city_map.width * 16, city_map.height * 16))
    obj.Background(ut.load_image("maps/location_two/assets/background.png"), 0, 0, groups['back_photo'])
    dialogs, player = get_save(location_id, groups, cur)

    return groups, dialogs, player, None, rain


@ut.create_connect
def location_save(save_id, creatures_group, dialogs, location_name, cur=None):
    location_id = cur.execute(f'SELECT {location_name} FROM saves WHERE id=?', (save_id,)).fetchone()[0]

    for sk_id, health in cur.execute('SELECT id, health FROM skeletons WHERE location=?', (location_id,)).fetchall():
        cur.execute('DELETE FROM skeletons WHERE id=?', (sk_id,)).fetchall()
        cur.execute('DELETE FROM healths WHERE id=?', (health,))

    for creature in creatures_group:
        if creature.__class__.__name__ == 'Player':
            player_id = cur.execute('SELECT player FROM locations WHERE id=?', (location_id,)).fetchone()[0]
            cur.execute('UPDATE players SET x=?, y=?, direction=? WHERE id=?',
                        (creature.rect.x, creature.rect.y, creature.direction, player_id))
            cur.execute('''UPDATE healths SET current_health=? 
                        WHERE id=(SELECT health FROM players WHERE id=?)''',
                        (creature.health.current_health, player_id))

        elif creature.__class__.__name__ == 'Enemy':
            cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                        (creature.health.current_health, creature.health.max,
                         creature.health.factor, creature.health.indent))  # Здоровье скелета в сохранении

            # Добавляем скелета с привязкой к хп
            cur.execute('''INSERT INTO skeletons(health, x, y, direction, location)
                       SELECT MAX(Id), ?, ?, ?, ? FROM healths''',
                        (creature.rect.x, creature.rect.y, creature.direction, location_id))

    for bd_dialog in cur.execute('SELECT id FROM dialogs WHERE location=?', (location_id,)).fetchall():
        cur.execute('DELETE FROM answers WHERE dialog=?', (bd_dialog[0],)).fetchall()
        cur.execute('DELETE FROM dialogs WHERE id=?', (bd_dialog[0],))
    for dialog in dialogs:
        # Добавляем диалоги с привязкой к локации
        cur.execute('''INSERT INTO dialogs(question, x, y, radius, location) VALUES(?, ?, ?, ?, ?)''',
                    (dialog.question, dialog.x, dialog.y, dialog.radius, location_id))

        # Добавляем ответы с привязкой к диалогу
        for answer in dialog.answers:
            cur.execute('''INSERT INTO answers(dialog, answer)
                                SELECT MAX(Id), ? FROM dialogs''', (answer,))


@ut.create_connect
def get_killed_monsters(save_id, cur=None):
    return cur.execute('SELECT killed_monsters FROM saves WHERE id = ?', (save_id,)).fetchone()[0]
