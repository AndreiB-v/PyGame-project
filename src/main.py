import pygame
from pygame.gfxdraw import rectangle

from utils import load_image
from animation import Animation
from intro import *


class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos, *args):
        super().__init__(group)

        self.all_group = args[0]

        # Прописываем физические параметры
        self.gravity = 0.6
        self.acceleration = 0.5

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
            self.rect.x += 5 * factor_x
            self.set_animation("move_right")

        elif direction == "left":
            self.rect.x -= 5 * factor_x
            self.set_animation("move_left")

        self.is_moving = True

    def dash(self, direction):
        current_time = pygame.time.get_ticks()

        if self.can_dash and (current_time - self.last_dash_time >= self.dash_cooldown):
            # Запоминаем начальную и конечную позиции для плавного движения
            self.start_pos = self.rect.x
            if direction == "right":
                self.set_animation("dash_right")
                self.end_pos = self.start_pos + self.dash_speed * factor_x
            elif direction == "left":
                self.end_pos = self.start_pos - self.dash_speed * factor_x
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
                if abs(self.rect.y + self.rect.height - hit.rect.y) < 3:
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
        self.fall_speed += self.gravity

        # Проверяем на столкновения со стенками
        self.wall_collision()

        # Обновляем позицию по оси Y
        self.rect.y += self.fall_speed * factor_y

        # обновляем координаты по Y координате (препятствия над и под)
        hits = pygame.sprite.spritecollide(self, self.all_group, False)
        for hit in hits:
            if pygame.sprite.collide_mask(self, hit):
                if self.rect.y - hit.rect.y < hit.rect.y - self.rect.y:
                    self.rect.y -= abs(self.rect.y + self.rect.height - hit.rect.y)
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


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height, group):
        super().__init__(group)
        self.image = pygame.Surface((width * factor_x, height * factor_y), pygame.SRCALPHA)
        self.image.fill(pygame.Color("white"))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * factor_x
        self.rect.y = pos_y * factor_y


class Game:
    def __init__(self):
        pygame.init()
        self.size = width, height
        pygame.display.set_caption("Корабли ходят по небу")
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        player_pos = (50 * factor_x, 100 * factor_y)

        # Создаём группы
        self.player_group = pygame.sprite.Group()
        self.all_group = pygame.sprite.Group()

        self.player = Player(self.player_group, player_pos, self.all_group)
        Platform(0, 300, 401, 1000, self.all_group)
        Platform(400, 700, 400, 1000, self.all_group)
        Platform(600, 500, 700, 100, self.all_group)
        Platform(798, 300, 700, 1000, self.all_group)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Проверка зажатия WASD или стрелочек
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.direction = "right"
                self.player.move("right")
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.direction = "left"
                self.player.move("left")
            if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
                self.player.jump()
            if keys[pygame.K_LCTRL]:  # Рывок
                self.player.dash(self.player.direction)

            # Отрисовываем
            self.screen.fill((0, 0, 0))
            self.player_group.draw(self.screen)
            self.player.update()
            self.all_group.draw(self.screen)

            self.clock.tick(60)
            pygame.display.flip()

        pygame.quit()


# screen_log = start_screen()
# while screen_log not in ('run_game', 'close'):
#     screen_log = screen_log()
# if screen_log == 'close':
#     pygame.quit()

if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()
