import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos, *args):
        super().__init__(group)

        # Группы спрайтов, с которыми взаимодействует игрок
        self.all_group = args[0]

        # Прописываем физические параметры
        self.gravity = 0.6
        self.acceleration = 0.5

        # Прописываем параметры игрока
        self.posx, self.posy = pos
        self.fall_speed = 0
        self.jump_strength = -15
        self.is_ground = False
        self.direction = "right"

        # Создаём спрайт игрока
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, 30, 40))
        self.rect = self.image.get_rect(topleft=(self.posx, self.posy))


    def move(self, direction):
        # Движение игрока
        if direction == "right":
            self.rect.x += 7
        elif direction == "left":
            self.rect.x -= 7

    def dash(self, direction):
        if direction == "right":
            self.rect.x += 17
        elif direction == "left":
            self.rect.x -= 17

    def jump(self):
        if self.is_ground:
            self.fall_speed = self.jump_strength
            self.is_ground = False

    def update(self):
        # Применяем гравитацию
        self.fall_speed += self.gravity

        # Обновляем позицию по оси Y
        if not self.is_ground:
            self.rect.y += self.fall_speed

            hits = pygame.sprite.spritecollide(self, self.all_group, False)  # Проверка столкновений
            if hits:
                self.fall_speed = 0
                self.is_ground = True


class Platform(pygame.sprite.Sprite):
    def __init__(self, posx, posy, all_sprites):
        super().__init__(all_sprites)
        self.image = pygame.Surface((700, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color("gray"), (0, 0, 700, 10))
        self.rect = self.image.get_rect(topleft=(posx, posy))


def main():
    pygame.init()
    size = width, height = 700, 700
    pygame.display.set_caption("Корабли ходят по небу")
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    player_pos = (50, 100)

    # Создаём группы
    player_group = pygame.sprite.Group()
    all_group = pygame.sprite.Group()

    player = Player(player_group, player_pos, all_group)
    Platform(0, 300, all_group)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Проверака зажатия wasd или стрелочек
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.direction = "right"
            player.move("right")
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.direction = "left"
            player.move("left")
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.jump()
        if keys[pygame.K_LCTRL]: # Рывок
            player.dash(player.direction)

        # Отрисовываем
        screen.fill((0, 0, 0))
        player_group.draw(screen)
        player.update()
        all_group.draw(screen)

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
