# Файл для вспомогательных функций
import json
import os
import sys
from math import sin

import pygame

with open('../settings.json') as file:
    settings = json.load(file)

# Задаем основные настраиваемые параметры из settings.json
# fps и volume НЕ константы так как будут меняться в настройках в реальном времени
# для изменения размера экрана мы будем использовать перезаход в игру, так что они константы
fps = settings['FPS']
volume = settings['FPS']
app_bar = settings['APP BAR']
# Задается размер экрана с соотношением 16:9
SIZE = WIDTH, HEIGHT = 16 * settings['SIZE FACTOR'], 9 * settings['SIZE FACTOR']

# Инициализируем pygame
pygame.init()
clock = pygame.time.Clock()

# Создается экран, в зависимости от настроек
if app_bar:
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Корабли ходят по небу")
else:
    screen = pygame.display.set_mode(SIZE, pygame.NOFRAME)

# факторы, которые умножаем на каждый x/y, для работы с размером экрана
FACTOR_X = WIDTH / 1920
FACTOR_Y = HEIGHT / 1080

# Определяем группы спрайтов
ships_layer = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
bottom_layer = pygame.sprite.Group()
top_layer = pygame.sprite.Group()
mid_layer = pygame.sprite.Group()
button_layer = pygame.sprite.Group()
player_group = pygame.sprite.Group()


# Полностью очищаем объекты прошлой сцены
def initialization():
    ships_layer.empty()
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
    # мод хромакея, удаляет задний фон
    if mode:
        if 'CHROMAKEY' in mode:
            image = image.convert()
            if mode == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        # мод меню, она
        if 'MENU' in mode:
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


# Функция, которой передаёшь градус, радиус и центр окр-ти, и получаешь координаты этой точки окружности
def return_dot(degree, radius, x, y):
    n = degree % 360
    radian = n * 3.141592653589793 / 180
    side_x = radius * sin(radian)
    side_y = (radius ** 2 - side_x ** 2) ** 0.5
    ch_t = n // 90 + 1 if n / 90 >= n // 90 else n // 90
    if ch_t in (1, 4):
        side_y = -side_y
    return x + side_x * FACTOR_X, y + side_y * FACTOR_Y


# Рендер класса, унаследованного от Popup, это отдельный цикл, обрабатывающий все нажатия и т.д,
# приостанавливает цикл, где был вызван до тех пор, пока не возвратит какое-либо значение, полученное от кнопок Popup
def render_popup(popup_class):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                popup_class.update(event.pos, 'down')
            if event.type == pygame.MOUSEBUTTONUP:
                value = popup_class.update(event.pos, 'up')
                if value:
                    return value

        screen.fill((0, 0, 0))
        popup_class.draw_popup(screen)

        pygame.display.flip()
        clock.tick(fps)
