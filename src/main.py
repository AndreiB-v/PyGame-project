from scenes import *

if __name__ == "__main__":
    # Задаем 'логи экрана', то есть screen_log содержит функцию исполняемой сцены scenes
    screen_log = game()
    # Каждая функция из scenes возвращает функцию следующей сцены
    while screen_log != 'close':
        screen_log = screen_log()
    # Если нажат Alt + F4, то функция сцены возвращает 'close', после чего игра останавливается
    if screen_log == 'close':
        pygame.quit()
