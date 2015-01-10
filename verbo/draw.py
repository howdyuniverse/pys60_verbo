import appuifw
import graphics

class Draw(object):

    RGB_BLACK = (0, 0, 0)
    RGB_WHITE = (255, 255, 255)
    RGB_RED = (237, 28, 36)
    WORD_FONT = ("normal", 28)
    INFO_FONT = ("normal", 16)

    def __init__(self):
        self.canvas = None
        self.img = None
        self.canvas = appuifw.Canvas(redraw_callback=self.redraw)
        self.img = graphics.Image.new(self.canvas.size)

        self.screen_width = self.canvas.size[0]
        self.screen_height = self.canvas.size[1]
        self.focus_x = self.screen_width / 3.
        self.focus_y = self.screen_height / 2.

    def clear(self):
        self.img.clear(Draw.RGB_WHITE)

    def redraw(self, rect=(0, 0, 0, 0)):
        if not self.canvas:
            return
        if self.img:
            self.canvas.blit(self.img)

    def background(self):
        # top line
        self.img.line((self.focus_x,
                      0,
                      self.focus_x,
                      self.focus_y-30),
                      width=1,
                      outline=Draw.RGB_BLACK)
        # buttom line
        self.img.line((self.focus_x,
                      self.screen_height,
                      self.focus_x,
                      self.focus_y+10),
                      width=1,
                      outline=Draw.RGB_BLACK)

    def text(self, text, color, x, y, font):
        self.img.text((x, y),
                        text,
                        fill=color,
                        font=font)

    def text_width(self, text):
        return self.canvas.measure_text(text, Draw.WORD_FONT)[0][2]

    def get_prefix(self, word, focus):
        if focus == 0:
            pt1 = 0
            pt1_width = 0
        else:
            pt1 = word[:focus]
            pt1_width = self.text_width(pt1)

        return pt1, pt1_width

    def get_focus_letter(self, word, focus):
        pt2 = word[focus]
        pt2_w = self.text_width(pt2)

        return pt2, pt2_w

    def get_postfix(self, word, focus):
        if focus == len(word)-1:
            pt3 = 0
        else:
            pt3 = word[focus+1:]

        return pt3

    def word(self, word, focus_letter):
        """
            Draw one word. Separate word by prefix,
            middle marked letter and last part.
        """
        self.background()

        prefix, prefix_w = self.get_prefix(word, focus_letter)
        fletter, fletter_w = self.get_focus_letter(word, focus_letter)
        # half width
        fletter_hw = fletter_w / 2.
        postfix = self.get_postfix(word, focus_letter)

        # draw all parts
        if prefix_w > 0:
            self.text(prefix,
                      Draw.RGB_BLACK,
                      self.focus_x - prefix_w - fletter_hw,
                      self.focus_y,
                      Draw.WORD_FONT)

        self.text(fletter,
                  Draw.RGB_RED,
                  self.focus_x - fletter_hw,
                  self.focus_y,
                  Draw.WORD_FONT)

        if postfix:
            self.text(postfix,
                      Draw.RGB_BLACK,
                      self.focus_x + fletter_hw,
                      self.focus_y,
                      Draw.WORD_FONT)

        self.redraw()

    def info(self, wpm):
        self.text(u"%swpm" % wpm,
                  Draw.RGB_BLACK,
                  10, 20,
                  Draw.INFO_FONT)
