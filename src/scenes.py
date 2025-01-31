from objects import *
from map import Map
from camera import update_camera, draw_group_with_camera

# Основной цикл игры
def game():
    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    initialization()

    player_pos = (1800 * FACTOR_X, 100 * FACTOR_Y)

    # Создаём объект карты
    map = Map(screen, "loco1")
    groups = map.get_groups() # Получаем все группы спрайтов с нашей карты
    top_layer = groups[1] # Передаём игроку 1 аргумент, т.к. метод get_groups возращает группу platforms второй

    # Заполняем группы
    Background(load_image("images/first_background.jpg"), 0, 0, bottom_layer)
    mid_layer = groups[0]
    button_layer = groups[2] # die блоки

    # Создаём игрока
    player = Player(player_group, player_pos, top_layer, button_layer)

    # Создаём камеру
    camera = pygame.Rect(0, 0, WIDTH, HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'

        # Проверка зажатия WASD или стрелочек
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.direction = "right"
            player.move("right")
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.direction = "left"
            player.move("left")
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            player.jump()
        if keys[pygame.K_LCTRL]:  # Рывок
            player.dash(player.direction)

        # Очистка экрана
        screen.fill((0, 0, 0))

        # Обновляем игрока
        player.update()

        # Обновление камеры
        update_camera(player.rect, camera, map.width, map.height)

        # Отрисовка карты с учётом камеры
        map.render(screen, camera)

        # Рисуем все группы спрайтов с учётом камеры
        draw_group_with_camera(bottom_layer, screen, camera)
        draw_group_with_camera(mid_layer, screen, camera)
        draw_group_with_camera(top_layer, screen, camera)
        draw_group_with_camera(button_layer, screen, camera)

        # Отрисовка игрока относительно камеры
        player.draw(screen, camera)

        pygame.display.flip()
        clock.tick(fps)


# Экран 'приветствия', главная менюшка
def start_screen():
    initialization()

    bg = Background(load_image('menu UI/Background.png', 'MENU'), 670, 0, bottom_layer)
    fg = Background(load_image('menu UI/Foreground.png', 'MENU'), 0, 0, top_layer)

    ship1 = Ship(1)
    cloud1 = Cloud(1)
    mountain = Mountain()
    ship2 = Ship(-1)
    cloud2 = Cloud(-1)
    play_button = Button(32, 528, select_save, load_image('menu UI/PlayButton.png', 'MENU'),
                         (all_sprites, button_layer), FACTOR_X, FACTOR_Y)
    settings_button = Button(33, 788, settings, load_image('menu UI/SettingsButton.png', 'MENU'),
                             (all_sprites, button_layer), FACTOR_X, FACTOR_Y)
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
                                   load_image(f'select UI/Save {save_count}.png', 'MENU'),
                                   (all_sprites, button_layer), FACTOR_X, FACTOR_Y))
        if save_count == 5:
            plus_button.kill()

    initialization()

    bg = Background(load_image('select UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    art1 = Art(load_image('select UI/Cloud 1.png', 'MENU'), 1038, 102)
    art2 = Art(load_image('select UI/Cloud 2.png', 'MENU'), 1168, 245)
    art3 = Art(load_image('select UI/Island 1.png', 'MENU'), 1360, 560)
    art4 = Art(load_image('select UI/Island 2.png', 'MENU'), 1020, 460)
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png', 'MENU'),
                             (all_sprites, button_layer), FACTOR_X, FACTOR_Y)
    plus_button = Button(549, 834, plus, load_image('select UI/Plus.png', 'MENU'),
                         (all_sprites, button_layer), FACTOR_X, FACTOR_Y)

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
def settings():
    initialization()

    bg = Background(load_image('settings UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    gear = Gearwheel()
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png', 'MENU'),
                             (all_sprites, button_layer), FACTOR_X, FACTOR_Y)

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
                    if func == start_screen:
                        return start_screen
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
