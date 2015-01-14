from xml.parsers import expat


class XMLParser:

    def __init__(self):
        self.parser = expat.ParserCreate()
        # handlers
        self.parser.CharacterDataHandler = self.handle_char
        self.parser.StartElementHandler = self.handle_start
        self.parser.EndElementHandler = self.handle_end

    def handle_char(self, data):
        pass

    def handle_start(self, name, attrs):
        pass
    
    def handle_end(self, name):
        pass


class FB2Parser(XMLParser):

    def __init__(self, book_path):
        self.book_path = book_path
        XMLParser.__init__(self)

    def parse_words(self):
        self.words = []
        book_file = open(self.book_path)
        book_txt = book_file.read()
        book_file.close()

        self.parser.Parse(book_txt)

        return self.words

    def handle_char(self, data):
        self.append_words(data)

    def append_words(self, string):
        for word in string.split():
            self.words.append(word)
