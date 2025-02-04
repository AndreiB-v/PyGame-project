from random import choice, randint, uniform

import pygame.font

from src.animation import Animation
from utils import *

ship1_image = load_image('menu UI/Ship 1.png', 'MENU')
ship2_image = load_image('menu UI/Ship 2.png', 'MENU')

# Класс кнопки
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, function, image, groups):
        super().__init__(groups)
        self.backup_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * FACTOR_X
        self.rect.y = y * FACTOR_Y
        self.function = function

        self.size_factor = (self.rect.width / 10 * FACTOR_X, self.rect.height / 10 * FACTOR_Y)

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


# Класс всплывающего окна, используется для диалогов, паузы и т.д (от него следует наследоваться)
class Popup:
    def __init__(self, blackout, color):
        self.popup_layer = pygame.sprite.Group()
        self.last_frame = None
        self.buttons = []
        self.active = False

        self.background = pygame.Surface(screen.get_size())
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
        self.last_frame = pygame.Surface(screen.get_size())
        self.last_frame.blit(screen, (0, 0))


# Класс диалога: question - вопрос, x_activation - позиция x на карте, y_activation - позиция y на карте,
# radius - радиус на котором действует активация, *answers - ответы
class Dialog(Popup):
    def __init__(self, question, x_activation, y_activation, radius, *answers):
        super().__init__(100, (255, 255, 255))
        self.question = question
        self.radius = radius
        self.x = x_activation
        self.y = y_activation

        for answer in enumerate(answers):
            button = load_image('buttons/Empty.png', 'MENU')

            font = pygame.font.Font('../data/DoubleBass-Regular-trial.ttf', int(50 * FACTOR_X))
            text = font.render(answer[1], 1, (208, 185, 14))
            text_w = text.get_width()
            text_h = text.get_height()
            text_x = button.get_rect().width * 0.5 - text_w // 2
            text_y = button.get_rect().height * 0.5 - text_h // 2
            button.blit(text, (text_x, text_y))

            self.buttons.append(Button(WIDTH * 0.05, 50 + 250 * answer[0], answer[1],
                                       button, self.popup_layer))

    # Функция возвращает, является ли точка в радиусе активации анимации
    def check_pos(self, x, y):
        return abs(x - self.x) <= self.radius and abs(y - self.y) <= self.radius

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pygame.draw.rect(screen, (208, 185, 14), ((0, HEIGHT * 0.72), (WIDTH, HEIGHT - HEIGHT * 0.75)))
        pygame.draw.rect(screen, (50, 36, 11), ((0, HEIGHT * 0.75), (WIDTH, HEIGHT - HEIGHT * 0.75)))

        self.popup_layer.draw(screen)

        font = pygame.font.Font('../data/DoubleBass-Regular-trial.ttf', 40)
        text = font.render(self.question, 1, (208, 185, 14))
        text_x = WIDTH * 0.5 - text.get_width() // 2
        text_y = HEIGHT * 0.85 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


