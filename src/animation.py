from utils import *


class Animation:
    def __init__(self, folder_path, frame_rate, flip_horizontal=False):
        self.frames = load_animation(folder_path)
        self.frame_rate = frame_rate
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        # Отзеркаливаем анимацию
        if flip_horizontal:
            self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_frame(self):
        return self.frames[self.current_frame]
