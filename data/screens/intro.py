# Это файл, в котором будем хранить начало игры
# Конец игры и результаты будут в этой же папке screens
# Надпись "погибли" или что-либо такое
# В общем-то,тоже чисто для структурирования кода


import pygame


class Intro: # Пропиши в этом классе заставку, которую ты сделал
    def __init__(self, screen):
        self.draw_intro(screen)

    def draw_intro(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 50)
        text = font.render("Hello, Pygame!", True, (100, 255, 100))
        text_x = 450 // 2 - text.get_width() // 2
        text_y = 450 // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)
