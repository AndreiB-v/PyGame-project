# Файл для вспомогательных функций
import json
import os
import sys
import pygame

with open('../settings.json') as file:
    settings = json.load(file)

# Задаем основные настраиваемые параметры из settings.json
# fps и volume НЕ константы так как будут меняться в настройках в реальном времени
# для изменения размера экрана мы будем использовать перезаход в игру, так что они константы
fps = settings['FPS']
volume = settings['FPS']
SIZE = WIDTH, HEIGHT = 16 * settings['SIZE FACTOR'], 9 * settings['SIZE FACTOR']

# Инициализируем pygame
pygame.init()
clock = pygame.time.Clock()

# Задается размер экрана с соотношением 16:9, позже это пропишем в другом месте
screen = pygame.display.set_mode(SIZE, pygame.NOFRAME)

# факторы, которые умножаем на каждый x/y, для работы с размером экрана
FACTOR_X = WIDTH / 1920
FACTOR_Y = HEIGHT / 1080

# Определяем группы спрайтов
all_sprites = pygame.sprite.Group()
bottom_layer = pygame.sprite.Group()
top_layer = pygame.sprite.Group()
mid_layer = pygame.sprite.Group()
button_layer = pygame.sprite.Group()
player_group = pygame.sprite.Group()


# Полностью очищаем объекты прошлой сцены
def initialization():
    all_sprites.empty()
    bottom_layer.empty()
    top_layer.empty()
    mid_layer.empty()
    button_layer.empty()
    player_group.empty()


# Функция для добавления изображений
def load_image(name, mode=None):
    fullname = os.path.join('../data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if mode == 'CHROMAKEY':
        image = image.convert()
        if mode == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    elif mode == 'MENU':
        x = image.get_width()
        y = image.get_height()
        image = pygame.transform.scale(image, (x * FACTOR_X, y * FACTOR_Y))
        image = image.convert_alpha()
    return image


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
        image = load_image(full_path)
        image = pygame.transform.scale(image, (100 * FACTOR_X, 87 * FACTOR_Y))
        frames.append(image)

    return frames
