import src.utils as ut
import pygame as pg


class Animation:
    def __init__(self, folder_path, creature, frame_rate, flip_horizontal=False):
        scale = {'character': (100 * 0.58, 87 * 0.58),
                 'skeleton': (100 * 0.58, 87 * 0.58),
                 'yumiko': (39, 53),
                 'mother': (12.258064516 * 2.2, 20 * 2.2)}[creature]
        self.frames = ut.load_animation(folder_path, creature, scale)
        self.frame_rate = frame_rate
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()

        # Отзеркаливаем анимацию
        if flip_horizontal:
            self.frames = [pg.transform.flip(frame, True, False) for frame in self.frames]

    def update(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_frame(self):
        return self.frames[self.current_frame]

    def __len__(self):
        return len(self.frames)
