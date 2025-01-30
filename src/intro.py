# Это начальная заставка, осталось только кнопки добавить

from random import choice, randint, uniform

import pygame.time

from utils import *

pygame.init()
# Задается размер экрана с соотношением 16:9, позже это пропишем в другом месте
screen = pygame.display.set_mode(size, pygame.NOFRAME)


# факторы, которые умножаем на каждый x/y, для работы с размером экрана


def load_image(name, colorkey=None):
    fullname = os.path.join('../data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        x = image.get_width()
        y = image.get_height()
        image = pygame.transform.scale(image, (factor_x * x, factor_y * y))
        image = image.convert_alpha()
    return image


ship1_image = load_image('menu UI/Ship 1.png')
ship2_image = load_image('menu UI/Ship 2.png')
cloud1_image = load_image('menu UI/Cloud 1.png')
cloud2_image = load_image('menu UI/Cloud 2.png')


class Background(pygame.sprite.Sprite):
    def __init__(self, image, x, y, group):
        super().__init__(all_sprites, group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * factor_x
        self.rect.y = y * factor_y


class Mountain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mid_layer)
        self.image = load_image('menu UI/Mountain.png')
        self.rect = self.image.get_rect()
        self.rect.x = 1096 * factor_x
        self.rect.y = 569 * factor_y


class Ship(pygame.sprite.Sprite):
    def __init__(self, vector):
        super().__init__(all_sprites, mid_layer)
        self.image = choice([ship1_image, ship2_image])
        self.vector = vector
        self.rect = self.image.get_rect()
        self.move_factor = uniform(1, 3)
        if self.vector == -1:
            self.rect.x = WIDTH
            if self.image == ship1_image:
                self.image = pygame.transform.flip(self.image, True, False)
        if self.vector == 1:
            self.rect.x = 0
            if self.image == ship2_image:
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y = randint(0, HEIGHT - self.rect.height * 2)

    def update(self):
        self.rect.x += self.vector * self.move_factor * 60 / fps
        if WIDTH + 10 < self.rect.x or self.rect.x < 0:
            self.__init__(self.vector)


class Cloud(pygame.sprite.Sprite):
    def __init__(self, vector):
        super().__init__(all_sprites, mid_layer)
        self.image = choice([cloud1_image, cloud2_image])
        self.move_factor = uniform(0.9, 1.5)
        self.vector = vector
        self.image = pygame.transform.flip(self.image, choice([True, False]), False)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        if self.vector == -1:
            self.rect.x = WIDTH
        if self.vector == 1:
            self.rect.x = -20
        self.rect.y = randint(0 + 20, HEIGHT - self.rect.height)

    def update(self):
        self.rect.x += self.vector * self.move_factor * 60 / fps
        if WIDTH + 20 < self.rect.x or self.rect.x < 0 - 40:
            self.__init__(self.vector)


class Art(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(all_sprites, mid_layer)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * factor_x
        self.rect.y = y * factor_y

        self.vector = choice([-1, 1])
        self.amplitude = randint(self.rect.height // 15, self.rect.height // 12)
        self.orig_y = self.rect.y

    def update(self):
        self.rect.y += self.vector * 1
        if abs(self.orig_y - self.rect.y) > self.amplitude:
            self.vector = -self.vector


class Gearwheel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mid_layer)
        self.image = load_image('settings UI/1.png')
        self.rect = self.image.get_rect()
        self.rect.x = 1150 * factor_x
        self.rect.y = 280 * factor_y
        self.current = 1

    def update(self):
        self.current = (self.current % 4) + 1
        if self.current == 4:
            self.rect.y = 274 * factor_y
        else:
            self.rect.y = 270 * factor_y
        self.image = load_image(f'settings UI/{self.current}.png')


def initialization():
    all_sprites.empty()
    bottom_layer.empty()
    top_layer.empty()
    mid_layer.empty()
    button_layer.empty()


def play():
    save_count = 0
    save_buttons = []

    def plus():
        nonlocal save_count
        save_count += 1
        save_buttons.append(Button(381, 160 + 151 * (save_count - 1), 'run_game',
                                   load_image(f'select UI/Save {save_count}.png'),
                                   (all_sprites, button_layer), factor_x, factor_y))
        if save_count == 5:
            plus_button.kill()

    initialization()

    bg = Background(load_image('select UI/Background.png'), 0, 0, bottom_layer)
    art1 = Art(load_image('select UI/Cloud 1.png'), 1038, 102)
    art2 = Art(load_image('select UI/Cloud 2.png'), 1168, 245)
    art3 = Art(load_image('select UI/Island 1.png'), 1360, 560)
    art4 = Art(load_image('select UI/Island 2.png'), 1020, 460)
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png'),
                             (all_sprites, button_layer), factor_x, factor_y)
    plus_button = Button(549, 834, plus, load_image('select UI/Plus.png'),
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
                    elif func == 'run_game':
                        return 'run_game'
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

    bg = Background(load_image('settings UI/Background.png'), 0, 0, bottom_layer)
    gear = Gearwheel()
    bookmark_button = Button(350, 0, start_screen, load_image('select UI/Bookmark.png'),
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


all_sprites = pygame.sprite.Group()
bottom_layer = pygame.sprite.Group()
top_layer = pygame.sprite.Group()
mid_layer = pygame.sprite.Group()
button_layer = pygame.sprite.Group()


def start_screen():
    initialization()

    bg = Background(load_image('menu UI/Background.png'), 670, 0, bottom_layer)
    fg = Background(load_image('menu UI/Foreground.png'), 0, 0, top_layer)

    ship1 = Ship(1)
    cloud1 = Cloud(1)
    mountain = Mountain()
    ship2 = Ship(-1)
    cloud2 = Cloud(-1)
    play_button = Button(32, 528, play, load_image('menu UI/PlayButton.png'),
                         (all_sprites, button_layer), factor_x, factor_y)
    settings_button = Button(33, 788, settings, load_image('menu UI/SettingsButton.png'),
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
