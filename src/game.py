# Файлик для работы с приложением


import pygame
from data.screens.intro import Intro


class Application:
    def __init__(self):
        pygame.init()
        self.size = width, height = 500, 500
        pygame.display.set_caption("Корабли ходят по небу")
        self.screen = pygame.display.set_mode(self.size)

        self.fps = 60
        self.clock = pygame.time.Clock()

        self.intro = Intro(self.screen)  # Инициализируем здесь интро, в ивентах прописать начало самой игры

        self.running = True
        self.run()

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.intro.draw_intro(self.screen) # Здесь можно вызывать функцию draw для движения кораблей

            self.clock.tick(self.fps)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    app = Application()