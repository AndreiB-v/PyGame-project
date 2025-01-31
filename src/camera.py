import pygame

def update_camera(player_rect, camera_rect, world_width, world_height):
    # Камера следит за игроком
    camera_rect.center = player_rect.center


def draw_group_with_camera(group, screen, camera):
    for sprite in group:
        offset_x = sprite.rect.x - camera.x
        offset_y = sprite.rect.y - camera.y
        screen.blit(sprite.image, (offset_x, offset_y))