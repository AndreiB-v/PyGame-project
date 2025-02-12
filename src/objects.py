from math import ceil
from random import choice, randint, uniform

import pygame as pg
import utils as ut


# Класс кнопки
class Button(pg.sprite.Sprite):
    def __init__(self, x, y, function, image, groups):
        super().__init__(groups)
        self.backup_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * ut.factor_x
        self.rect.y = y * ut.factor_y
        self.function = function

        self.size_factor = (self.rect.width / 10 * ut.factor_x, self.rect.height / 10 * ut.factor_y)

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
                self.image = pg.transform.scale(self.image,
                                                (self.rect.width - self.size_factor[0],
                                                 self.rect.height - self.size_factor[1]))
                self.rect.x += self.size_factor[0] / 2
                self.rect.y += self.size_factor[1] / 2


class Slider(pg.sprite.Sprite):
    def __init__(self, x, y, max_value, item, text=None, current=None):
        super().__init__(ut.button_layer)
        # для экрана current_value = 40
        if current:
            self.current_value = current
        else:
            self.current_value = ut.settings[item]
        self.max_value = max_value
        self.image, self.rect, self.bar, self.dot = self.generate_image()
        self.item = item
        if not text:
            self.text = {'x': 0, 'y': 0, 'center': False, 'size': 100}
        else:
            self.text = text

        # Координаты полоски прокрутки
        self.bar.x = (x + self.dot.width) * ut.factor_x
        self.bar.y = (y + self.dot.width // 2) * ut.factor_y
        # Координаты основного спрайта
        self.rect.x = (x - self.dot.width // 2) * ut.factor_x
        self.rect.y = y * ut.factor_y
        # Координаты точки прокрутки
        self.dot.x += self.rect.x
        self.dot.y = self.rect.y

        self.pos = (x, y)
        self.is_active = False

    def generate_image(self):
        slider_bar = ut.load_image('settings UI/slider_bar.png', 'MENU')
        slider_dot = ut.load_image('settings UI/slider_dot.png', 'MENU')
        bar = slider_bar.get_rect()
        dot = slider_dot.get_rect()
        image = pg.Surface((bar.width + dot.width, dot.height), pg.SRCALPHA)
        rect = image.get_rect()
        image.blit(slider_bar, (dot.width // 2, rect.height // 2 - bar.height // 2))
        image.blit(slider_dot, (bar.width / self.max_value * self.current_value, 0))
        dot.x = bar.width / self.max_value * self.current_value
        return image, rect, bar, dot

    def update(self, pos1, mode, pos2=None):
        global settings
        x, y = pos1
        if mode == 'down':
            if self.dot.x <= x <= self.dot.x + self.dot.width and self.dot.y <= y <= self.dot.y + self.dot.height:
                self.is_active = True
                return True
            return False
        elif mode == 'move' and self.is_active:
            x_after, y_after = pos2
            if self.bar.x <= x_after <= self.bar.x + self.bar.width:
                self.current_value = int((x_after - self.bar.x) / (self.bar.width / self.max_value))
            elif x_after > self.bar.x + self.bar.width:
                self.current_value = self.max_value
            else:
                self.current_value = 0
            self.__init__(self.pos[0], self.pos[1], self.max_value, self.item,
                          text=self.text, current=self.current_value)
            self.is_active = True

    def save_changes(self):
        if self.is_active:
            self.is_active = False
            if ut.old_settings[self.item] != self.current_value:
                ut.settings[self.item] = self.current_value
                return True  # возвращает, изменились ли настроки

    def draw_text(self):
        if self.text['center']:
            text = ut.get_text(f'{(self.current_value + 40) * 16}:{(self.current_value + 40) * 9}',
                               (50, 36, 11), font='../data/Berlin-Sans-FB-Demi-Font.ttf',
                               font_size=int(self.text['size'] * ut.factor_x))
        else:
            text = ut.get_text(str(self.current_value), (50, 36, 11),
                               font='../data/Berlin-Sans-FB-Demi-Font.ttf',
                               font_size=int(self.text['size'] * ut.factor_x))
        if self.text['center']:
            ut.screen.blit(text, (self.text['x'] * ut.factor_x - text.get_width() // 2, self.text['y'] * ut.factor_x))
        else:
            ut.screen.blit(text, (self.text['x'] * ut.factor_x, self.text['y'] * ut.factor_x))


# Класс всплывающего окна, используется для диалогов, паузы и т.д (от него следует наследоваться)
class Popup:
    def __init__(self, blackout, color):
        self.popup_layer = pg.sprite.Group()
        self.last_frame = None
        self.buttons = []
        self.active = False

        self.background = pg.Surface(ut.size)
        self.background.fill(color)
        self.background.set_alpha(blackout)

    def update(self, pos, mode):
        for i in self.buttons:
            value = i.update(pos, mode)
            if value:
                self.active = False
                return value

    def draw_popup(self, screen):
        screen.blit(self.last_frame, (0, 0))
        screen.blit(self.background, (0, 0))

    def set_active(self, screen):
        self.active = True
        self.last_frame = pg.Surface(ut.size)
        self.last_frame.blit(screen, (0, 0))


# Класс диалога: question - вопрос, x_activation - позиция x на карте, y_activation - позиция y на карте,
# radius - радиус на котором действует активация, *answers - ответы
class Dialog(Popup):
    def __init__(self, question, x_activation, y_activation, radius, *answers):
        super().__init__(100, (255, 255, 255))
        self.question = question
        self.answers = answers
        self.radius = radius
        self.x = x_activation
        self.y = y_activation

        for answer in enumerate(self.answers):
            button = ut.load_image('buttons/Empty.png', 'MENU')

            font = pg.font.Font('../data/DoubleBass-Regular-trial.ttf', int(50 * ut.factor_x))
            text = font.render(answer[1], 1, (208, 185, 14))
            text_w = text.get_width()
            text_h = text.get_height()
            text_x = button.get_rect().width * 0.5 - text_w // 2
            text_y = button.get_rect().height * 0.5 - text_h // 2
            button.blit(text, (text_x, text_y))

            self.buttons.append(Button(ut.width * 0.05, 50 + 250 * answer[0], answer[1],
                                       button, self.popup_layer))

    # Функция возвращает, является ли точка в радиусе активации анимации
    def check_pos(self, x, y):
        return abs(x - self.x) <= self.radius and abs(y - self.y) <= self.radius

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pg.draw.rect(screen, (208, 185, 14), ((0, ut.height * 0.72), (ut.width, ut.height)))
        pg.draw.rect(screen, (50, 36, 11), ((0, ut.height * 0.75), (ut.width, ut.height)))

        self.popup_layer.draw(screen)

        font = pg.font.Font('../data/DoubleBass-Regular-trial.ttf', 40)
        text = font.render(self.question, 1, (208, 185, 14))
        text_x = ut.width * 0.5 - text.get_width() // 2
        text_y = ut.height * 0.85 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


# Класс паузы
class Pause(Popup):
    def __init__(self):
        super().__init__(150, (0, 0, 0))
        self.buttons.append(Button(1920 / 2 - 180, 1080 / 2.5 - 180, 'return',
                                   ut.load_image('buttons/ReturnToGame.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 + 400 - 140, 1080 / 2.5 - 121, 'select_save',
                                   ut.load_image('buttons/Over.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 - 400 - 140, 1080 / 2.5 - 121, 'settings',
                                   ut.load_image('buttons/Settings.png', 'MENU'), self.popup_layer))

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pg.draw.rect(screen, (208, 185, 14), ((0, ut.height * 0.72), (ut.width, ut.height)))
        pg.draw.rect(screen, (50, 36, 11), ((0, ut.height * 0.75), (ut.width, ut.height)))
        self.popup_layer.draw(screen)

        text = ut.get_text('ИГРА ОСТАНОВЛЕНА', (205, 185, 3),
                           font='../data/DoubleBass-Regular-trial.ttf',
                           font_size=int(100 * ut.factor_x))
        screen.blit(text, (ut.width * 0.5 - text.get_width() // 2, ut.height * 0.85 - text.get_height() // 2))


class EndGame(Popup, pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self, ut.all_sprites, ut.top_layer)
        Popup.__init__(self, 100, (255, 255, 255))
        self.image = ut.load_image('images/flag.png')
        self.image = pg.transform.scale(self.image, (100 * 0.58, 100 * 0.58))  # (100 * FACTOR_X, 100 * FACTOR_Y)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.buttons.append(Button(1920 / 2 + 200 - 140, 1080 / 2.5 - 121, 'start_screen',
                                   ut.load_image('buttons/Over.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 - 200 - 140, 1080 / 2.5 - 121, 'quit',
                                   ut.load_image('buttons/Off.png', 'MENU'), self.popup_layer))

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pg.draw.rect(screen, (208, 185, 14), ((0, ut.height * 0.72), (ut.width, ut.height)))
        pg.draw.rect(screen, (50, 36, 11), ((0, ut.height * 0.75), (ut.width, ut.height)))
        self.popup_layer.draw(screen)

        font = pg.font.Font('../data/DoubleBass-Regular-trial.ttf',
                            int(100 * ut.factor_x))
        text = font.render('ИГРА ПРОЙДЕНА', 1, (205, 185, 3))
        text_x = ut.width * 0.5 - text.get_width() // 2
        text_y = ut.height * 0.85 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


# Класс шестерёнки (это из экрана Settings)
class Gearwheel(pg.sprite.Sprite):
    def __init__(self):
        super().__init__(ut.all_sprites, ut.mid_layer)
        self.image = ut.load_image('settings UI/1.png', 'MENU')
        self.rect = self.image.get_rect()
        self.rect.x = 1150 * ut.factor_x
        self.rect.y = 280 * ut.factor_y
        self.current = 1

    def update(self):
        self.current = (self.current % 4) + 1
        if self.current == 4:
            self.rect.y = 274 * ut.factor_y
        else:
            self.rect.y = 270 * ut.factor_y
        self.image = ut.load_image(f'settings UI/{self.current}.png', 'MENU')


# Класс арт (это из экрана Select save, производит анимацию парения (вверх/вниз)
class Art(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(ut.all_sprites, ut.mid_layer)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * ut.factor_x
        self.rect.y = y * ut.factor_y

        self.vector = choice([-1, 1])
        self.amplitude = randint(self.rect.height // 15, self.rect.height // 12)
        self.orig_y = self.rect.y

    def update(self):
        self.rect.y += self.vector * 1
        if abs(self.orig_y - self.rect.y) > self.amplitude:
            self.vector = -self.vector


# Класс облака (это из экрана Start screen, движется туда/сюда)
class Cloud(pg.sprite.Sprite):
    def __init__(self, vector):
        super().__init__(ut.all_sprites, ut.mid_layer)
        self.image = choice([ut.load_image('menu UI/Cloud 1.png', 'MENU'),
                             ut.load_image('menu UI/Cloud 2.png', 'MENU')])
        self.move_factor = uniform(0.9, 1.5)
        self.vector = vector
        self.image = pg.transform.flip(self.image, choice([True, False]), False)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        if self.vector == -1:
            self.rect.x = ut.width
        if self.vector == 1:
            self.rect.x = -20
        self.rect.y = randint(0 + 20, ut.height - self.rect.height)

    def update(self):
        self.rect.x += self.vector * self.move_factor * 60 / ut.fps
        if ut.width + 20 < self.rect.x or self.rect.x < 0 - 40:
            self.__init__(self.vector)


class BgCloud(pg.sprite.Sprite):
    def __init__(self, group, clouds, screen_width, screen_height):
        super().__init__(group)
        self.image = choice(clouds)
        self.rect = self.image.get_rect()
        self.screen_width = screen_width * 16
        self.screen_height = screen_height * 16

        self.direction = choice([-1, 1])

        # Устанавливаем начальную позицию облака
        if self.direction == 1:  # Спавн слева
            self.rect.x = -self.rect.width
        else:  # Спавн справа
            self.rect.x = self.screen_width
            self.image = pg.transform.flip(self.image, True, False)  # Отразить облако

        self.rect.y = randint(0, self.screen_height - self.rect.height)  # Высота спавна

        self.speed = uniform(1.2, 3.5) * self.direction

    def update(self, *args):
        self.rect.x += int(self.speed)  # Приводим к int для гарантированного движения

        # Если облако ушло за экран — создаём его заново
        if self.rect.x > self.screen_width or self.rect.x < -self.rect.width:
            self.rect.x = -self.rect.width if self.direction == 1 else self.screen_width
            self.rect.y = randint(0, self.screen_height - self.rect.height)  # Новая высота
            self.speed = uniform(1.2, 3.5) * self.direction  # Перегенерируем скорость


# Класс корабля (это из экрана Start screen, движется туда/сюда + поворачивает объект)
class Ship(pg.sprite.Sprite):
    def __init__(self, vector, width, height, group):
        super().__init__(ut.all_sprites, group)
        ship1_image = ut.load_image('menu UI/Ship 1.png', 'MENU')
        ship2_image = ut.load_image('menu UI/Ship 2.png', 'MENU')
        self.image = choice([ship1_image, ship2_image])
        self.vector = vector
        self.rect = self.image.get_rect()
        self.move_factor = uniform(1, 3)
        self.width = width
        self.height = height
        self.group = group
        if self.vector == -1:
            self.rect.x = self.width
            if self.image == ship1_image:
                self.image = pg.transform.flip(self.image, True, False)
        if self.vector == 1:
            self.rect.x = 0
            if self.image == ship2_image:
                self.image = pg.transform.flip(self.image, True, False)
        # self.rect.y = randint(0, self.height - self.rect.height * 2)

    def update(self):
        self.rect.x += self.vector * self.move_factor * 60 / ut.fps
        if self.width + 10 < self.rect.x or self.rect.x < 0:
            self.__init__(self.vector, self.width, self.height, self.group)


# Класс горы (это из экрана Start screen, статичное говно)
class Mountain(pg.sprite.Sprite):
    def __init__(self):
        super().__init__(ut.all_sprites, ut.mid_layer)
        self.image = ut.load_image('menu UI/Mountain.png', 'MENU')
        self.rect = self.image.get_rect()
        self.rect.x = 1096 * ut.factor_x
        self.rect.y = 569 * ut.factor_y


# Класс заднего фона (можно использовать где угодно)
class Background(pg.sprite.Sprite):
    def __init__(self, image, x, y, group):
        super().__init__(ut.all_sprites, group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * ut.factor_x
        self.rect.y = y * ut.factor_y


class Event:
    def __init__(self, duration, cooldown):
        self.duration = duration  # в миллисекундах
        self.cooldown = cooldown  # Время ожидания между событиями в миллисекундах
        self.is_active = False

        self.last_activation = 0  # Обязательно int значение
        self.start_time = None

    def time_check(self):
        return pg.time.get_ticks() - self.last_activation >= self.cooldown

    def activation(self):
        current_time = pg.time.get_ticks()
        self.is_active = True
        self.last_activation = current_time
        self.start_time = current_time

    def __bool__(self):
        return self.is_active


class Health(pg.sprite.Sprite):
    def __init__(self, max_health, indent, size_factor):
        super().__init__(ut.all_sprites, ut.top_layer)

        self.current_health = max_health  # текущее здоровье
        self.max = max_health  # максимальное здоровье
        self.factor = size_factor  # меняет размер сердец на экране
        self.indent = indent  # отступ между сердцами в пикселях

        self.image = None
        self.rect = None

        self.update_image()

    def update_image(self):
        if self.current_health > 0:
            size_width = ceil(self.current_health / 2) * 135 + self.indent * ceil(self.current_health / 2) - self.indent
            self.image = pg.Surface((size_width, 114))
            self.rect = self.image.get_rect()
            self.rect.x = 20
            for heart in range(int(self.current_health) // 2):
                self.image.blit(ut.load_image('images/health/full hp.png'), (heart * 135 + heart * self.indent, 0))
            if self.current_health % 2 == 1:
                self.image.blit(ut.load_image('images/health/half hp.png'), (self.rect.width - 135, 0))
            self.image = pg.transform.scale(self.image,
                                            (size_width * self.factor * 0.9, 114 * self.factor))
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect()

    def synchron_pos(self, target, indent_x, indent_y):
        self.rect.center = target.rect.center
        self.rect.y += indent_y
        self.rect.x += indent_x

    def __bool__(self):
        return bool(int(self.current_health) // 1)

    def __isub__(self, value):
        self.current_health -= value
        if self.current_health < 1:
            self.current_health = 0
        self.update_image()
        return self

    def __iadd__(self, value):
        self.current_health += value
        self.update_image()
        return self
