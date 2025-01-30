from objects import *

class Game:
    def __init__(self):
        pygame.init()
        self.size = WIDTH, HEIGHT
        pygame.display.set_caption("Корабли ходят по небу")
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        player_pos = (50 * factor_x, 100 * factor_y)

        # Создаём группы
        self.player_group = pygame.sprite.Group()
        self.all_group = pygame.sprite.Group()

        self.player = Player(self.player_group, player_pos, self.all_group)
        Platform(0, 300, 401, 1000, self.all_group)
        Platform(400, 700, 400, 1000, self.all_group)
        Platform(600, 500, 700, 100, self.all_group)
        Platform(798, 300, 700, 1000, self.all_group)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Проверка зажатия WASD или стрелочек
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.direction = "right"
                self.player.move("right")
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.direction = "left"
                self.player.move("left")
            if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
                self.player.jump()
            if keys[pygame.K_LCTRL]:  # Рывок
                self.player.dash(self.player.direction)

            # Отрисовываем
            self.screen.fill((0, 0, 0))
            self.player_group.draw(self.screen)
            self.player.update()
            self.all_group.draw(self.screen)

            self.clock.tick(fps)
            pygame.display.flip()

        pygame.quit()


def game():
    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    initialization()

    player_pos = (50 * factor_x, 100 * factor_y)

    player = Player(player_group, player_pos, top_layer)
    Platform(0, 300, 401, 1000, top_layer)
    Platform(400, 700, 400, 1000, top_layer)
    Platform(600, 500, 700, 100, top_layer)
    Platform(798, 300, 700, 1000, top_layer)

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

        screen.fill((0, 0, 0))

        # Обновляем игрока
        player.update()

        # Рисуем все группы
        bottom_layer.draw(screen)
        mid_layer.draw(screen)
        player_group.draw(screen)
        top_layer.draw(screen)
        button_layer.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


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
                         (all_sprites, button_layer), factor_x, factor_y)
    settings_button = Button(33, 788, settings, load_image('menu UI/SettingsButton.png', 'MENU'),
                             (all_sprites, button_layer), factor_x, factor_y)
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


def select_save():
    save_count = 0
    save_buttons = []

    def plus():
        nonlocal save_count
        save_count += 1
        save_buttons.append(Button(381, 160 + 151 * (save_count - 1), game,
                                   load_image(f'select UI/Save {save_count}.png', 'MENU'),
                                   (all_sprites, button_layer), factor_x, factor_y))
        if save_count == 5:
            plus_button.kill()

    initialization()

    bg = Background(load_image('select UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    art1 = Art(load_image('select UI/Cloud 1.png', 'MENU'), 1038, 102)
    art2 = Art(load_image('select UI/Cloud 2.png', 'MENU'), 1168, 245)
    art3 = Art(load_image('select UI/Island 1.png', 'MENU'), 1360, 560)
    art4 = Art(load_image('select UI/Island 2.png', 'MENU'), 1020, 460)
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png', 'MENU'),
                             (all_sprites, button_layer), factor_x, factor_y)
    plus_button = Button(549, 834, plus, load_image('select UI/Plus.png', 'MENU'),
                         (all_sprites, button_layer), factor_x, factor_y)

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


def settings():
    initialization()

    bg = Background(load_image('settings UI/Background.png', 'MENU'), 0, 0, bottom_layer)
    gear = Gearwheel()
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png', 'MENU'),
                             (all_sprites, button_layer), factor_x, factor_y)

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
