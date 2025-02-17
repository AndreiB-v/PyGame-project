import random
from random import choice as ch

import pygame.image
from pygame.rect import Rect

from objects import *
from map import Map
from camera import Camera
from src.creatures import Player, Enemy

current_location = "City"

# Основной цикл игры
def game():
    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    initialization()
    global current_location

    pygame.mixer.music.stop()  # Останавливаем музыку при начале игры

    dream_map = dialogs = creatures_group = enemy = enemy2 = None
    back_photo = cloud_layer = background_layer = platforms_group = deadly_layer = player = end_game = next_lvl = None
    rain = []

    # Карта: сон
    def dream():
        nonlocal dream_map, dialogs, back_photo, cloud_layer, background_layer, \
            platforms_group, deadly_layer, player, end_game, creatures_group, enemy, enemy2, next_lvl
        dream_map = Map(screen, "location_one\loco1")
        player_pos = (
            int(dream_map.get_player_start_position()[0]),
            int(dream_map.get_player_start_position()[1]))  # Получаем позицию игрока с карты
        umiko_pos = (
            int(dream_map.get_umiko_position()[0]),
            int(dream_map.get_umiko_position()[1]))
        win_flag_pos = (
            int(dream_map.get_win_flag_position()[0]),
            int(dream_map.get_win_flag_position()[1]))

        groups = dream_map.get_groups()  # Получаем все группы спрайтов с нашей карты

        # Получаем все файлы облаков
        files = get_images("../data/maps/location_one/clouds")
        clouds = []
        for i in files:
            clouds.append(load_image(f"maps/location_one/clouds/{i}"))

        # ЛОКАЛЬНЫЕ (для game) группы
        back_photo = pygame.sprite.Group()  # Статичный бэк
        cloud_layer = pygame.sprite.Group()  # Слой для облаков
        background_layer = groups[0]  # Бэкграунд
        platforms_group = groups[1]  # Группа платформ
        deadly_layer = groups[2]  # Смертельные блоки
        creatures_group = pygame.sprite.Group()  # Группа игрока

        # background
        Background(load_image("images/background.png"), 0, 0, back_photo)

        # Создаём игрока
        player = Player(creatures_group, player_pos, platforms_group, deadly_layer)
        enemy = Enemy(creatures_group, player_pos, platforms_group, deadly_layer)
        enemy2 = Enemy(creatures_group, (557, 1138), platforms_group, deadly_layer)
        end_game = EndGame(win_flag_pos[0], win_flag_pos[1])
        next_lvl = NextLevel(win_flag_pos[0] + 2000, win_flag_pos[1] + 2000) # Не обязателен

        # Создаём облака
        for _ in range(10):
            BgCloud(cloud_layer, clouds, dream_map.width, dream_map.height)

        dialogs = [Dialog('кРСАВА, убил монстра',
                          umiko_pos[0],
                          umiko_pos[1],
                          100 * FACTOR_X,
                          'спасибо!', 'да, я такой!')]

    # Карта: город
    def city():
        nonlocal dream_map, dialogs, back_photo, cloud_layer, background_layer, \
            platforms_group, deadly_layer, player, end_game, creatures_group, rain, next_lvl
        city_map = Map(screen, "location_two\loco2")

        player_pos = (
            int(city_map.get_player_start_position()[0]),
            int(city_map.get_player_start_position()[1]))  # Получаем позицию игрока с карты

        win_flag_pos = (
            int(city_map.get_win_flag_position()[0]),
            int(city_map.get_win_flag_position()[1]))

        groups = city_map.get_groups()  # Получаем все группы спрайтов с нашей карты

        # ЛОКАЛЬНЫЕ (для game) группы
        back_photo = pygame.sprite.Group()  # Статичный бэк
        cloud_layer = pygame.sprite.Group() # Не использующиеся группы всё равно нужно определять, иначе они будут None
        background_layer = groups[0]  # Бэкграунд
        platforms_group = groups[1]  # Группа платформ
        deadly_layer = groups[2]  # Смертельные блоки
        creatures_group = pygame.sprite.Group()  # Группа игрока

        # background
        Background(load_image("maps/location_two/assets/background.png"), -300, -300, back_photo)

        # Создаём игрока
        player = Player(creatures_group, player_pos, platforms_group, deadly_layer)

        # Создаём дождь
        for _ in range(1000):
            rain.append(Drop(city_map.width * 16, city_map.height * 16))

        pygame.mixer.music.load("../data/sounds/rain_sound.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)

        # Вин поз
        end_game = EndGame(win_flag_pos[0] + 500, win_flag_pos[1] + 500) # Обязателен для меню, но на карте не нужен
        next_lvl = NextLevel(win_flag_pos[0], win_flag_pos[1])

        dialogs = [Dialog('О, привет, сынок',
                          3128 - 300,
                          1512,
                          100 * FACTOR_X,
                          'Куда ты так поздно?', 'И куда ты?')]

    if current_location == "City":
        city()
    else:
        dream()

    # ______________ ДИАЛОГИ __________________ #
    screen2 = pygame.Surface(screen.get_size())
    screen3 = pygame.Surface(screen.get_size())
    screen2.set_colorkey((0, 0, 0))
    screen3.set_colorkey((0, 0, 0))
    screen3.set_alpha(10)
    degree = 0  # анимация (Е)
    activ_dial_x = activ_dial_y = 0  # положение анимации (Е)
    push = False  # зажата ли (Е)
    e_image = load_image('images/e.png', 'MENU')  # картинка Е
    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

    pause = Pause()

    jump_pressed_last_frame = False  # Для обработки нажатия прыжка по новой механики (она вводится, что бы работал двойной прыжок)

    # Создаём камеру
    camera = Camera()

    while True:
        if pygame.sprite.collide_mask(player, end_game):
            end_game.set_active(screen)
            end_game_log = render_popup(end_game)
            if end_game_log in 'start_screen':
                return start_screen
            elif end_game_log == 'quit':
                return 'close'
        if pygame.sprite.collide_mask(player, next_lvl):
            current_location = "Dream"
            return game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.KEYDOWN:
                if event.key == 101:
                    screen2 = pygame.Surface(screen.get_size())
                    screen2.set_colorkey((0, 0, 0))
                    if player.direction == 'right':
                        activ_dial_x, activ_dial_y = (player.rect.x + player.rect.width - camera.x(),
                                                      player.rect.y - camera.y())
                    else:
                        activ_dial_x, activ_dial_y = player.rect.x - camera.x(), player.rect.y - camera.y()
                    degree = 0
                    push = True
                if event.key == 27:
                    pause.set_active(screen)
                    pause_log = render_popup(pause)
                    if pause_log in ('start_screen', 'settings'):
                        return {'start_screen': start_screen, 'settings': lambda: settings(game)}[pause_log]
                    elif pause_log == 'quit':
                        return 'close'
            if event.type == pygame.KEYUP:
                if event.key == 101:
                    push = False

        # Проверка зажатия WASD или стрелочек
        keys = pygame.key.get_pressed()
        jump_pressed_now = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.direction = "right"
            player.move("right")
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.direction = "left"
            player.move("left")
        if jump_pressed_now and not jump_pressed_last_frame:
            player.jump()
        if keys[pygame.K_LCTRL]:  # Рывок
            player.dash(player.direction)
        if keys[pygame.K_x]:
            player.attack1()

        # Обновляем переменную для следующего кадра:
        jump_pressed_last_frame = jump_pressed_now

        # Очистка экрана
        screen.fill((50, 131, 218))

        # Обновление всех существ
        # creatures_group.update(creatures_group)
        for sprite in creatures_group:
            sprite.update(creatures_group)
        if len(creatures_group) > 1:
            enemy.check_trigger_radius(player)
            enemy2.check_trigger_radius(player)

        # Обновление камеры
        camera.update(player)

        # Рисуем все группы спрайтов с учётом камеры
        camera.draw_group(bottom_layer, screen)
        camera.draw_group(back_photo, screen)
        camera.draw_group(background_layer, screen)

        # Если дождь был создан, то рисуем его
        if rain:
            for drop in rain:
                drop.update()
                drop.draw()

        camera.draw_group(cloud_layer, screen)
        camera.draw_group(mid_layer, screen)
        camera.draw_group(platforms_group, screen)
        camera.draw_group(deadly_layer, screen)
        camera.draw_group(top_layer, screen)
        camera.draw_group(creatures_group, screen)

        # ______________ ДИАЛОГИ __________________ #
        cur_dialog = None
        if dialogs:
            for item_dialog in dialogs:
                if player.rect.colliderect(item_dialog.x - item_dialog.radius + player.left_indent,
                                           item_dialog.y - item_dialog.radius,
                                           item_dialog.radius * 2 - player.left_indent - player.right_indent,
                                           item_dialog.radius * 2):
                    cur_dialog = item_dialog

        if cur_dialog and push:
            for i in range(10):
                degree += 1 * 60 / fps
                pygame.draw.circle(screen2, pygame.Color('white'), radius=2,
                                   center=return_dot(degree, 30, activ_dial_x, activ_dial_y))
            screen.blit(screen2, (0, 0))
            e_image.set_alpha(255)
            screen.blit(e_image, (activ_dial_x - e_image.get_rect().width / 2,
                                  activ_dial_y - e_image.get_rect().height / 2))
        elif cur_dialog:
            e_image.set_alpha(100)
            screen.blit(e_image, (cur_dialog.x - e_image.get_rect().width / 2 - camera.x(),
                                  cur_dialog.y - e_image.get_rect().height / 2 - camera.y()))
        if cur_dialog:
            screen3.fill((0, 0, 0))
            pygame.draw.rect(screen3, pygame.Color('white'), (cur_dialog.x - cur_dialog.radius - camera.x(),
                                                              cur_dialog.y - cur_dialog.radius - camera.y(),
                                                              cur_dialog.radius * 2,
                                                              cur_dialog.radius * 2))
            screen.blit(screen3, (0, 0))
        if degree > 400 and push:
            push = False
            cur_dialog.set_active(screen)
        if cur_dialog and cur_dialog.active:
            answer = render_popup(cur_dialog)
            dialogs.remove(cur_dialog)
            cur_dialog = None
            if answer == 'quit':
                return 'close'
            if answer == "Куда ты так поздно?" or answer == "И куда ты?":
                dialogs = [Dialog('Сам же знаешь. На работу',
                          3128 - 300,
                          1512,
                          100 * FACTOR_X,
                          'Опять переработки?', 'Как много работы')]
            if answer == "Опять переработки?" or answer == "Как много работы":
                dialogs = [Dialog('Ну, а что поделать? Ладно, я побежала, бязательно поешь!',
                          3128 - 300,
                          1512,
                          100 * FACTOR_X,
                          'Хорошо, пока', 'Окей, увидимся')]
        # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

        pygame.display.flip()
        clock.tick(fps)


# Экран 'приветствия', главная менюшка
def start_screen():
    initialization()

    bg = Background(load_image('menu UI/Background.png', 'MENU'), 670, 0, bottom_layer)
    fg = Background(load_image('menu UI/Foreground.png', 'MENU'), 0, 0, top_layer)

    ship1 = Ship(1, WIDTH, HEIGHT, mid_layer)
    cloud1 = Cloud(1)
    mountain = Mountain()
    ship2 = Ship(-1, WIDTH, HEIGHT, mid_layer)
    cloud2 = Cloud(-1)
    play_button = Button(32, 528, select_save, load_image('buttons/Play.png', 'MENU'),
                         (all_sprites, button_layer))
    settings_button = Button(33, 788, lambda: settings(start_screen),
                             load_image('buttons/Settings.png', 'MENU'),
                             (all_sprites, button_layer))

    # Песня на заднем плане
    pygame.mixer.music.load("../data/sounds/start_screen_background_music.mp3")
    pygame.mixer.music.play(-1)  # Проигрывание + зацикливание
    pygame.mixer.music.set_volume(0.05)  # Уменьшаем громкость в половину1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_layer.update(event.pos, 'down')
            if event.type == pygame.MOUSEBUTTONUP:
                for func in [play_button.update(event.pos, 'up'),
                             settings_button.update(event.pos, 'up')]:
                    if func:
                        return func

        mid_layer.update()

        screen.fill((0, 0, 0))
        bottom_layer.draw(screen)
        mid_layer.draw(screen)
        top_layer.draw(screen)
        button_layer.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


# Экран выбора сохранения
def select_save():
    save_count = 0
    save_buttons = []

    def plus():
        nonlocal save_count
        save_count += 1
        save_buttons.append(Button(381, 160 + 151 * (save_count - 1), game,
                                   load_image(f'buttons/saves/Save {save_count}.png', 'MENU'),
                                   (all_sprites, button_layer)))
        if save_count == 5:
            plus_button.kill()

    initialization()

    bg = Background(load_image('select UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    art1 = Art(load_image('select UI/Cloud 1.png', 'MENU'), 1038, 102)
    art2 = Art(load_image('select UI/Cloud 2.png', 'MENU'), 1168, 245)
    art3 = Art(load_image('select UI/Island 1.png', 'MENU'), 1360, 560)
    art4 = Art(load_image('select UI/Island 2.png', 'MENU'), 1020, 460)
    bookmark_button = Button(350, 0, start_screen, load_image('buttons/BookmarkHome.png', 'MENU'),
                             (all_sprites, button_layer))
    plus_button = Button(549, 834, plus, load_image('buttons/Plus.png', 'MENU'),
                         (all_sprites, button_layer))

    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 50)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_layer.update(event.pos, 'down')
            if event.type == pygame.MOUSEBUTTONUP:
                for func in ([bookmark_button.update(event.pos, 'up'),
                              plus_button.update(event.pos, 'up')] +
                             [i.update(event.pos, 'up') for i in save_buttons]):
                    if func == start_screen:
                        return start_screen
                    elif func == game:
                        return game
                    elif func:
                        func()
            if event.type == MYEVENTTYPE:
                mid_layer.update()

        screen.fill((0, 0, 0))
        bottom_layer.draw(screen)
        mid_layer.draw(screen)
        top_layer.draw(screen)
        button_layer.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


# Экран настроек
def settings(back_scene):
    initialization()

    bg = Background(load_image('settings UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    gear = Gearwheel()
    bookmark_button = Button(350, 0, back_scene,
                             load_image('buttons/BookmarkHome.png' if back_scene == start_screen
                                        else 'buttons/BookmarkBack.png', 'MENU'),
                             (all_sprites, button_layer))

    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_layer.update(event.pos, 'down')
            if event.type == pygame.MOUSEBUTTONUP:
                for func in [bookmark_button.update(event.pos, 'up')]:
                    if func == back_scene:
                        return back_scene
                    elif func:
                        func()
            if event.type == MYEVENTTYPE:
                mid_layer.update()

        screen.fill((0, 0, 0))
        bottom_layer.draw(screen)
        mid_layer.draw(screen)
        top_layer.draw(screen)
        button_layer.draw(screen)

        pygame.display.flip()
        clock.tick(fps)
