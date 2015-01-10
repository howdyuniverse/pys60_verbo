# -*- coding: utf-8 -*-

# http://pys60.garage.maemo.org/doc/s60/node37.html

import appuifw
import e32
import graphics
import key_codes
import codecs


class Draw(object):

    RGB_BLACK = (0, 0, 0)
    RGB_WHITE = (255, 255, 255)
    RGB_RED = (237, 28, 36)
    FONT = ('normal', 28)

    def __init__(self):
        self.old_screen = appuifw.app.screen
        appuifw.app.orientation = "landscape"
        self.canvas = None
        self.img = None
        self.canvas = appuifw.Canvas(redraw_callback=self.redraw)
        # init graphics
        self.screen_width = self.canvas.size[0]
        self.screen_height = self.canvas.size[1]
        self.focus_x = self.screen_width / 3.
        self.focus_y = self.screen_height / 2.
        self.img = graphics.Image.new(self.canvas.size)
        #
        self.old_body = appuifw.app.body
        appuifw.app.body = self.canvas

    def redraw(self, aRect=(0, 0, 0, 0)):
        if not self.canvas:
            return
        if self.img:
            self.canvas.blit(self.img)

    def draw_background(self):
        # top line
        self.img.line((self.focus_x,
                      0,
                      self.focus_x,
                      self.focus_y-30),
                      3)
        # buttom line
        self.img.line((self.focus_x,
                      self.screen_height,
                      self.focus_x,
                      self.focus_y+10),
                      3)

    def draw_str(self, text, color, x, y):
        self.img.text((x, y), text, fill=color, font=Draw.FONT)

    def text_width(self, text):
        return self.canvas.measure_text(text, Draw.FONT)[0][2]


class Verbo(Draw):

    punct_marks = (",", ".", "-", ":")

    def __init__(self, book_path):
        self.old_body = appuifw.app.body
        self.old_menu = appuifw.app.menu
        appuifw.app.exit_key_handler = self.quit_prog
        appuifw.app.menu = [
            (u"Start", self.resume_reader),
            (u"Exit", self.quit_prog)
            ]
        Draw.__init__(self)

        self.exit_flag = False
        self.pause = False

        self.book_path = book_path
        # index of last word
        self.last_word = 0

        self.word_delay = 0.5
        self.punct_delay = self.word_delay * 2
        self.words = []

        self.timer = e32.Ao_timer()
        self.app_lock = e32.Ao_lock()
        self.app_lock.wait()

    def quit_prog(self):
        self.exit_flag = True
        appuifw.app.body = self.old_body
        self.canvas = None
        self.app_lock.signal()
        appuifw.app.menu = self.old_menu
        appuifw.app.orientation = "portrait"
        appuifw.app.exit_key_handler = None

    def pause_reader(self):
        self.pause = True
        self.canvas.bind(key_codes.EScancode5, self.resume_reader)
        # enable rewind when pause
        self.canvas.bind(key_codes.EScancode6, self.prev_word)
        self.canvas.bind(key_codes.EScancode4, self.next_word)

    def prev_word(self):
        self.last_word -= 1
        self.display_word(self.words[self.last_word])

    def next_word(self):
        self.last_word += 1
        self.display_word(self.words[self.last_word])

    def resume_reader(self):
        self.pause = False
        self.canvas.bind(key_codes.EScancode5, self.pause_reader)
        # disable rewind when reading
        self.canvas.bind(key_codes.EScancode6, lambda: None)
        self.canvas.bind(key_codes.EScancode4, lambda: None)
        self.start_reading()

    def best_letter_pos(self, word):
        """ Primitive algorithm for defining focus letter """
        word_len = len(word)
        best_letter = 0

        if word_len == 1:
            best_letter = 0
        elif word_len >= 2 and word_len <= 5:
            best_letter = 1
        elif word_len >= 6 and word_len <= 9:
            best_letter = 2
        elif word_len >= 10 and word_len <= 13:
            best_letter = 3
        else:
            best_letter = 4

        return best_letter

    def get_part1(self, word, focus):
        if focus == 0:
            pt1 = 0
            pt1_width = 0
        else:
            pt1 = word[:focus]
            pt1_width = self.text_width(pt1)

        return pt1, pt1_width

    def get_part2(self, word, focus):
        pt2 = word[focus]
        pt2_w = self.text_width(pt2)

        return pt2, pt2_w

    def get_part3(self, word, focus):
        if focus == len(word)-1:
            pt3 = 0
        else:
            pt3 = word[focus+1:]

        return pt3

    def draw_word(self, word, focus_letter):
        """
            Draw one word. Separate word by prefix,
            middle marked letter and last part.
        """
        self.img.clear(Draw.RGB_WHITE)
        self.draw_background()

        if len(word) == 0:
            self.redraw()
            return

        part1, part1_w = self.get_part1(word, focus_letter)
        part2, part2_w = self.get_part2(word, focus_letter)
        # half width
        part2_hw = part2_w / 2.
        part3 = self.get_part3(word, focus_letter)

        # draw all parts
        if part1_w > 0:
            self.draw_str(part1,
                          Draw.RGB_BLACK,
                          self.focus_x - part1_w - part2_hw,
                          self.focus_y)

        self.draw_str(part2,
                      Draw.RGB_RED,
                      self.focus_x - part2_hw,
                      self.focus_y)

        if part3:
            self.draw_str(part3,
                          Draw.RGB_BLACK,
                          self.focus_x + part2_hw,
                          self.focus_y)

        self.redraw()

    def display_word(self, word):
        best_letter = self.best_letter_pos(word)
        self.draw_word(word, best_letter)

    def parse_words(self):
        """ Parse words from book into self.word.
            Now support only txt format.
        """
        book_file = codecs.open(self.book_path, "r", "utf-8")
        for line in book_file:
            for w in line.split():
                self.words.append(w)

        book_file.close()

    def check_punct(self, word):
        if word[-1] in self.punct_marks:
            return True
        return False

    def start_reading(self):
        # parse all words from book into self.words
        self.parse_words()
        offset = self.last_word

        for wnum, word in enumerate(self.words[self.last_word:]):
            # when user press pause or exit from reader
            if self.pause or self.exit_flag:
                self.last_word = offset + wnum
                self.pause = False
                break

            self.display_word(word)

            if self.check_punct(word):
                e32.ao_sleep(self.punct_delay)
            else:
                e32.ao_sleep(self.word_delay)


if __name__ == "__main__":
    book_path = "E:\\bbc_azimov.txt"
    # book_path = "E:\\alphabet.txt"

    Verbo(book_path).start_reading()
