from random import randint

import pygame

from src.animation import Animation
from src.objects import Event, Health
from src.utils import fps, top_layer, all_sprites, FACTOR_Y, HEIGHT, WIDTH


class Creature(pygame.sprite.Sprite):
    def __init__(self, group, pos, platforms_group, deadly_layer, hp, hp_factor):
        super().__init__(group)
        self.groups = group
        self.move_factor = 5  # фактор сдвига по пикселям

        self.hp = hp
        self.hp_factor = hp_factor

        self.health = Health(hp, 15, hp_factor)

        self.platforms_group = platforms_group
        self.deadly_layer = deadly_layer

        self.is_die = False

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
        if not self.is_die:
            self.direction = direction
            if direction == "right":
                self.rect.x += self.move_factor * 60 / fps * 0.58  # * FACTOR_X
                self.set_animation("move_right")

            elif direction == "left":
                self.rect.x -= self.move_factor * 60 / fps * 0.58  # * FACTOR_X
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
                    self.rect.x = hit.rect.x + hit.rect.width - self.left_indent
                elif min(left_side, right_side, top_side) == right_side:
                    self.rect.x = hit.rect.x - self.rect.width + self.right_indent

    def die_block_collision(self):
        # получаем пересекаемые объекты и перебираем каждый отдельно
        hits = pygame.sprite.spritecollide(self, self.deadly_layer, False)
        for hit in hits:
            # Если маски пересекаются
            if pygame.sprite.collide_mask(self, hit):
                self.get_damage(0.5)

    def get_damage(self, n, direction=None):
        self.health -= n
        if direction == 'right':
            self.rect.x += 10
        elif direction == 'left':
            self.rect.x -= 10
        if not self.health:
            self.die()

    def die(self):
        if not self.is_die:
            self.is_die = True
            self.set_animation(f'die_{self.direction}')

    def make_die(self):
        if self.is_die:
            if self.current_animation.current_frame == len(self.current_animation) - 1 or not self.is_ground:
                self.health.kill()
                self.__init__(self.groups, self.pos, self.platforms_group, self.deadly_layer, self.hp, self.hp_factor)

    # Если существо стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
    def passive_animation(self):
        if not self.is_moving:
            self.current_animation = self.animations[f"idle_{self.direction}"]

    def update(self, *args):
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
                    self.rect.y -= abs(self.rect.y + self.rect.height - hit.rect.y) - 2  # round(FACTOR_Y + 1) * 1
                    self.fall_speed = 0
                    self.is_ground = True
                    break
                elif self.rect.y - hit.rect.y > hit.rect.y - self.rect.y:
                    self.rect.y = hit.rect.y + hit.rect.height - self.top_indent
                    self.fall_speed = 0
                    break
        else:
            self.is_ground = False

        self.make_die()

        # Класс игрока, перенесено из main


