import pygame as pg
import src.objects as obj
import src.utils as ut
import src.interaction_bd as bd
from src.camera import Camera

save_id = None
last_scene = None


# Основной цикл игры
def game():
    global last_scene
    last_scene = game
    end_game = None

    # Инициализируем группы (удаляем все объекты, чтобы не рисовать прошлые сцены
    ut.initialization()

    def save_return(value):
        bd.location_save(save_id, groups['creatures_group'], dialogs, return_current_location())
        pg.mixer.music.stop()
        return value

    # Карта: сон
    @ut.create_connect
    def change_location(location, cur=None):
        cur.execute(f'UPDATE saves SET current_location = ? WHERE id = ?', (location, save_id))

    # возвращает текущую локацию (dream или city)
    @ut.create_connect
    def return_current_location(cur=None):
        return cur.execute('SELECT current_location FROM saves WHERE id = ?', (save_id,)).fetchone()[0]

    # проверяет, инициализирован ли сон в сохранении и создает его, если нет
    @ut.create_connect
    def check_dream(player, cur=None):
        if not cur.execute(f'SELECT dream FROM saves WHERE id = ?', (save_id,)).fetchone()[0]:
            bd.create_dream_save(player, save_id)

    # обновляет состояние double_jump (на True)
    @ut.create_connect
    def update_double_jump(cur=None):
        cur.execute('UPDATE saves SET double_jump = 1 WHERE id = ?', (save_id,))

    def init_save():
        nonlocal end_game
        location = return_current_location()
        if location == 'dream':
            end_game = obj.EndGame(1940, 1956, save_id)
            return bd.get_dream_save(save_id)
        else:
            pg.mixer.music.load("../data/sounds/rain_sound.mp3")
            pg.mixer.music.play(-1)
            pg.mixer.music.set_volume(ut.settings['SOUNDS VOLUME'] * 0.01)
            return bd.get_city_save(save_id)

    groups, dialogs, player, skeletons, rain = init_save()
    next_lvl = obj.NextLevel(3103, 1541)

    # ______________ ДИАЛОГИ __________________ #
    screen2 = pg.Surface(ut.screen.get_size(), pg.SRCALPHA)
    screen3 = pg.Surface(ut.screen.get_size(), pg.SRCALPHA)
    screen3.set_alpha(10)
    degree = 0  # анимация (Е)
    activ_dial_x = activ_dial_y = 0  # положение анимации (Е)
    push = False  # зажата ли (Е)
    e_image = ut.load_image('images/e.png', 'CUSTOM_SIZE', factors=(0.58, 0.58))
    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

    # Для обработки нажатия прыжка по новой механики (она вводится, что бы работал двойной прыжок)
    jump_pressed_last_frame = False

    # Создаём камеру, паузу, конец игры
    camera = Camera()
    pause = obj.Pause()

    while True:
        if end_game is not None:
            if pg.sprite.collide_mask(player, end_game):
                end_game.set_active(ut.screen)
                end_game_log = ut.render_popup(end_game)
                if end_game_log in 'start_screen':
                    return save_return(start_screen)
                elif end_game_log == 'quit':
                    return save_return('close')
        if pg.sprite.collide_mask(player, next_lvl):
            bd.location_save(save_id, groups['creatures_group'], dialogs, return_current_location())
            pg.mixer.music.stop()

            check_dream(player)
            change_location('dream')
            return game

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return save_return('close')
            if event.type == pg.KEYDOWN:
                if event.key == 101:
                    screen2 = pg.Surface(ut.screen.get_size())
                    screen2.set_colorkey((0, 0, 0))
                    if player.direction == 'right':
                        activ_dial_x, activ_dial_y = (player.rect.x + player.rect.width - camera.x(),
                                                      player.rect.y - camera.y())
                    else:
                        activ_dial_x, activ_dial_y = player.rect.x - camera.x(), player.rect.y - camera.y()
                    degree = 0
                    push = True
                if event.key == 27:
                    pause.set_active(ut.screen)
                    pg.mixer.music.pause()
                    pause_log = ut.render_popup(pause)
                    if pause_log in ('select_save', 'settings'):
                        return save_return({'select_save': select_save, 'settings': settings}[pause_log])
                    elif pause_log == 'quit':
                        return save_return('close')
                    pg.mixer.music.unpause()
            if event.type == pg.KEYUP:
                if event.key == 101:
                    push = False

        # Проверка зажатия WASD или стрелочек
        keys = pg.key.get_pressed()
        jump_pressed_now = keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            player.direction = "right"
            player.move("right")
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            player.direction = "left"
            player.move("left")
        if jump_pressed_now and not jump_pressed_last_frame:
            player.jump()
        if keys[pg.K_LCTRL]:  # Рывок
            player.dash(player.direction)
        if keys[pg.K_x]:
            player.attack1()

        # Обновляем переменную для следующего кадра:
        jump_pressed_last_frame = jump_pressed_now

        # Очистка экрана
        ut.screen.fill((50, 131, 218))

        # Обновление всех существ
        # creatures_group.update(creatures_group)
        for sprite in groups['creatures_group']:
            sprite.update(groups['creatures_group'])
        if skeletons:
            for skeleton in skeletons:
                skeleton.check_trigger_radius(player)

        # Обновление камеры
        camera.update(player)

        # Рисуем все группы спрайтов с учётом камеры
        for group in groups.values():
            camera.draw_group(group, ut.screen)
        camera.draw_group(ut.top_layer, ut.screen)

        # Если дождь был создан, то рисуем его
        if rain:
            for drop in rain:
                drop.update()
                drop.draw()

        # ______________ ДИАЛОГИ __________________ #
        cur_dialog = None
        for item_dialog in dialogs:
            if player.rect.colliderect(item_dialog.x - item_dialog.radius + player.left_indent,
                                       item_dialog.y - item_dialog.radius,
                                       item_dialog.radius * 2 - player.left_indent - player.right_indent,
                                       item_dialog.radius * 2):
                cur_dialog = item_dialog

        if cur_dialog and push:
            for i in range(10):
                degree += 1 * 60 / ut.fps
                pg.draw.circle(screen2, pg.Color('white'), radius=2,
                               center=ut.return_dot(degree, 30, activ_dial_x, activ_dial_y))
            if degree > 400 and push:
                ut.sounds['dialog_activation'].play()
                push = False
                cur_dialog.set_active(ut.screen)
            ut.screen.blit(screen2, (0, 0))
            e_image.set_alpha(255)
            ut.screen.blit(e_image, (activ_dial_x - e_image.get_rect().width / 2,
                                     activ_dial_y - e_image.get_rect().height / 2))
        elif cur_dialog:
            e_image.set_alpha(100)
            ut.screen.blit(e_image, (cur_dialog.x - e_image.get_rect().width / 2 - camera.x(),
                                     cur_dialog.y - e_image.get_rect().height / 2 - camera.y()))
        if cur_dialog:
            screen3.fill((0, 0, 0))
            pg.draw.rect(screen3, pg.Color('white'), (cur_dialog.x - cur_dialog.radius - camera.x(),
                                                      cur_dialog.y - cur_dialog.radius - camera.y(),
                                                      cur_dialog.radius * 2,
                                                      cur_dialog.radius * 2))
            ut.screen.blit(screen3, (0, 0))
        if cur_dialog and cur_dialog.active:
            answer = ut.render_popup(cur_dialog)
            if answer == 'quit':
                return save_return('close')
            else:
                dialogs.remove(cur_dialog)
                cur_dialog = None
            if answer == "куда ты так поздно?" or answer == "и куда ты?":
                dialogs.append(obj.Dialog('сам же знаешь. на работу',
                                          3128 - 300, 1512, 100,
                                          'опять переработки?', 'как много работы'))
            if answer == "опять переработки?" or answer == "как много работы":
                dialogs.append(obj.Dialog('ну, а что поделать? ладно, я побежала, обязательно поешь!',
                                          3128 - 300, 1512, 100,
                                          'хорошо, пока', 'окей, увидимся'))
            if answer == "где я?":
                dialogs.append(obj.Dialog('м? серьёзно? по твоему кислому лицу и в правду видно, '
                                          'что ты не понимаешь, где ты..', 557, 1138, 20, '"молчание"'))
            if answer == '"молчание"':
                dialogs.append(obj.Dialog('ну что ж.. поздравляю, ты попал в сказочный мир снов, '
                                          'в нём может происходить всё, что угодно, ведь на то он и сказочный!',
                                          557, 1138, 20,
                                          'ты знаешь, как отсюда можно выбраться?'))
            if answer == 'ты знаешь, как отсюда можно выбраться?':
                dialogs.append(obj.Dialog('нет, если честно, но за помощь со скелетом я могу немного тебе помочь! '
                                          'возьми это', 557, 1138, 20, 'получить двойной прыжок'))
            if answer == 'получить двойной прыжок':
                player.plot_double_jump = True
                update_double_jump()
                dialogs.append(obj.Dialog(' здесь трудно без таких умений, поэтому рада, что дала тебе его. '
                                          'с помощью этого навыка ты сможешь свободно передвигаться по миру '
                                          'и я надеюсь, что ты найдёшь выход домой!',
                                          557, 1138, 20, 'спасибо'))
        # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ДИАЛОГИ ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ #

        pg.display.flip()
        ut.clock.tick(ut.fps)

    # Экран 'приветствия', главная менюшка


