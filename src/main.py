from scenes import *

if __name__ == "__main__":
    screen_log = start_screen()
    while screen_log != 'close':
        screen_log = screen_log()
    if screen_log == 'close':
        pygame.quit()
