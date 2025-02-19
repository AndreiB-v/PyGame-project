# Файл для вспомогательных функций
import os
import sqlite3
import sys
from math import sin
import json

import pygame as pg

with open('../settings.json') as file:
    settings = json.load(file)

old_settings = dict(settings)  # сохраняем текущие настройки
fps = settings['FPS']  # фпс
volume = settings['SOUNDS VOLUME']  # громкость звука
app_bar = settings['APP BAR']  # верхняя панель
size_factor = settings['SIZE FACTOR'] + 40  # фактор экрана

# Инициализируем pygame
pg.init()
clock = pg.time.Clock()

# Определяем группы спрайтов
all_sprites = pg.sprite.Group()
bottom_layer = pg.sprite.Group()
mid_layer = pg.sprite.Group()
top_layer = pg.sprite.Group()
button_layer = pg.sprite.Group()


def sounds_init():
    sounds_names = ['die_character', 'die_skeleton', 'hit_air', 'hit_target', 'dialog_activation']
    all_sounds = {}
    for name in sounds_names:
        sound = pg.mixer.Sound(f'../data/sounds/{name}.wav')
        sound.set_volume(volume * 0.01)
        all_sounds[name] = sound
    return all_sounds


def screen_init():
    pg.display.quit()
    pg.display.init()
    # Создается экран, в зависимости от настроек
    if app_bar:
        surface = pg.display.set_mode(size)
        pg.display.set_icon(pg.image.load('../data/images/icon.png'))
        pg.display.set_caption("Корабли ходят по небу")
    else:
        surface = pg.display.set_mode(size, pg.NOFRAME)
    return surface


# Задается размер экрана с соотношением 16:9
size = width, height = 16 * size_factor, 9 * size_factor  # (40 - наименьшее, 120 - наибольшее)

# факторы, которые умножаем на каждый x/y, для работы с размером экрана
factor_x = width / 1920
factor_y = height / 1080

screen = screen_init()
sounds = sounds_init()


# Полностью очищаем объекты прошлой сцены
def initialization():
    all_sprites.empty()
    bottom_layer.empty()
    mid_layer.empty()
    top_layer.empty()
    button_layer.empty()


# Функция для добавления изображений
def load_image(filename, mode=None, factors=(factor_x, factor_y)):
    fullname = os.path.join('../data', filename)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)

    im_width = image.get_width()
    im_height = image.get_height()
    if mode:
        # мод хромакея, удаляет задний фон
        if 'CHROMAKEY' in mode:
            image = image.convert()
            if mode == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        # мод для UI интерфейса
        if 'MENU' in mode:
            image = pg.transform.scale(image, (im_width * factor_x, im_height * factor_y))
        if 'CUSTOM_SIZE' in mode:
            image = pg.transform.scale(image, (im_width * factors[0], im_height * factors[1]))
        image = image.convert_alpha()
    return image


# Получение всех картинок
def get_images(directory):
    files = os.listdir(directory)  # Имена всех файлов
    return files


# Функция для получения всех кадров анимации
def load_animation(folder_path, enemy):
    # Путь к папке, где лежат кадры
    base_folder = os.path.join("../data/images", enemy, folder_path)

    if not os.path.isdir(base_folder):
        print(f"Папка {base_folder} не найдена")
        sys.exit()

    # Получаем все файлы в папке base_folder
    files = sorted(os.listdir(base_folder))
    frames = []

    for file_name in files:
        full_path = os.path.join(base_folder, file_name)
        image = load_image(full_path)
        image = pg.transform.scale(image, (100 * 0.58, 87 * 0.58))  # (100 * FACTOR_X, 87 * FACTOR_Y)
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
    return x + side_x * 0.58, y + side_y * 0.58


# Рендер класса, унаследованного от Popup, это отдельный цикл, обрабатывающий все нажатия и т.д,
# приостанавливает цикл, где был вызван до тех пор, пока не возвратит какое-либо значение, полученное от кнопок Popup
def render_popup(popup_class):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'quit'
            if event.type == pg.MOUSEBUTTONDOWN:
                popup_class.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                value = popup_class.update(event.pos, 'up')
                if value:
                    return value

        screen.fill((0, 0, 0))
        popup_class.draw_popup(screen)

        pg.display.flip()
        clock.tick(fps)


def create_connect(func):
    def decorated_func(*args, **kwargs):
        con = sqlite3.connect("../data/database/db.sqlite")
        cur = con.cursor()
        result = func(*args, **kwargs, cur=cur)
        con.commit()
        con.close()
        return result

    return decorated_func


def get_text(text, color=(0, 0, 0), font=None, font_size=50, rect=(1000, 1000)):
    init_font = pg.font.Font(font, int(font_size))
    while init_font.size(text)[0] > rect[0] or init_font.size(text)[1] > rect[1]:
        font_size -= 1
        init_font = pg.font.Font(font, int(font_size))
    text_surface = init_font.render(text, 1, color)
    return text_surface


# меняет и сохраняет настройки и возвращает, был ли изменен экран
def update_settings():
    global fps, volume, app_bar, size_factor, size, width, height, \
        screen, factor_x, factor_y, old_settings, settings, sounds

    if settings['FPS'] == 0:
        settings['FPS'] = 1

    with open('../settings.json', 'w') as settings_file:
        json.dump(settings, settings_file)

    fps = settings['FPS']
    volume = settings['SOUNDS VOLUME']
    app_bar = settings['APP BAR']
    size_factor = settings['SIZE FACTOR'] + 40
    size = width, height = 16 * size_factor, 9 * size_factor
    factor_x = width / 1920
    factor_y = height / 1080
    if size_factor - 40 != old_settings['SIZE FACTOR'] or app_bar != old_settings['APP BAR']:
        screen = screen_init()
    sounds = sounds_init()

    old_settings = dict(settings)
