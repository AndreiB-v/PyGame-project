# Файл для вспомогательных функций
# Типа зарзрузки изображения, карты или музыки
# Для структурирования кода, поэтому - пиши сюда специальные функции


import os
import sys
import pygame


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
        image = load_image(full_path, True)
        image = pygame.transform.scale(image, (70, 80))
        frames.append(image)

    return frames



