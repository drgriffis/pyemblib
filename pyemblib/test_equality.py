'''
Script to check if two embedding files contain the same embeddings,
modulo a (runtime-configurable) floating point tolerance
'''

import numpy as np
from . import read
from . import word2vec
from .common import *

if __name__ == '__main__':
    
    def _cli():
        import optparse
        parser = optparse.OptionParser(usage='Usage: %prog EMBEDF1 EMBEDF2',
                description='Reads embeddings from EMBEDF1 and EMBEDF2 and compares them for equality')
        parser.add_option('--format-1', dest='format_1',
            type='choice', choices=list(CLI_Formats.options()), default=CLI_Formats.default(),
            help='format of EMBEDF1')
        parser.add_option('--format-2', dest='format_2',
            type='choice', choices=list(CLI_Formats.options()), default=CLI_Formats.default(),
            help='format of EMBEDF2')
        parser.add_option('-t', '--tolerance', dest='tolerance',
            type='float', default=0.002,
            help='tolerance +/- to account for floating point deviation (default %default)')
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.print_help()
            exit()
        return args, options
    (emb1f, emb2f), options = _cli()

    print('== Testing embedding equality ==')
    print('  Input %s file 1: %s' % (options.format_1, emb1f))
    print('  Input %s file 2: %s' % (options.format_2, emb2f))
    print('  Error tolerance: %f' % options.tolerance)

    fmt1, mode1 = CLI_Formats.parse(options.format_1)
    fmt2, mode2 = CLI_Formats.parse(options.format_2)

    print('\nReading input #1 (%s)...' % options.format_1)
    embeddings_1 = read(emb1f, format=fmt1, mode=mode1)

    print('\nReading input #2 (%s)...' % options.format_2)
    embeddings_2 = read(emb2f, format=fmt2, mode=mode2)

    print('\nChecking equality...')

    keys1 = set(embeddings_1.keys())
    keys2 = set(embeddings_2.keys())
    if len(keys1 - keys2) > 0 or len(keys2 - keys1) > 0:
        print('  FAILED!\n  Keys do not match between files.')
    else:
        valid = True
        for k in keys1:
            v1, v2 = embeddings_1[k], embeddings_2[k]
            diff = v1 - v2
            for val in diff:
                if np.abs(val) > options.tolerance:
                    valid = False
                    break
            if not valid:
                break
        if not valid:
            print('  FAILED!\n  Vector difference in key "%s".' % k)
        else:
            print('  PASSED!')
