from random import choice, randint, uniform

from src.animation import Animation
from utils import *


# Класс кнопки
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
    def __init__(self, vector):
        super().__init__(all_sprites, mid_layer)
        self.image = choice([load_image('menu UI/Ship 1.png', 'MENU'),
                             load_image('menu UI/Ship 2.png', 'MENU')])
        self.vector = vector
        self.rect = self.image.get_rect()
        self.move_factor = uniform(1, 3)
        if self.vector == -1:
            self.rect.x = WIDTH
            if self.image == load_image('menu UI/Ship 1.png', 'MENU'):
                self.image = pygame.transform.flip(self.image, True, False)
        if self.vector == 1:
            self.rect.x = 0
            if self.image == load_image('menu UI/Ship 2.png', 'MENU'):
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y = randint(0, HEIGHT - self.rect.height * 2)


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
        self.image.fill(pygame.Color("white"))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * FACTOR_X
        self.rect.y = pos_y * FACTOR_Y


# Класс игрока, перенесено из main
class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos, *args):
        super().__init__(group)

        self.all_group = args[0]

        # Прописываем физические параметры
        self.gravity = 0.6

        # Прописываем параметры игрока
        self.fall_speed = 0
        self.jump_strength = -15
        self.is_ground = False

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
                           "jump_right": Animation("jump", frame_rate=230),
                           "jump_left": Animation("jump", frame_rate=230, flip_horizontal=True),
                           "dash_right": Animation("dash", frame_rate=180),
                           "dash_left": Animation("dash", frame_rate=180, flip_horizontal=True)}
        self.current_animation = self.animations["idle_right"]

        # Создаём спрайт игрока
        self.image = self.current_animation.get_frame()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

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
        hits_after = pygame.sprite.spritecollide(self, self.all_group, False)
        for hit in hits_after:
            if pygame.sprite.collide_mask(self, hit):
                if self.rect.y + self.rect.height - round(FACTOR_Y + 1) * 1 - 1 == hit.rect.y:
                    self.fall_speed = self.jump_strength
                    self.is_ground = False

                    if self.direction == "right":
                        self.set_animation("jump_right")
                    else:
                        self.set_animation("jump_left")
                    break

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

        self.is_moving = False

        # Обновляем текущую анимацию
        self.current_animation.update()
        self.image = self.current_animation.get_frame()

        # Обновляем маску и хит-боксы
        self.mask = pygame.mask.from_surface(self.image)
        self.left_indent = min(self.mask.outline(), key=lambda x: x[0])[0]
        self.right_indent = self.rect.width - max(self.mask.outline(), key=lambda x: x[0])[0] - 1
        self.top_indent = min(self.mask.outline(), key=lambda x: x[1])[1]
