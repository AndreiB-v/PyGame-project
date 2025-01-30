# Файл для вспомогательных функций
# Типа загрузки изображения, карты или музыки


import os
import sys
import pygame
from pytmx import load_pygame

FPS = 60
clock = pygame.time.Clock()
size = width, height = 16 * 79, 9 * 78

factor_x = width / 1920
factor_y = height / 1080


# Функция для добавления изображений
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


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, function, image, groups, factor_x, factor_y):
        super().__init__(groups)
        self.backup_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * factor_x
        self.rect.y = y * factor_y
        self.function = function

        self.size_factor = (self.rect.width / 10 * factor_x, self.rect.height / 10 * factor_y)

    def update(self, *args):
        x, y = args[0]
        pressed = (self.rect.x <= x <= self.rect.x + self.rect.width
                   and self.rect.y <= y <= self.rect.y + self.rect.height)
        if self.image != self.backup_image and args[1] == 'up':
            self.image = self.backup_image
            self.rect.x -= self.size_factor[0] / 2
            self.rect.y -= self.size_factor[1] / 2
            if pressed:
                return self.function
        if pressed:
            if args[1] == 'down':
                self.image = pygame.transform.scale(self.image,
                                                    (self.rect.width - self.size_factor[0],
                                                     self.rect.height - self.size_factor[1]))
                self.rect.x += self.size_factor[0] / 2
                self.rect.y += self.size_factor[1] / 2


# Функция для получения всех кадров анмиации
def load_animation(folder_path):
    # Путь к папке, где лежат кадры
    base_folder = os.path.join("../data/images", folder_path)

    if not os.path.isdir(base_folder):
        print(f"Папка {base_folder} не найдена")
        sys.exit()

    # Получаем все файлы в папке base_folder
    files = sorted(os.listdir(base_folder))
    frames = []

    for file_name in files:
        full_path = os.path.join(base_folder, file_name)
        image = load_image(full_path, True)
        image = pygame.transform.scale(image, (70 * factor_x, 80 * factor_y))
        frames.append(image)

    return frames
