'''
Script for converting a binary word2vec file to text format
'''

from . import read
from . import word2vec
from .common import *

if __name__ == '__main__':
    
    def _cli():
        import optparse
        parser = optparse.OptionParser(usage='Usage: %prog EMBEDF OUTPUTF',
                description='Reads binary word2vec-format embeddings in BINF and writes them as text to TXTF')
        parser.add_option('--from', dest='from_format',
            type='choice', choices=list(CLI_Formats.options()), default=CLI_Formats.default(),
            help='current format of EMBEDF')
        parser.add_option('--to', dest='to_format',
            type='choice', choices=list(CLI_Formats.options()), default=CLI_Formats.default(),
            help='desired output format of OUTPUTF')
        addCLIReplaceErrors(parser)
        addCLISkipParsingErrors(parser)
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.print_help()
            exit()
        return args[0], args[1], options.from_format, options.to_format, options
    srcf, destf, from_format, to_format, options = _cli()

    print('== Embedding format conversion ==')
    print('  Input %s format file: %s' % (from_format, srcf))
    print('  Output %s format file: %s' % (to_format, destf))
    print('  Replacing Unicode decode errors: %s' % str(options.replace_errors))
    print('  Skipping parsing errors: %s' % str(options.skip_parsing_errors))

    from_fmt, from_mode = CLI_Formats.parse(from_format)
    to_fmt, to_mode = CLI_Formats.parse(to_format)

    errors = parseCLIReplaceErrors(options)

    print('\nReading %s input...' % from_format)
    embeddings = read(srcf, format=from_fmt, mode=from_mode, errors=errors, skip_parsing_errors=options.skip_parsing_errors)

    print('Writing %s output...' % to_format)
    if to_fmt == Format.Word2Vec:
        word2vec.write(embeddings, destf, mode=to_mode, verbose=True)
