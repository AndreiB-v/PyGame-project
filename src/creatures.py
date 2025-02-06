from random import randint

import pygame

from src.animation import Animation
from src.objects import Event
from src.utils import FACTOR_X, fps, FACTOR_Y


class Creature(pygame.sprite.Sprite):
    def __init__(self, group, pos, platforms_group, deadly_layer):
        super().__init__(group)
        self.move_factor = 5  # фактор сдвига по пикселям

        self.platforms_group = platforms_group
        self.deadly_layer = deadly_layer

        # Прописываем физические параметры
        self.gravity = 0.6

        # Параметры существа
        self.is_moving = False
        self.fall_speed = 0
        self.jump_strength = -12.5
        self.is_ground = False
        self.pos = pos
        self.direction = "right"  # Куда смотрит существо

        # image и animation прописывать отдельно (см. Player)

    def set_animation(self, animation_name):
        if self.current_animation != self.animations[animation_name]:
            self.current_animation = self.animations[animation_name]
            self.current_animation.current_frame = 0
        elif animation_name == "idle":
            self.current_animation.current_frame = 0

    def move(self, direction):
        if direction == "right":
            self.rect.x += self.move_factor * FACTOR_X * 60 / fps
            self.set_animation("move_right")

        elif direction == "left":
            self.rect.x -= self.move_factor * FACTOR_X * 60 / fps
            self.set_animation("move_left")

        self.is_moving = True

    def update_hitboxes(self):
        self.mask = pygame.mask.from_surface(self.image)
        self.left_indent = min(self.mask.outline(), key=lambda x: x[0])[0]
        self.right_indent = self.rect.width - max(self.mask.outline(), key=lambda x: x[0])[0] - 1
        self.top_indent = min(self.mask.outline(), key=lambda x: x[1])[1]

    def wall_collision(self):
        # получаем пересекаемые объекты и перебираем каждый отдельно
        hits = pygame.sprite.spritecollide(self, self.platforms_group, False)
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
                    self.dash_event.start_time = None

                    self.rect.x = hit.rect.x + hit.rect.width - self.left_indent
                elif min(left_side, right_side, top_side) == right_side:
                    self.is_dashing = False
                    self.dash_event.start_time = None

                    self.rect.x = hit.rect.x - self.rect.width + self.right_indent

    def die_block_collision(self):
        # получаем пересекаемые объекты и перебираем каждый отдельно
        hits = pygame.sprite.spritecollide(self, self.deadly_layer, False)
        for hit in hits:
            # Если маски пересекаются
            if pygame.sprite.collide_mask(self, hit):
                self.rect.x = self.pos[0]
                self.rect.y = self.pos[1]

    # Если существо стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
    def passive_animation(self):
        if not self.is_moving:
            if self.direction == "right":
                self.current_animation = self.animations["idle_right"]
            else:
                self.current_animation = self.animations["idle_left"]

    def update(self):
        # Применяем гравитацию
        self.fall_speed += self.gravity * 60 / fps

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Обновляем позицию по оси Y
        self.rect.y += self.fall_speed * 60 / fps * 0.58  # * FACTOR_Y

        # обновляем координаты по Y координате (препятствия над и под)
        hits = pygame.sprite.spritecollide(self, self.platforms_group, False)
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


