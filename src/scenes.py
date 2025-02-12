import pygame as pg

import objects as obj
import utils as ut
from map import Map
from camera import Camera
from src.creatures import Player, Enemy

save_id = None
last_scene = None


def create_dream_save(save_id, cur):
    dream_map = Map(ut.screen, "loco1")
    cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                (10, 10, 0.2, 15))  # Здоровье игрока в сохранении

    # Добавляем игрока по координатам из карты
    cur.execute('INSERT INTO players(health, x, y, direction) SELECT MAX(Id), ?, ?, ? FROM healths',
                (int(dream_map.get_player_start_position()[0]),  # x игрока
                 int(dream_map.get_player_start_position()[1]),  # y игрока
                 'right'))  # direction игрока

    # Добавляем игрока в локацию
    cur.execute('INSERT INTO locations(player) SELECT MAX(Id) FROM players')  # id последнего добавленного игрока

    location_id = cur.execute('SELECT MAX(Id) FROM locations').fetchone()[0]

    # Сюда добавлять диалоги С НАЧАЛА СЮЖЕТА
    dialogs = [{'question': 'Это диалог',
                'x': int(dream_map.get_umiko_position()[0]),
                'y': int(dream_map.get_umiko_position()[1]),
                'radius': 100 * ut.factor_x,  # радиус активации
                'answers': ['да ну', 'ладно...']}, ]
    for dialog in dialogs:
        # Добавляем диалоги с привязкой к локации
        cur.execute('''INSERT INTO dialogs(question, x, y, radius, location) VALUES(?, ?, ?, ?, ?)''',
                    (dialog['question'], dialog['x'], dialog['y'], dialog['radius'], location_id))

        # Добавляем ответы с привязкой к диалогу
        for answer in dialog['answers']:
            cur.execute('''INSERT INTO answers(dialog, answer)
                        SELECT MAX(Id), ? FROM dialogs''', (answer,))

    skeletons = [{'x': int(dream_map.get_player_start_position()[0]),
                  'y': int(dream_map.get_player_start_position()[1])},
                 {'x': 557,
                  'y': 1138}]
    for skeleton in skeletons:
        cur.execute('INSERT INTO healths(current_health, max_health, size_factor, indent) VALUES(?, ?, ?, ?)',
                    (10, 10, 0.1, 15))  # Здоровье скелета в сохранении

        # Добавляем скелета с привязкой к хп
        cur.execute('''INSERT INTO skeletons(health, x, y, direction, location)
                    SELECT MAX(Id), ?, ?, ?, ? FROM healths''',
                    (skeleton['x'], skeleton['y'], 'right', location_id))

    # Добавляем сон в сохранение
    cur.execute('''UPDATE saves SET dream = ? WHERE id = ?''', (location_id, save_id))


@ut.create_connect
def get_dream_save(cur=None):
    location_id = cur.execute('SELECT dream FROM saves WHERE id=?', (save_id,)).fetchone()[0]
    dream_map = Map(ut.screen, "location_one/loco1")
    map_groups = dream_map.get_groups()

    groups = {'background_layer': map_groups[0],  # Бэкграунд
              'platforms_group': map_groups[1],  # Группа платформ
              'deadly_layer': map_groups[2],  # Смертельные блоки
              'creatures_group': pg.sprite.Group()}  # Все существа

    # Заполняем диалоги
    dialogs = []
    for dialog in cur.execute('''SELECT id, question, x, y, radius FROM dialogs WHERE location=?''',
                              (location_id,)).fetchall():
        answers = cur.execute('''SELECT answer FROM answers WHERE dialog=?''', (dialog[0],)).fetchall()
        dialogs.append(obj.Dialog(*list(dialog[1:]) + [i[0] for i in answers]))

    obj.Background(ut.load_image("images/background.png"), 0, 0, groups['background_layer'])

    # Инициализируем игрока
    x, y, direction, hp = cur.execute('''SELECT x, y, direction, (SELECT current_health FROM healths WHERE id=health)
    FROM players WHERE id=(SELECT player FROM locations WHERE id=?)''', (location_id,)).fetchone()
    player = Player(groups['creatures_group'], (x, y), groups['platforms_group'], groups['deadly_layer'], hp=hp)
    player.direction = direction

    skeletons = []
    for x, y, direction, hp in cur.execute('''SELECT x, y, direction, (SELECT current_health 
    FROM healths WHERE id=health) FROM skeletons WHERE location=?''', (location_id,)).fetchall():
        enemy = Enemy(groups['creatures_group'], (x, y), groups['platforms_group'], groups['deadly_layer'], hp=hp)
        enemy.direction = direction
        skeletons.append(enemy)

    return groups, dialogs, player, skeletons


