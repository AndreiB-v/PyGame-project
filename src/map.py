import pygame
import pytmx
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        if self.image is not None:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = None

class Map:
    def __init__(self, screen, map_name):
        self.screen = screen
        self.tmx_data = load_pygame(f'../data/maps/location_one/{map_name}.tmx')
        self.all_sprites = pygame.sprite.Group()
        self.platforms_group = pygame.sprite.Group()
        self.die_block_group = pygame.sprite.Group()
        self.create_tile_sprites()
        self.player_start_position = self.get_player_start_position()

    def create_tile_sprites(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    tile_x = x * self.tmx_data.tilewidth
                    tile_y = y * self.tmx_data.tileheight
                    tile = Tile(image, tile_x, tile_y)
                    if 'platforms' in layer.name.lower():
                        self.platforms_group.add(tile)
                    elif 'dieBlocks' in layer.name.lower():
                        self.die_block_group.add(tile)
                    self.all_sprites.add(tile)

    def get_player_start_position(self):
        for obj in self.tmx_data.objects:
            if obj.name == 'player':
                return (obj.x, obj.y)
        return None

    def get_groups(self):
        return self.all_sprites, self.platforms_group, self.die_block_group

    def render(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    self.screen.blit(image, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))