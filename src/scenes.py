import random
from random import choice as ch

from pygame.rect import Rect

from objects import *
from map import Map
from camera import update_camera, draw_group_with_camera

# Основной цикл игры
def game():
    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    initialization()

    # Создаём объект карты
    map = Map(screen, "loco1")
    player_pos = (int(map.get_player_start_position()[0]), int(map.get_player_start_position()[1])) # Получаем позицию игрока с карты

    groups = map.get_groups() # Получаем все группы спрайтов с нашей карты
    top_layer = groups[1] # Передаём игроку 1 аргумент, т.к. метод get_groups возращает группу platforms второй

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

    dialogs = [Dialog('Привет, ЭТО диАЛОГи!', 300 * FACTOR_X, 200 * FACTOR_Y, 100 * FACTOR_X,
                      'Хм, ЭтО КрУтО!', 'ОКЕ!')]
    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

    pause = Pause()
    end_game = EndGame(1400 * FACTOR_X, 200 * FACTOR_Y)

    player_pos = (50 * FACTOR_X, 100 * FACTOR_Y)

    # Заполняем группы
    Background(load_image("images/first_background.jpg"), 0, 0, bottom_layer)
    mid_layer = groups[0]
    button_layer = groups[2] # die блоки

    # Создаём игрока
    player = Player(player_group, player_pos, top_layer, button_layer)

    # Создаём корабли
    # for i in range(10):
    #     Ship(random.choice([-1, 1]), int(map.width) * 16, int(map.height) * 16, ships_layer)

    jump_pressed_last_frame = False # Для обработки нажатия прыжка по новой механики (она вводится, что бы работал двойной прыжок)

    # Создаём камеру
    camera = pygame.Rect(0, 0, WIDTH, HEIGHT)

    while True:
        if pygame.sprite.collide_mask(player, end_game):
            end_game.set_active(screen)
            end_game_log = render_popup(end_game)
            if end_game_log in 'start_screen':
                return start_screen
            elif end_game_log == 'quit':
                return 'close'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.KEYDOWN:
                if event.key == 101:
                    screen2 = pygame.Surface(screen.get_size())
                    screen2.set_colorkey((0, 0, 0))
                    if player.direction == 'right':
                        activ_dial_x, activ_dial_y = player.rect.x + player.rect.width, player.rect.y
                    else:
                        activ_dial_x, activ_dial_y = player.rect.x, player.rect.y
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
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            player.jump()
        if keys[pygame.K_LCTRL]:  # Рывок
            player.dash(player.direction)

        # Обновляем переменную для следующего кадра:
        jump_pressed_last_frame = jump_pressed_now

        # Очистка экрана
        screen.fill((0, 0, 0))

        # Обновляем игрока
        player.update()

        cur_dialog = None
        for item_dialog in dialogs:
            if player.rect.colliderect(item_dialog.x - item_dialog.radius + player.left_indent,
                                       item_dialog.y - item_dialog.radius,
                                       item_dialog.radius * 2 - player.left_indent - player.right_indent,
                                       item_dialog.radius * 2):
                cur_dialog = item_dialog

        # Обновление камеры
        update_camera(player.rect, camera, map.width, map.height)

        # Отрисовка карты с учётом камеры
        map.render(screen, camera)

        # Рисуем все группы спрайтов с учётом камеры
        draw_group_with_camera(bottom_layer, screen, camera)
        # ships_layer.draw(screen)
        draw_group_with_camera(mid_layer, screen, camera)
        draw_group_with_camera(top_layer, screen, camera)
        draw_group_with_camera(button_layer, screen, camera)

        # Отрисовка игрока относительно камеры
        player.draw(screen, camera)

        # ______________ ДИАЛОГИ __________________ #
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
            screen.blit(e_image, (cur_dialog.x - e_image.get_rect().width / 2,
                                  cur_dialog.y - e_image.get_rect().height / 2))
        if cur_dialog:
            screen3.fill((0, 0, 0))
            pygame.draw.rect(screen3, pygame.Color('white'), (cur_dialog.x - cur_dialog.radius,
                                                              cur_dialog.y - cur_dialog.radius,
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
