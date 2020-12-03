import game
import pygame
import character.character as character
from utils import *

DIALOGUE_MAX_CHAR_LINES = 0
LEFT_X = 0

load: bool = False
DIALOGUE_BOX: pygame.Surface = None
RIGHT_ARROW: pygame.Surface = None
DOWN_ARROW: pygame.Surface = None
SELECT_TOP: pygame.Surface = None
SELECT_DOWN: pygame.Surface = None
SELECT_MID: pygame.Surface = None


def load_hud_item():
    global load, DIALOGUE_BOX, RIGHT_ARROW, DOWN_ARROW, SELECT_TOP, SELECT_DOWN, SELECT_MID, DIALOGUE_MAX_CHAR_LINES
    global LEFT_X
    if not load:
        load = True
        HUD = pygame.image.load("assets/textures/hud/HUD.png")
        DIALOGUE_BOX = character.get_part(HUD, (0, 25, 280, 78), (game.SURFACE_SIZE[0] * 0.9, game.SURFACE_SIZE[1] * 0.2))
        RIGHT_ARROW = character.get_part(HUD, (0, 0, 6, 10), (12, 20))
        DOWN_ARROW = character.get_part(HUD, (6, 0, 16, 6), (20, 12))
        SELECT_TOP = character.get_part(HUD, (0, 10, 74, 15), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.05))
        SELECT_DOWN = character.get_part(HUD, (0, 19, 74, 25), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.05))
        SELECT_MID = character.get_part(HUD, (74, 10, 149, 25), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.08))
        DIALOGUE_MAX_CHAR_LINES = int(game.SURFACE_SIZE[0] * 0.85) // game.FONT_SIZE_16[0]
        LEFT_X = int(game.SURFACE_SIZE[0] * 0.15)
        del HUD


class Dialog(object):

    def __init__(self, text, speed=50, speed_skip=False, timed=0, need_morph_text=False):
        """

        text => sting list with each lines or sting lang key with need_morph_text=True
        speed => nb of ms in each char show (-1 for instant)
        speed_skip => can skip lines with action click default False
        timed => none skip and auto closable after timed ms need only 2 text line or less and speed_skip = False
        :type timed: int
        :type speed_skip: bool
        :type speed: int
        """
        if speed_skip and timed != 0:
            raise ValueError("Can't create Dialogue box with speed_skip and timed !=0")
        if timed != 0 and len(text) > 2:
            raise ValueError("Can't create Dialogue with timed !=0 and len(text) > 2")
        if need_morph_text:
            t = game.game_instance.get_message(text)
            self.text = Dialog.split(t)

        else:
            self.text = text
        self.speed = speed
        self.start_render_line = -1
        self.current_line = 0
        self.show_line = 0
        self.timed = timed
        self.speed_skip = speed_skip
        self.need_enter = False
        self.mono_line = len(self.text) == 1
        self.display_arrow = timed == 0
        self.open_time = current_milli_time()
        self.is_end_line = False

    def render(self, display: pygame.Surface):
        display.blit(DIALOGUE_BOX, (int(game.SURFACE_SIZE[0] * 0.05), game.SURFACE_SIZE[1] * 0.75))
        t = current_milli_time()

        if 0 < self.timed < (t - self.start_render_line):
            game.game_instance.player.close_dialogue()
            return

        # print(self.current_line)
        if self.start_render_line == -1:
            self.start_render_line = t
        nb_char = (((t - self.start_render_line) // self.speed) + 1) if self.speed > 0 else (len(self.text[self.current_line]) + 1)
        if nb_char > len(self.text[self.current_line]) or self.is_end_line:
            if self.show_line == 0 and not self.mono_line:
                self.show_line = 1
                self.current_line += 1
                self.start_render_line = t
                nb_char = 1
            else:
                nb_char = len(self.text[self.current_line])
                if self.display_arrow:
                    display.blit(DOWN_ARROW, (game.SURFACE_SIZE[0] * 0.88, game.SURFACE_SIZE[1] * 0.88))
                self.need_enter = True
                self.is_end_line = True

        if self.show_line == 1:
            l = game.FONT_24.render(self.text[self.current_line - 1], True, (0, 0, 0))
            display.blit(l, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78)))

        l = self.text[self.current_line]
        current = game.FONT_24.render(l[0: nb_char], True, (0, 0, 0))
        display.blit(current, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78) + ((game.SURFACE_SIZE[1] * 0.2 / 3) * self.show_line)))

    def press_action(self):

        if self.need_enter or self.speed_skip or (self.timed > 0 and current_milli_time() - self.open_time > self.open_time):
            self.need_enter = False
            if self.mono_line or (self.current_line == (len(self.text) - 1)):
                if self.speed and not self.is_end_line:
                    self.is_end_line = True
                    return False
                else:
                    return True
            if self.show_line == 0 and not self.mono_line:
                self.show_line = 1
            self.current_line += 1
            self.start_render_line = current_milli_time()
        return False

    def pres_y(self, up):
        pass

    @staticmethod
    def split(text):
        split_text = text.split()
        split_line = []
        line = ""

        for i in split_text:
            if (len(line) + len(i)) > DIALOGUE_MAX_CHAR_LINES > len(i) or i == '[l]':
                split_line.append(line)
                line = ""
            if i != '[l]':
                line += i + " "
        if len(line) != 0:
            split_line.append(line)
        return split_line


class QuestionDialog(Dialog):

    def __init__(self, text, callback, ask, speed=50, speed_skip=False, timed=0, need_morph_text=False):
        """
        ask => dic [Show:value]
        :type ask: dict[str:object]
        """
        super().__init__(text, speed, speed_skip, timed, need_morph_text)
        if len(ask) < 2:
            raise ValueError("len of ask need be > 2")

        self.ask = ask
        self.select = 0
        self.callback = callback

    def render(self, display: pygame.Surface):
        super().render(display)
        if self.current_line == len(self.text) - 1 and self.need_enter:
            self.display_arrow = False
            nb_line = len(self.ask)
            draw_x = int(game.SURFACE_SIZE[0] * 0.75)
            draw_y = int(game.SURFACE_SIZE[1] * 0.68)
            display.blit(SELECT_DOWN, (draw_x, draw_y))
            for i in range(nb_line):
                draw_y -= game.SURFACE_SIZE[1] * 0.08
                display.blit(SELECT_MID, (draw_x, draw_y))

            draw_y -= game.SURFACE_SIZE[1] * 0.05
            display.blit(SELECT_TOP, (draw_x, draw_y))

            draw_y += game.SURFACE_SIZE[1] * 0.06
            draw_x += 35
            c = 0
            for key in self.ask:
                if c == self.select:
                    display.blit(RIGHT_ARROW, (draw_x - 18, draw_y + 3))
                font = game.FONT_24.render(key, True, (0, 0, 0))
                display.blit(font, (draw_x, draw_y))
                draw_y += game.SURFACE_SIZE[1] * 0.08
                c += 1

    def pres_y(self, up):
        if self.current_line == len(self.text) - 1 and self.need_enter:
            if up:
                self.select = self.select = max(self.select - 1, 0)
            else:
                self.select = min(self.select + 1, len(self.ask) - 1)

    def press_action(self):
        if self.current_line == len(self.text) - 1 and self.need_enter:
            return not self.callback(self.ask[self.select], self.select)
        else:
            return super().press_action()