class Player(Creature):
    def __init__(self, group, pos, platforms_group, deadly_layer, hp=10, hp_factor=0.2):
        super().__init__(group, pos, platforms_group, deadly_layer, hp, hp_factor)

        # Параметры для рывка
        self.can_dash = True
        self.start_pos = None
        self.end_pos = None
        self.dash_speed = 150  # Смещение при рывке

        self.dash_event = Event(200, 500)
        self.attack1_event = Event(400, 1000)

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
                                                  flip_horizontal=True),
                           "attack1_right": Animation("attack-1", 'character', frame_rate=100),
                           "attack1_left": Animation("attack-1", 'character', frame_rate=100,
                                                     flip_horizontal=True),
                           "die_right": Animation('die', 'character', frame_rate=100),
                           "die_left": Animation('die', 'character', frame_rate=100,
                                                 flip_horizontal=True)}
        self.current_animation = self.animations["idle_right"]

        # Создаём спрайт игрока
        self.image = self.current_animation.get_frame()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos

        # Создаем отступы от маски, именно они образуют хит-бокс
        self.update_hitboxes()

    def dash(self, direction):
        if self.can_dash:
            if self.dash_event.time_check():
                # Запоминаем начальную и конечную позиции для плавного движения
                self.start_pos = self.rect.x
                if direction == "right":
                    self.set_animation("dash_right")
                    self.end_pos = self.start_pos + self.dash_speed * 0.58  # * FACTOR_X
                elif direction == "left":
                    self.end_pos = self.start_pos - self.dash_speed * 0.58  # * FACTOR_X
                    self.set_animation("dash_left")

                self.dash_event.activation()

    def attack1(self):
        if self.attack1_event.time_check():
            self.set_animation(f'attack1_{self.direction}')
            self.attack1_event.activation()

    def make_attack1(self, all_creatures):
        current_time = pygame.time.get_ticks()
        if self.attack1_event.start_time is not None and not self.is_die:
            self.attack1_event.is_active = True
            elapsed_time = current_time - self.attack1_event.start_time

            if self.current_animation.current_frame == 2:
                attack_radius = pygame.rect.Rect(0, 0, 50, 37)
                attack_radius.center = self.rect.center
                for sprite in all_creatures:
                    if sprite != self:
                        if sprite.rect.colliderect(attack_radius):
                            sprite.get_damage(0.5, self.direction)

            if not elapsed_time < self.attack1_event.duration:
                self.attack1_event.start_time = None  # Сбрасываем время начала атаки
                self.attack1_event.is_active = False

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
        if self.dash_event.start_time is not None and not self.is_die:
            self.dash_event.is_active = True
            elapsed_time = current_time - self.dash_event.start_time

            if elapsed_time < self.dash_event.duration:
                progress = elapsed_time / self.dash_event.duration
                new_x = int(self.start_pos + (self.end_pos - self.start_pos) * progress)
                self.rect.x = new_x
            else:
                # Завершаем рывок после истечения времени
                self.rect.x = self.end_pos
                self.dash_event.start_time = None  # Сбрасываем время начала рывка
                self.dash_event.is_active = False

    def update(self, all_creatures):
        super().update()

        self.make_attack1(all_creatures)

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

        self.health.synchron_pos(self, WIDTH * 0.49 - self.health.rect.width // 2, - HEIGHT * 0.45)

        # Обновляем маску и хит-боксы
        if self.current_animation not in (self.animations[f"attack1_{self.direction}"],
                                          self.animations[f"attack1_{self.direction}"]):
            self.update_hitboxes()

    def passive_animation(self):
        if self.is_die:
            self.current_animation = self.animations[f"die_{self.direction}"]
        elif self.dash_event.is_active:
            self.current_animation = self.animations[f"dash_{self.direction}"]
        elif self.attack1_event.is_active:
            self.current_animation = self.animations[f"attack1_{self.direction}"]
        elif (not self.is_ground and self.is_moving) or not self.is_ground:
            self.current_animation = self.animations[f"jump_{self.direction}"]
        else:
            Creature.passive_animation(self)

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
                    self.dash_event.is_active = False
                    self.dash_event.start_time = None

                    self.rect.x = hit.rect.x + hit.rect.width - self.left_indent
                elif min(left_side, right_side, top_side) == right_side:
                    self.dash_event.is_active = False
                    self.dash_event.start_time = None

                    self.rect.x = hit.rect.x - self.rect.width + self.right_indent


class Enemy(Creature):
    def __init__(self, group, pos, platforms_group, deadly_layer, hp=10, hp_factor=0.1):
        super().__init__(group, pos, platforms_group, deadly_layer, hp, hp_factor)

        self.trigger_radius = pygame.rect.Rect(0, 0, 400, 400)
        self.fight_radius = pygame.rect.Rect(0, 0, 150, 150)
        self.vector = 0
        self.move_factor = 3

        self.attack_event = Event(1000, 1000)
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
                                                    flip_horizontal=True),
                           "die_right": Animation('die', 'sceleton', frame_rate=100),
                           "die_left": Animation('die', 'sceleton', frame_rate=100,
                                                 flip_horizontal=True)}
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
            diff_right = target.rect.x - self.trigger_radius.center[0]
            diff_left = target.rect.x + target.rect.width - self.trigger_radius.center[0]
            if abs(diff_left) - abs(diff_right) > 50:
                self.direction = 'left'
                self.vector = diff_left / abs(diff_left)
                return
            elif abs(diff_right) - abs(diff_left) > 50:
                self.direction = 'right'
                self.vector = diff_right / abs(diff_right)
                return

        if target.rect.colliderect(self.fight_radius):
            self.attack()
        self.vector = 0

    def attack(self):
        if randint(0, 50) == 1:
            if self.attack_event.time_check():
                self.set_animation(f"attack_{self.direction}")
                self.current_attack = 'sword strike'
                self.attack_event.activation()

    def make_attack(self, all_creatures):
        current_time = pygame.time.get_ticks()
        if self.attack_event.start_time is not None and not self.is_die:

            self.attack_event.is_active = True
            elapsed_time = current_time - self.attack_event.start_time

            if self.current_animation.current_frame == 7:
                attack_radius = pygame.rect.Rect(0, 0, 50, 37)
                attack_radius.center = self.rect.center
                for sprite in all_creatures:
                    if sprite != self:
                        if sprite.rect.colliderect(attack_radius):
                            sprite.get_damage(0.5, self.direction)

            if not elapsed_time < self.attack_event.duration:
                self.attack_event.start_time = None  # Сбрасываем время начала атаки
                self.attack_event.is_active = False

    def passive_animation(self):
        if self.is_die:
            self.current_animation = self.animations[f"die_{self.direction}"]
        elif self.attack_event.is_active:
            self.current_animation = self.animations[f"attack_{self.direction}"]
        else:
            super().passive_animation()

    def update(self, all_creatures):
        if self.vector != 0:
            self.move({1: 'right', -1: 'left'}[self.vector])

        super().update()

        # Если игрок стоит, то меняем анимацию на анимацию стояния бездействия, или на анимацию прыжка
        self.passive_animation()

        self.make_attack(all_creatures)

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Проверяем на столкновение с die блоками
        self.die_block_collision()

        self.is_moving = False

        # Обновляем текущую анимацию
        self.current_animation.update()
        self.image = self.current_animation.get_frame()

        self.health.synchron_pos(self, 0, -35)

        # Обновляем маску и хит-боксы
        self.update_hitboxes()