# Класс игрока, перенесено из main
class Player(Creature):
    def __init__(self, group, pos, platforms_group, deadly_layer):
        super().__init__(group, pos, platforms_group, deadly_layer)

        # Параметры для рывка
        self.can_dash = True
        self.dash_cooldown = 500  # Время ожидания между рывками в миллисекундах
        self.last_dash_time = 0
        self.is_dashing = False

        self.dash_duration = 200  # Длительность рывка в миллисекундах
        self.dash_start_time = None
        self.start_pos = None
        self.end_pos = None
        self.dash_speed = 150  # Смещение при рывке

        self.dash_event = Event(200, 500)

        # Группы анимаций принадлежащих игроку
        self.animations = {"move_right": Animation("walk", 'character', frame_rate=200),
                           "move_left": Animation("walk", 'character', frame_rate=200,
                                                  flip_horizontal=True),
                           "idle_right": Animation("idle", 'character', frame_rate=200),
                           "idle_left": Animation("idle", 'character', frame_rate=200,
                                                  flip_horizontal=True),
                           "jump_right": Animation("jump", 'character', frame_rate=180),
                           "jump_left": Animation("jump", 'character', frame_rate=180,
                                                  flip_horizontal=True),
                           "dash_right": Animation("dash", 'character', frame_rate=180),
                           "dash_left": Animation("dash", 'character', frame_rate=180,
                                                  flip_horizontal=True)}
        self.current_animation = self.animations["idle_right"]

        # Создаём спрайт игрока
        self.image = self.current_animation.get_frame()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos

        # Создаем отступы от маски, именно они образуют хит-бокс
        self.update_hitboxes()

    def dash(self, direction):
        current_time = pygame.time.get_ticks()

        if self.can_dash:
            if self.dash_event.time_check():
                # Запоминаем начальную и конечную позиции для плавного движения
                self.start_pos = self.rect.x
                if direction == "right":
                    self.set_animation("dash_right")
                    self.end_pos = self.start_pos + self.dash_speed * FACTOR_X
                elif direction == "left":
                    self.end_pos = self.start_pos - self.dash_speed * FACTOR_X
                    self.set_animation("dash_left")

                self.dash_event.start_time = current_time
                self.dash_event.last_activation = current_time
                self.can_dash = False

    def jump(self):
        self.rect.y += 1
        if self.is_ground:
            hits_after = pygame.sprite.spritecollide(self, self.platforms_group, False)
            for hit in hits_after:
                if pygame.sprite.collide_mask(self, hit):
                    if abs(self.rect.y + self.rect.height - hit.rect.y) <= 3:
                        # if self.rect.y + self.rect.height - round(FACTOR_Y + 1) * 1 - 1 == hit.rect.y:
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

    def make_dash(self):
        # Проверяем возможность выполнения рывка
        current_time = pygame.time.get_ticks()
        if not self.can_dash and self.dash_event.time_check():
            self.can_dash = True  # Разрешаем выполнение рывка снова

        # Рывок
        if self.dash_event.start_time is not None:
            self.is_dashing = True
            elapsed_time = current_time - self.dash_event.start_time

            if elapsed_time < self.dash_event.duration:
                progress = elapsed_time / self.dash_event.duration
                new_x = int(self.start_pos + (self.end_pos - self.start_pos) * progress)
                self.rect.x = new_x
            else:
                # Завершаем рывок после истечения времени
                self.rect.x = self.end_pos
                self.dash_event.start_time = None  # Сбрасываем время начала рывка
                self.is_dashing = False

                # Сбрасываем кадры анимации для рывка
                if self.direction == "right":
                    self.set_animation("dash_right")
                else:
                    self.set_animation("dash_left")

    def update(self):
        super().update()

        # Если игрок стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
        self.passive_animation()

        self.make_dash()

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Проверяем на столкновение с die блоками
        self.die_block_collision()

        self.is_moving = False

        # Обновляем текущую анимацию
        self.current_animation.update()
        self.image = self.current_animation.get_frame()

        # Обновляем маску и хит-боксы
        self.update_hitboxes()

    def passive_animation(self):
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
        else:
            Creature.passive_animation(self)


class Enemy(Creature):
    def __init__(self, group, pos, platforms_group, deadly_layer):
        super().__init__(group, pos, platforms_group, deadly_layer)

        self.trigger_radius = pygame.rect.Rect(0, 0, 400, 400)
        self.fight_radius = pygame.rect.Rect(0, 0, 100, 100)
        self.vector = 0
        self.move_factor = 3

        self.current_attack = None

        # Группы анимаций принадлежащих игроку
        self.animations = {"move_right": Animation("walk", 'sceleton', frame_rate=100),
                           "move_left": Animation("walk", 'sceleton', frame_rate=100,
                                                  flip_horizontal=True),
                           "idle_right": Animation("idle", 'sceleton', frame_rate=200),
                           "idle_left": Animation("idle", 'sceleton', frame_rate=200,
                                                  flip_horizontal=True),
                           "attack_right": Animation('attack', 'sceleton', frame_rate=100),
                           "attack_left": Animation('attack', 'sceleton', frame_rate=100,
                                                    flip_horizontal=False)}
        self.current_animation = self.animations["idle_right"]

        # Создаём спрайт игрока
        self.image = self.current_animation.get_frame()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos

        # Создаем отступы от маски, именно они образуют хит-бокс
        self.update_hitboxes()

    def check_trigger_radius(self, target):
        self.trigger_radius.center = self.rect.center
        self.fight_radius.center = self.rect.center
        if target.rect.colliderect(self.trigger_radius):
            diff = target.rect.center[0] - self.trigger_radius.center[0]
            if abs(diff) > 1:
                self.vector = diff / abs(diff)
                return
        if target.rect.colliderect(self.fight_radius):
            self.attack()
        self.vector = 0

    def attack(self):
        if randint(0, 1000) == 10 and not self.current_attack:
            self.set_animation(f"attack_{self.direction}")
            self.current_attack = 'sword strike'

    # def make_attack(self, attack):
    #     if attack == 'sword strike':

    def update(self):
        if self.vector != 0:
            self.move({1: 'right', -1: 'left'}[self.vector])

        super().update()

        # Если игрок стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
        self.passive_animation()

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Проверяем на столкновение с die блоками
        self.die_block_collision()

        self.is_moving = False

        # Обновляем текущую анимацию
        self.current_animation.update()
        self.image = self.current_animation.get_frame()

        # Обновляем маску и хит-боксы
        self.update_hitboxes()
