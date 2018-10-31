'''
Print the vocabulary of an embedding file to stdout, one word per line.
'''
import sys
from . import *

if __name__=='__main__':
    def _cli():
        import optparse
        parser = optparse.OptionParser(usage='Usage: %prog EMBF')
        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.print_help()
            exit()
        return args[0], options
    embf, options = _cli()
    vocab = readVocab(embf)
    for v in vocab:
        sys.stdout.write('%s\n' % v)
