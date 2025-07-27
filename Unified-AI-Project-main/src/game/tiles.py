import pygame
import random

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100

class Tile:
    def __init__(self, x, y, tile_type='grass'):
        self.x = x
        self.y = y
        self.tile_type = tile_type # 'grass', 'tilled', 'planted', 'rock'
        self.crop = None
        self.growth_stage = 0
        self.rock = None
        if self.tile_type == 'rock':
            self.rock = Rock(x, y)

class TileMap:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        self.tiles = [[Tile(x, y, 'rock' if random.random() < 0.1 else 'grass') for y in range(height)] for x in range(width)]

    def render(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                # For now, just draw a colored square for each tile type
                color = (0, 255, 0) # Green for grass
                if self.tiles[x][y].tile_type == 'tilled':
                    color = (139, 69, 19) # Brown for tilled
                elif self.tiles[x][y].tile_type == 'planted':
                    color = (0, 100, 0) # Dark green for planted
                elif self.tiles[x][y].tile_type == 'rock':
                    color = (128, 128, 128) # Grey for rock
                pygame.draw.rect(surface, color, (x * 32, y * 32, 32, 32))