# Класс паузы
class Pause(Popup):
    def __init__(self):
        super().__init__(150, (0, 0, 0))
        self.buttons.append(Button(1920 / 2 - 180, 1080 / 2.5 - 180, 'return',
                                   load_image('buttons/ReturnToGame.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 + 400 - 140, 1080 / 2.5 - 121, 'start_screen',
                                   load_image('buttons/Over.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 - 400 - 140, 1080 / 2.5 - 121, 'settings',
                                   load_image('buttons/Settings.png', 'MENU'), self.popup_layer))

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pygame.draw.rect(screen, (208, 185, 14), ((0, HEIGHT * 0.72), (WIDTH, HEIGHT - HEIGHT * 0.75)))
        pygame.draw.rect(screen, (50, 36, 11), ((0, HEIGHT * 0.75), (WIDTH, HEIGHT - HEIGHT * 0.75)))
        self.popup_layer.draw(screen)

        font = pygame.font.Font('../data/DoubleBass-Regular-trial.ttf',
                                int(100 * FACTOR_X))
        text = font.render('ИГРА ОСТАНОВЛЕНА', 1, (205, 185, 3))
        text_x = WIDTH * 0.5 - text.get_width() // 2
        text_y = HEIGHT * 0.85 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


class EndGame(Popup, pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, all_sprites, mid_layer)
        Popup.__init__(self, 100, (255, 255, 255))
        self.image = load_image('images/flag.png')
        self.image = pygame.transform.scale(self.image, (100 * FACTOR_X, 100 * FACTOR_Y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.buttons.append(Button(1920 / 2 + 200 - 140, 1080 / 2.5 - 121, 'start_screen',
                                   load_image('buttons/Over.png', 'MENU'), self.popup_layer))
        self.buttons.append(Button(1920 / 2 - 200 - 140, 1080 / 2.5 - 121, 'quit',
                                   load_image('buttons/Off.png', 'MENU'), self.popup_layer))

    def draw_popup(self, screen):
        super().draw_popup(screen)

        pygame.draw.rect(screen, (208, 185, 14), ((0, HEIGHT * 0.72), (WIDTH, HEIGHT - HEIGHT * 0.75)))
        pygame.draw.rect(screen, (50, 36, 11), ((0, HEIGHT * 0.75), (WIDTH, HEIGHT - HEIGHT * 0.75)))
        self.popup_layer.draw(screen)

        font = pygame.font.Font('../data/DoubleBass-Regular-trial.ttf',
                                int(100 * FACTOR_X))
        text = font.render('ИГРА ПРОЙДЕНА', 1, (205, 185, 3))
        text_x = WIDTH * 0.5 - text.get_width() // 2
        text_y = HEIGHT * 0.85 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


# Класс шестерёнки (это из экрана Settings)
class Gearwheel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mid_layer)
        self.image = load_image('settings UI/1.png', 'MENU')
        self.rect = self.image.get_rect()
        self.rect.x = 1150 * FACTOR_X
        self.rect.y = 280 * FACTOR_Y
        self.current = 1

    def update(self):
        self.current = (self.current % 4) + 1
        if self.current == 4:
            self.rect.y = 274 * FACTOR_Y
        else:
            self.rect.y = 270 * FACTOR_Y
        self.image = load_image(f'settings UI/{self.current}.png', 'MENU')


# Класс арт (это из экрана Select save, производит анимацию парения (вверх/вниз)
class Art(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(all_sprites, mid_layer)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * FACTOR_X
        self.rect.y = y * FACTOR_Y

        self.vector = choice([-1, 1])
        self.amplitude = randint(self.rect.height // 15, self.rect.height // 12)
        self.orig_y = self.rect.y

    def update(self):
        self.rect.y += self.vector * 1
        if abs(self.orig_y - self.rect.y) > self.amplitude:
            self.vector = -self.vector


# Класс облака (это из экрана Start screen, движется туда/сюда)
class Cloud(pygame.sprite.Sprite):
    def __init__(self, vector):
        super().__init__(all_sprites, mid_layer)
        self.image = choice([load_image('menu UI/Cloud 1.png', 'MENU'),
                             load_image('menu UI/Cloud 2.png', 'MENU')])
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


# Класс корабля (это из экрана Start screen, движется туда/сюда + поворачивает объект)
class Ship(pygame.sprite.Sprite):
    def __init__(self, vector, width, height, group):
        super().__init__(all_sprites, group)
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
                self.image = pygame.transform.flip(self.image, True, False)
        if self.vector == 1:
            self.rect.x = 0
            if self.image == ship2_image:
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y = randint(0, self.height - self.rect.height * 2)

    def update(self):
        self.rect.x += self.vector * self.move_factor * 60 / fps
        if self.width + 10 < self.rect.x or self.rect.x < 0:
            self.__init__(self.vector, self.width, self.height, self.group)

# Класс горы (это из экрана Start screen, статичное говно)
class Mountain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mid_layer)
        self.image = load_image('menu UI/Mountain.png', 'MENU')
        self.rect = self.image.get_rect()
        self.rect.x = 1096 * FACTOR_X
        self.rect.y = 569 * FACTOR_Y


# Класс заднего фона (можно использовать где угодно)
class Background(pygame.sprite.Sprite):
    def __init__(self, image, x, y, group):
        super().__init__(all_sprites, group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * FACTOR_X
        self.rect.y = y * FACTOR_Y


# Класс платформы, перенесено из main
class Platform(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height, group):
        super().__init__(group)
        self.image = pygame.Surface((width * FACTOR_X, height * FACTOR_Y), pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        # self.image.fill((50, 36, 11), (10, 10, width, height))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * FACTOR_X
        self.rect.y = pos_y * FACTOR_Y


# Класс игрока, перенесено из main
class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos, *args):
        super().__init__(group)

        self.all_group = args[0]
        self.die_blocks_group = args[1]

        # Прописываем физические параметры
        self.gravity = 0.6

        # Прописываем параметры игрока
        self.fall_speed = 0
        self.jump_strength = -12.5
        self.is_ground = False
        self.pos = pos
        self.double_jump_available = False

        # Параметры для рывка
        self.can_dash = True
        self.dash_cooldown = 500  # Время ожидания между рывками в миллисекундах
        self.last_dash_time = 0
        self.is_moving = False
        self.is_dashing = False
        self.direction = "right"

        self.dash_duration = 200  # Длительность рывка в миллисекундах
        self.dash_start_time = None
        self.start_pos = None
        self.end_pos = None
        self.dash_speed = 150  # Смещение при рывке

        # Группы анимаций принадлежащих игроку
        self.animations = {"move_right": Animation("walk", frame_rate=200),
                           "move_left": Animation("walk", frame_rate=200, flip_horizontal=True),
                           "idle_right": Animation("idle", frame_rate=200),
                           "idle_left": Animation("idle", frame_rate=200, flip_horizontal=True),
                           "jump_right": Animation("jump", frame_rate=180),
                           "jump_left": Animation("jump", frame_rate=180, flip_horizontal=True),
                           "dash_right": Animation("dash", frame_rate=180),
                           "dash_left": Animation("dash", frame_rate=180, flip_horizontal=True)}
        self.current_animation = self.animations["idle_right"]

        # Создаём спрайт игрока
        self.image = self.current_animation.get_frame()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos

        # Создаем отступы от маски, именно они образуют хит-бокс
        self.mask = pygame.mask.from_surface(self.image)
        self.left_indent = min(self.mask.outline(), key=lambda x: x[0])
        self.right_indent = self.rect.width - max(self.mask.outline(), key=lambda x: x[0])[0] - 1
        self.top_indent = self.rect.height - max(self.mask.outline(), key=lambda x: x[1])[1] - 1

    def set_animation(self, animation_name):
        if self.current_animation != self.animations[animation_name]:
            self.current_animation = self.animations[animation_name]
            self.current_animation.current_frame = 0
        elif animation_name == "idle":
            self.current_animation.current_frame = 0

    def move(self, direction):
        if direction == "right":
            self.rect.x += 5 * FACTOR_X * 60 / fps
            self.set_animation("move_right")

        elif direction == "left":
            self.rect.x -= 5 * FACTOR_X * 60 / fps
            self.set_animation("move_left")

        self.is_moving = True

    def dash(self, direction):
        current_time = pygame.time.get_ticks()

        if self.can_dash and (current_time - self.last_dash_time >= self.dash_cooldown):
            # Запоминаем начальную и конечную позиции для плавного движения
            self.start_pos = self.rect.x
            if direction == "right":
                self.set_animation("dash_right")
                self.end_pos = self.start_pos + self.dash_speed * FACTOR_X
            elif direction == "left":
                self.end_pos = self.start_pos - self.dash_speed * FACTOR_X
                self.set_animation("dash_left")

            # Устанавливаем время начала рывка
            self.dash_start_time = current_time
            self.can_dash = False
            self.last_dash_time = current_time

    def jump(self):
        self.rect.y += 1
        if self.is_ground:
            hits_after = pygame.sprite.spritecollide(self, self.all_group, False)
            for hit in hits_after:
                if pygame.sprite.collide_mask(self, hit):
                     if self.rect.y + self.rect.height - round(FACTOR_Y + 1) * 1 - 1 == hit.rect.y:
                        self.fall_speed = self.jump_strength
                        self.is_ground = False
                        self.double_jump_available = True  # Разрешаем двойной прыжок
                        self.set_animation(f"jump_{self.direction}")
                        break
        else:
            if self.double_jump_available:
                self.fall_speed = self.jump_strength
                self.double_jump_available = False
                self.set_animation(f"jump_{self.direction}")

    def wall_collision(self):
        # получаем пересекаемые объекты и перебираем каждый отдельно
        hits = pygame.sprite.spritecollide(self, self.all_group, False)
        for hit in hits:
            # Если маски пересекаются
            if pygame.sprite.collide_mask(self, hit):
                # Считаем расстояние игрока относительно объекта, с которым он пересекается
                # и смещаем его на наименьшее (top_side для избежания багов)
                left_side = abs(hit.rect.x + hit.rect.width - self.rect.x)
                right_side = abs(self.rect.x + self.rect.width - hit.rect.x)
                top_side = abs(self.rect.y + self.rect.height - hit.rect.y)
                if min(left_side, right_side, top_side) == left_side:
                    # По скольку эта функция работает, когда упираешься в стенки
                    self.is_dashing = False
                    self.dash_start_time = None

                    self.rect.x = hit.rect.x + hit.rect.width - self.left_indent
                elif min(left_side, right_side, top_side) == right_side:
                    self.is_dashing = False
                    self.dash_start_time = None

                    self.rect.x = hit.rect.x - self.rect.width + self.right_indent

    def die_block_collision(self):
        # получаем пересекаемые объекты и перебираем каждый отдельно
        hits = pygame.sprite.spritecollide(self, self.die_blocks_group, False)
        for hit in hits:
            # Если маски пересекаются
            if pygame.sprite.collide_mask(self, hit):
                self.rect.x = self.pos[0]
                self.rect.y = self.pos[1]

    def draw(self, screen, camera): # Отрисовка игрока с учётом смещения камеры.
        # Корректируем координаты игрока относительно камеры
        offset_x = self.rect.x - camera.x
        offset_y = self.rect.y - camera.y

        # Отрисовываем игрока на экране
        screen.blit(self.image, (offset_x, offset_y))

    def update(self):
        # Применяем гравитацию
        self.fall_speed += self.gravity * 60 / fps

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Обновляем позицию по оси Y
        self.rect.y += self.fall_speed * FACTOR_Y * 60 / fps

        # обновляем координаты по Y координате (препятствия над и под)
        hits = pygame.sprite.spritecollide(self, self.all_group, False)
        for hit in hits:
            if pygame.sprite.collide_mask(self, hit):
                if self.rect.y - hit.rect.y < hit.rect.y - self.rect.y:
                    self.rect.y -= abs(self.rect.y + self.rect.height - hit.rect.y) - round(FACTOR_Y + 1) * 1
                    self.fall_speed = 0
                    self.is_ground = True
                    break
                elif self.rect.y - hit.rect.y > hit.rect.y - self.rect.y:
                    self.rect.y = hit.rect.y + hit.rect.height - self.top_indent
                    self.fall_speed = 0
                    break
        else:
            self.is_ground = False

        # Проверяем возможность выполнения рывка
        current_time = pygame.time.get_ticks()
        if not self.can_dash and (current_time - self.last_dash_time >= self.dash_cooldown):
            self.can_dash = True  # Разрешаем выполнение рывка снова

        # Рывок
        if self.dash_start_time is not None:
            self.is_dashing = True
            elapsed_time = current_time - self.dash_start_time

            if elapsed_time < self.dash_duration:
                progress = elapsed_time / self.dash_duration
                new_x = int(self.start_pos + (self.end_pos - self.start_pos) * progress)
                self.rect.x = new_x
            else:
                # Завершаем рывок после истечения времени
                self.rect.x = self.end_pos
                self.dash_start_time = None  # Сбрасываем время начала рывка
                self.is_dashing = False

                # Сбрасываем кадры анимации для рывка
                if self.direction == "right":
                    self.set_animation("dash_right")
                else:
                    self.set_animation("dash_left")

        # Если игрок стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
        if self.is_dashing:
            if self.direction == "right":
                self.current_animation = self.animations["dash_right"]
            else:
                self.current_animation = self.animations["dash_left"]

        elif (not self.is_ground and self.is_moving) or not self.is_ground:
            if self.direction == "right":
                self.current_animation = self.animations["jump_right"]
            else:
                self.current_animation = self.animations["jump_left"]
        elif not self.is_moving:
            if self.direction == "right":
                self.current_animation = self.animations["idle_right"]
            else:
                self.current_animation = self.animations["idle_left"]

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Проверяем на столкновение с die блоками
        self.die_block_collision()

        self.is_moving = False

        # Обновляем текущую анимацию
        self.current_animation.update()
        self.image = self.current_animation.get_frame()

        # Обновляем маску и хит-боксы
        self.mask = pygame.mask.from_surface(self.image)
        self.left_indent = min(self.mask.outline(), key=lambda x: x[0])[0]
        self.right_indent = self.rect.width - max(self.mask.outline(), key=lambda x: x[0])[0] - 1
        self.top_indent = min(self.mask.outline(), key=lambda x: x[1])[1]