@ut.create_connect
def location_save(creatures_group, dialogs, location_name='dream', cur=None):
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


# Основной цикл игры
def game():
    global last_scene
    last_scene = game

    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    ut.initialization()

    def save_return(value):
        location_save(groups['creatures_group'], dialogs)
        return value

    # Карта: сон
    groups, dialogs, player, skeletons = get_dream_save()

    # ______________ ДИАЛОГИ __________________ #
    screen2 = pg.Surface(ut.screen.get_size(), pg.SRCALPHA)
    screen3 = pg.Surface(ut.screen.get_size(), pg.SRCALPHA)
    screen3.set_alpha(10)
    degree = 0  # анимация (Е)
    activ_dial_x = activ_dial_y = 0  # положение анимации (Е)
    push = False  # зажата ли (Е)
    e_image = ut.load_image('images/e.png', 'CUSTOM_SIZE', factors=(0.58, 0.58))
    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

    # Для обработки нажатия прыжка по новой механики (она вводится, что бы работал двойной прыжок)
    jump_pressed_last_frame = False

    # Создаём камеру, паузу, конец игры
    camera = Camera()
    pause = obj.Pause()
    end_game = obj.EndGame(1940, 1956)

    while True:
        if pg.sprite.collide_mask(player, end_game):
            end_game.set_active(ut.screen)
            end_game_log = ut.render_popup(end_game)
            if end_game_log in 'start_screen':
                save_return(start_screen)
            elif end_game_log == 'quit':
                return save_return('close')

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return save_return('close')
            if event.type == pg.KEYDOWN:
                if event.key == 101:
                    screen2 = pg.Surface(ut.screen.get_size())
                    screen2.set_colorkey((0, 0, 0))
                    if player.direction == 'right':
                        activ_dial_x, activ_dial_y = (player.rect.x + player.rect.width - camera.x(),
                                                      player.rect.y - camera.y())
                    else:
                        activ_dial_x, activ_dial_y = player.rect.x - camera.x(), player.rect.y - camera.y()
                    degree = 0
                    push = True
                if event.key == 27:
                    pause.set_active(ut.screen)
                    pause_log = ut.render_popup(pause)
                    if pause_log in ('select_save', 'settings'):
                        return save_return({'select_save': select_save, 'settings': settings}[pause_log])
                    elif pause_log == 'quit':
                        location_save(groups['creatures_group'], dialogs)
                        return save_return('close')
            if event.type == pg.KEYUP:
                if event.key == 101:
                    push = False

        # Проверка зажатия WASD или стрелочек
        keys = pg.key.get_pressed()
        jump_pressed_now = keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            player.direction = "right"
            player.move("right")
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            player.direction = "left"
            player.move("left")
        if jump_pressed_now and not jump_pressed_last_frame:
            player.jump()
        if keys[pg.K_LCTRL]:  # Рывок
            player.dash(player.direction)
        if keys[pg.K_x]:
            player.attack1()

        # Обновляем переменную для следующего кадра:
        jump_pressed_last_frame = jump_pressed_now

        # Очистка экрана
        ut.screen.fill((50, 131, 218))

        # Обновление всех существ
        # creatures_group.update(creatures_group)
        for sprite in groups['creatures_group']:
            sprite.update(groups['creatures_group'])
        for skeleton in skeletons:
            skeleton.check_trigger_radius(player)

        # Обновление камеры
        camera.update(player)

        # Рисуем все группы спрайтов с учётом камеры
        for group in groups.values():
            camera.draw_group(group, ut.screen)
        camera.draw_group(ut.top_layer, ut.screen)

        # ______________ ДИАЛОГИ __________________ #
        cur_dialog = None
        for item_dialog in dialogs:
            if player.rect.colliderect(item_dialog.x - item_dialog.radius + player.left_indent,
                                       item_dialog.y - item_dialog.radius,
                                       item_dialog.radius * 2 - player.left_indent - player.right_indent,
                                       item_dialog.radius * 2):
                cur_dialog = item_dialog

        if cur_dialog and push:
            for i in range(10):
                degree += 1 * 60 / ut.fps
                pg.draw.circle(screen2, pg.Color('white'), radius=2,
                               center=ut.return_dot(degree, 30, activ_dial_x, activ_dial_y))
            if degree > 400 and push:
                ut.sounds['dialog_activation'].play()
                push = False
                cur_dialog.set_active(ut.screen)
            ut.screen.blit(screen2, (0, 0))
            e_image.set_alpha(255)
            ut.screen.blit(e_image, (activ_dial_x - e_image.get_rect().width / 2,
                                     activ_dial_y - e_image.get_rect().height / 2))
        elif cur_dialog:
            e_image.set_alpha(100)
            ut.screen.blit(e_image, (cur_dialog.x - e_image.get_rect().width / 2 - camera.x(),
                                     cur_dialog.y - e_image.get_rect().height / 2 - camera.y()))
        if cur_dialog:
            screen3.fill((0, 0, 0))
            pg.draw.rect(screen3, pg.Color('white'), (cur_dialog.x - cur_dialog.radius - camera.x(),
                                                      cur_dialog.y - cur_dialog.radius - camera.y(),
                                                      cur_dialog.radius * 2,
                                                      cur_dialog.radius * 2))
            ut.screen.blit(screen3, (0, 0))
        if cur_dialog and cur_dialog.active:
            answer = ut.render_popup(cur_dialog)
            dialogs.remove(cur_dialog)
            cur_dialog = None
            if answer == 'quit':
                return save_return('close')
        # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

        pg.display.flip()
        ut.clock.tick(ut.fps)

    # Экран 'приветствия', главная менюшка


