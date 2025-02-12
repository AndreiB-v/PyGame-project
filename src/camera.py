import pygame

import utils as ut


class Camera:
    def __init__(self):
        self.preview_rect = pygame.rect.Rect(0, 0, ut.width, ut.height)

    def update(self, target):
        # Камера следит за игроком
        self.preview_rect.center = target.rect.center

    def draw_group(self, group, screen):
        for sprite in group:
            offset_x = sprite.rect.x - self.preview_rect.x
            offset_y = sprite.rect.y - self.preview_rect.y
            screen.blit(sprite.image, (offset_x, offset_y))

    def x(self):
        return self.preview_rect.x

    def y(self):
        return self.preview_rect.y