def start_screen():
    global last_scene
    last_scene = start_screen

    ut.initialization()

    bg = obj.Background(ut.load_image('menu UI/Background.png', 'MENU'), 670, 0, ut.bottom_layer)
    fg = obj.Background(ut.load_image('menu UI/Foreground.png', 'MENU'), 0, 0, ut.top_layer)

    ship1 = obj.Ship(1, ut.width, ut.height, ut.mid_layer)
    cloud1 = obj.Cloud(1)
    mountain = obj.Mountain()
    ship2 = obj.Ship(-1, ut.width, ut.height, ut.mid_layer)
    cloud2 = obj.Cloud(-1)
    play_button = obj.Button(32, 528, select_save, ut.load_image('buttons/Play.png', 'MENU'),
                             (ut.all_sprites, ut.button_layer))
    settings_button = obj.Button(33, 788, settings,
                                 ut.load_image('buttons/Settings.png', 'MENU'),
                                 (ut.all_sprites, ut.button_layer))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                ut.button_layer.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                for func in [play_button.update(event.pos, 'up'),
                             settings_button.update(event.pos, 'up')]:
                    if func:
                        return func

        ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)

        pg.display.flip()
        ut.clock.tick(ut.fps)


# Экран выбора сохранения
@ut.create_connect
def select_save(cur=None):
    ut.initialization()

    saves = cur.execute('SELECT id FROM saves').fetchall()
    save_count = len(saves)

    buttons = []
    plus_button = None

    for save in saves:
        buttons.append(obj.Button(381, 160 + 151 * (saves.index(save)), save[0],
                                  ut.load_image(f'buttons/saves/Save {saves.index(save) + 1}.png', 'MENU'),
                                  (ut.all_sprites, ut.button_layer)))
    buttons.append(obj.Button(350, 0, start_screen, ut.load_image('buttons/BookmarkHome.png', 'MENU'),
                              (ut.all_sprites, ut.button_layer)))

    def plus():
        nonlocal save_count, cur
        cur.execute('INSERT INTO saves(current_location) VALUES("city")')  # создаем новое сохранение
        save_id = cur.execute('SELECT MAX(Id) FROM saves').fetchone()[0]

        save_count += 1
        bd.create_city_save(save_id, cur)

        buttons.append(obj.Button(381, 160 + 151 * (save_count - 1), save_id,
                                  ut.load_image(f'buttons/saves/Save {save_count}.png', 'MENU'),
                                  (ut.all_sprites, ut.button_layer)))
        if save_count == 5:
            plus_button.kill()

    if save_count < 5:
        plus_button = obj.Button(549, 834, plus, ut.load_image('buttons/Plus.png', 'MENU'),
                                 (ut.all_sprites, ut.button_layer))

    bg = obj.Background(ut.load_image('select UI/Background.png', 'MENU'), 0, 0, ut.bottom_layer)
    art1 = obj.Art(ut.load_image('select UI/Cloud 1.png', 'MENU'), 1038, 102)
    art2 = obj.Art(ut.load_image('select UI/Cloud 2.png', 'MENU'), 1168, 245)
    art3 = obj.Art(ut.load_image('select UI/Island 1.png', 'MENU'), 1360, 560)
    art4 = obj.Art(ut.load_image('select UI/Island 2.png', 'MENU'), 1020, 460)

    MYEVENTTYPE = pg.USEREVENT + 1
    pg.time.set_timer(MYEVENTTYPE, 50)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                ut.button_layer.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                for func in [button.update(event.pos, 'up') for button in buttons]:
                    if func == start_screen:
                        return start_screen
                    elif func.__class__.__name__ == 'int':
                        global save_id
                        save_id = func
                        return game
                if plus_button is not None:
                    func = plus_button.update(event.pos, 'up')
                    if func:
                        func()
            if event.type == MYEVENTTYPE:
                ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)

        pg.display.flip()
        ut.clock.tick(ut.fps)

    # Экран настроек