def start_screen():
    global last_scene
    last_scene = start_screen

    ut.initialization()

    bg = obj.Background(ut.load_image('menu UI/Background.png', 'MENU'), 670, 0, ut.bottom_layer)
    fg = obj.Background(ut.load_image('menu UI/Foreground.png', 'MENU'), 0, 0, ut.top_layer)

    ship1 = obj.Ship(1, ut.width, ut.height, ut.mid_layer)
    cloud1 = obj.Cloud(1)
    mountain = obj.Mountain()
    ship2 = obj.Ship(-1, ut.width, ut.height, ut.mid_layer)
    cloud2 = obj.Cloud(-1)
    play_button = obj.Button(32, 528, select_save, ut.load_image('buttons/Play.png', 'MENU'),
                             (ut.all_sprites, ut.button_layer))
    settings_button = obj.Button(33, 788, settings,
                                 ut.load_image('buttons/Settings.png', 'MENU'),
                                 (ut.all_sprites, ut.button_layer))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                ut.button_layer.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                for func in [play_button.update(event.pos, 'up'),
                             settings_button.update(event.pos, 'up')]:
                    if func:
                        return func

        ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)

        pg.display.flip()
        ut.clock.tick(ut.fps)


# Экран выбора сохранения
@ut.create_connect
def select_save(cur=None):
    ut.initialization()

    saves = cur.execute('SELECT id FROM saves').fetchall()
    save_count = len(saves)

    buttons = []

    for save in saves:
        buttons.append(obj.Button(381, 160 + 151 * (saves.index(save)), save[0],
                                  ut.load_image(f'buttons/saves/Save {saves.index(save) + 1}.png', 'MENU'),
                                  (ut.all_sprites, ut.button_layer)))

    def plus():
        nonlocal save_count, cur
        cur.execute('INSERT INTO saves(current_location) VALUES("dream")')  # создаем новое сохранение
        save_id = cur.execute('SELECT MAX(Id) FROM saves').fetchone()[0]

        save_count += 1
        create_dream_save(save_id, cur)

        buttons.append(obj.Button(381, 160 + 151 * (save_count - 1), save_id,
                                  ut.load_image(f'buttons/saves/Save {save_count}.png', 'MENU'),
                                  (ut.all_sprites, ut.button_layer)))
        if save_count == 5 and plus_button:
            plus_button.kill()

    buttons.append(obj.Button(350, 0, start_screen, ut.load_image('buttons/BookmarkHome.png', 'MENU'),
                              (ut.all_sprites, ut.button_layer)))
    if save_count < 5:
        plus_button = buttons.append(obj.Button(549, 834, plus, ut.load_image('buttons/Plus.png', 'MENU'),
                                                (ut.all_sprites, ut.button_layer)))

    # for save in saves:

    bg = obj.Background(ut.load_image('select UI/Background.png', 'MENU'), 0, 0, ut.bottom_layer)
    art1 = obj.Art(ut.load_image('select UI/Cloud 1.png', 'MENU'), 1038, 102)
    art2 = obj.Art(ut.load_image('select UI/Cloud 2.png', 'MENU'), 1168, 245)
    art3 = obj.Art(ut.load_image('select UI/Island 1.png', 'MENU'), 1360, 560)
    art4 = obj.Art(ut.load_image('select UI/Island 2.png', 'MENU'), 1020, 460)

    MYEVENTTYPE = pg.USEREVENT + 1
    pg.time.set_timer(MYEVENTTYPE, 50)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                ut.button_layer.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                for func in [button.update(event.pos, 'up') for button in buttons]:
                    if func == start_screen:
                        return start_screen
                    elif func.__class__.__name__ == 'int':
                        global save_id
                        save_id = func
                        return game
                    elif func:
                        func()
            if event.type == MYEVENTTYPE:
                ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)

        pg.display.flip()
        ut.clock.tick(ut.fps)

    # Экран настроек


