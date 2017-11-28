'''
Print the dimensionality of an embedding file to stdout
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
        return args[0]
    embf = _cli()
    sys.stdout.write('%d\n' % read(embf, size_only=True))