def settings():
    ut.initialization()

    obj.Background(ut.load_image('settings UI/Background.png', 'MENU'), 0, 0, ut.bottom_layer)  # Задний фон
    obj.Gearwheel()
    buttons = [obj.Button(350, 0, last_scene, ut.load_image('buttons/BookmarkHome.png' if last_scene == start_screen
                                                            else 'buttons/BookmarkBack.png', 'MENU'), ut.button_layer),
               obj.Checkbox(745, 685, 'APP BAR', ut.button_layer, settings)]

    slider_push = False
    sliders = [
        # слайдер фпс
        obj.Slider(350, 300, 60, 'FPS', text={'x': 613, 'y': 195, 'center': False, 'size': 80}),
        # слайдер громкости
        obj.Slider(350, 445, 100, 'SOUNDS VOLUME', text={'x': 673, 'y': 350, 'center': False, 'size': 80}),
        # слайдер размера экрана
        obj.Slider(350, 594, 80, 'SIZE FACTOR', text={'x': 600, 'y': 635, 'center': True, 'size': 50})
    ]

    MYEVENTTYPE = pg.USEREVENT + 1
    pg.time.set_timer(MYEVENTTYPE, 100)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'close'
            if event.type == pg.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.update(event.pos, 'down')
                slider_push = any([slider.update(event.pos, 'down') for slider in sliders])
            if event.type == pg.MOUSEBUTTONUP:
                slider_push = False
                if any([slider.save_changes() for slider in sliders]):
                    ut.update_settings()
                    return settings
                for func in [button.update(event.pos, 'up') for button in buttons]:
                    if func == last_scene:
                        return last_scene
                    if func == settings:
                        return settings
            if event.type == pg.MOUSEMOTION:
                if slider_push:
                    for slider in sliders:
                        slider.update(event.rel, 'move', pos2=event.pos)
            if event.type == MYEVENTTYPE:
                ut.mid_layer.update()

        ut.screen.fill((0, 0, 0))
        ut.bottom_layer.draw(ut.screen)
        ut.mid_layer.draw(ut.screen)
        ut.top_layer.draw(ut.screen)
        ut.button_layer.draw(ut.screen)
        for slider in sliders:
            slider.draw_text()

        pg.display.flip()
        ut.clock.tick(ut.fps)