def settings():
    ut.initialization()

    obj.Background(ut.load_image('settings UI/Background.png', 'MENU'), 0, 0, ut.bottom_layer)  # Задний фон
    obj.Gearwheel()
    buttons = [obj.Button(350, 0, last_scene, ut.load_image('buttons/BookmarkHome.png' if last_scene == start_screen
                                                            else 'buttons/BookmarkBack.png', 'MENU'),
                          (ut.all_sprites, ut.button_layer))]

    slider_push = False
    sliders = [
        # слайдер фпс
        obj.Slider(350, 300, 60, 'FPS', text={'x': 613, 'y': 195, 'center': False, 'size': 80}),
        # слайдер громкости
        obj.Slider(350, 445, 100, 'SOUNDS VOLUME', text={'x': 673, 'y': 350, 'center': False, 'size': 80}),
        # слайдер размера экрана
        obj.Slider(350, 594, 80, 'SIZE FACTOR', text={'x': 600, 'y': 635, 'center': True, 'size': 50})
    ]

    MYEVENTTYPE = pg.USEREVENT + 1
    pg.time.set_timer(MYEVENTTYPE, 100)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.update(event.pos, 'down')
                slider_push = any([slider.update(event.pos, 'down') for slider in sliders])
            if event.type == pg.MOUSEBUTTONUP:
                slider_push = False
                if any([slider.save_changes() for slider in sliders]):
                    ut.update_settings()
                    return settings
                for func in [button.update(event.pos, 'up') for button in buttons]:
                    if func == last_scene:
                        return last_scene
            if event.type == pg.MOUSEMOTION:
                if slider_push:
                    for slider in sliders:
                        slider.update(event.rel, 'move', pos2=event.pos)
            if event.type == MYEVENTTYPE:
                ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)
        for slider in sliders:
            slider.draw_text()

        pg.display.flip()
        ut.clock.tick(ut.fps)
