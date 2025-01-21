# Это начальная заставка, осталось только кнопки добавить

import os
import sys
from random import choice, randint, uniform

import pygame

pygame.init()
size = width, height = 16 * 96, 9 * 96
# Задается размер экрана с соотношением 16:9, позже это пропишем в другом месте
screen = pygame.display.set_mode(size, pygame.NOFRAME)

factor_x = width / 1920
factor_y = height / 1080
# факторы, которые умножаем на каждый x/y, для работы с размером экрана


def load_image(name, colorkey=None):
    fullname = os.path.join('data/menu UI', name)
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


mountain_image = load_image('Гора.png')
ship1_image = load_image('Корабль 1.png')
ship2_image = load_image('Корабль 2.png')
cloud1_image = load_image('Облако 1.png')
cloud2_image = load_image('облако 2.png')
top_layer_image = load_image('Верхний слой.png')
bottom_layer_image = load_image('Нижний слой.png')


class Background(pygame.sprite.Sprite):
    def __init__(self, layer, group):
        super().__init__(all_sprites, group)
        if layer == 'top':
            self.image = top_layer_image
            self.rect = self.image.get_rect()
            self.rect.x = 0
        else:
            self.image = bottom_layer_image
            self.rect = self.image.get_rect()
            self.rect.x = 670 * factor_x
        self.rect.y = 0


class Mountain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mid_layer)
        self.image = mountain_image
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
            self.rect.x = width
            if self.image == ship1_image:
                self.image = pygame.transform.flip(self.image, True, False)
        if self.vector == 1:
            self.rect.x = 0
            if self.image == ship2_image:
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y = randint(0, height - self.rect.height * 2)

    def update(self):
        self.rect.x += self.vector * self.move_factor
        if width + 10 < self.rect.x or self.rect.x < 0:
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
            self.rect.x = width
        if self.vector == 1:
            self.rect.x = -20
        self.rect.y = randint(0 + 20, height - self.rect.height)

    def update(self):
        self.rect.x += self.vector * self.move_factor
        if width + 20 < self.rect.x or self.rect.x < 0 - 40:
            self.__init__(self.vector)


all_sprites = pygame.sprite.Group()
bottom_layer = pygame.sprite.Group()
top_layer = pygame.sprite.Group()
mid_layer = pygame.sprite.Group()

bg_bottom = Background('bottom', bottom_layer)
bg_top = Background('top', top_layer)

ship1 = Ship(1)
cloud1 = Cloud(1)
mountain = Mountain()
ship2 = Ship(-1)
cloud2 = Cloud(-1)

running = True
FPS = 60
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mid_layer.update()

    screen.fill((0, 0, 0))
    bottom_layer.draw(screen)
    mid_layer.draw(screen)
    top_layer.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
