from .packages.pygments import lexers, util
import logging

MAX_FILE_SIZE = 2 << 20
logger = logging.getLogger("TimeWalk")

class TimeWalkLexer:
    def __init__(self, args):
        self.args = args
        if args.language is not None:
            try:
                self._lexer = lexers.get_lexer_by_name(args.language.lower())
            except util.ClassNotFound:
                self._lexer = guess_lexer(args.file)
        else:
            self._lexer = guess_lexer(args.file)
        if self._lexer:
            logger.info("Lexer found, lang {}".format(self._lexer.name))
        else:
            logger.warning("No lexer found")

    def get_tokens(self):
        if self._lexer is None:
            return None
        with open(self.args.file) as f:
            text = f.read()
            return self._lexer.get_tokens_unprocessed(text) if self._lexer else []

    def get_language(self):
        return self._lexer.name if self._lexer else "Text"

def guess_lexer(filename):
    with open(filename) as f:
        text = f.read(256000)
        try:
            lexer = lexers.guess_lexer_for_filename(filename, text)
        except util.ClassNotFound:
            lexer = None
        return lexer
