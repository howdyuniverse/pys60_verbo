import key_codes
import appuifw
import codecs
import e32

from window import Dialog
from draw import Draw


class Reader(Dialog):

    PUNCT_MARKS = (",", ".", "-", ":")

    def __init__(self, cbk, book_title, book_path):
        menu = [(u"Start", self.reader_start),
                (u"Pause", self.reader_pause),
                (u"Close book", self.close_reader)]

        self.book_title = book_title
        self.book_path = book_path
        self.pause = False
        self.last_word = 0
        self.word_delay = 0.5
        self.punct_delay = self.word_delay * 2
        self.words = []
        self.parse_words()

        self.old_orientation = appuifw.app.orientation
        appuifw.app.orientation = "landscape"
        self.draw = Draw()

        Dialog.__init__(self,
                        cbk,
                        self.book_title,
                        self.draw.canvas,
                        menu,
                        self.close_reader)

    def parse_words(self):
        """ Parse words from book into self.word.
            Now support only txt format.
        """
        book_file = codecs.open(self.book_path, "r", "utf-8")
        for line in book_file:
            for w in line.split():
                self.words.append(w)

        book_file.close()

    def reader_start(self):
        self.pause = False
        self.draw.canvas.bind(key_codes.EScancode5, self.reader_pause)
        # disable rewind when reading
        self.draw.canvas.bind(key_codes.EScancode6, lambda: None)
        self.draw.canvas.bind(key_codes.EScancode4, lambda: None)
        self.start_reading()

    def reader_pause(self):
        self.pause = True
        self.draw.canvas.bind(key_codes.EScancode5, self.reader_start)
        # enable rewind when pause
        self.draw.canvas.bind(key_codes.EScancode6, self.prev_word)
        self.draw.canvas.bind(key_codes.EScancode4, self.next_word)

    def prev_word(self):
        self.last_word -= 1
        self.display_word(self.words[self.last_word])

    def next_word(self):
        self.last_word += 1
        self.display_word(self.words[self.last_word])

    def display_word(self, word):
        best_letter = self.best_letter_pos(word)
        self.draw.word(word, best_letter)

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

    def check_punct(self, word):
        if word[-1] in Reader.PUNCT_MARKS:
            return True
        return False

    def start_reading(self):
        offset = self.last_word

        for wnum, word in enumerate(self.words[self.last_word:]):
            # when user press pause or exit from reader
            if self.pause or self.cancel:
                self.last_word = offset + wnum
                self.pause = False
                break

            self.display_word(word)

            if self.check_punct(word):
                e32.ao_sleep(self.punct_delay)
            else:
                e32.ao_sleep(self.word_delay)

    def close_reader(self):
        appuifw.app.orientation = self.old_orientation
        self.cancel_app()
