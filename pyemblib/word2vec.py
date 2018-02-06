import codecs
import array
import sys
import numpy as np
from .common import *

def read(fname, mode=Mode.Binary, size_only=False):
    '''Returns array of words and word embedding matrix
    '''
    if mode == Mode.Text: output = _readTxt(fname, size_only=size_only)
    elif mode == Mode.Binary: output = _readBin(fname, size_only=size_only)
    return output

def _readTxt(fname, size_only=False):
    '''Returns array of words and word embedding matrix
    '''
    words, vectors = [], []
    hook = codecs.open(fname, 'r', 'utf-8')

    # get summary info about vectors file
    (numWords, dim) = (int(s.strip()) for s in hook.readline().split())
    if size_only:
        return (numWords, dim)

    for line in hook:
        chunks = line.split()
        word, vector = chunks[0].strip(), np.array([float(n) for n in chunks[1:]])
        words.append(word)
        vectors.append(vector)
    hook.close()

    assert len(words) == numWords
    for v in vectors: assert len(v) == dim

    return (words, vectors)

def _getFileSize(inf):
    curIx = inf.tell()
    inf.seek(0, 2)  # jump to end of file
    file_size = inf.tell()
    inf.seek(curIx)
    return file_size

def _readBin(fname, size_only=False):
    import sys
    words, vectors = [], []

    inf = open(fname, 'rb')

    # get summary info about vectors file
    summary = inf.readline().decode('utf-8')
    summary_chunks = [int(s.strip()) for s in summary.split(' ')]
    (numWords, dim) = summary_chunks[:2]
    if len(summary_chunks) > 2: float_size = 8
    else: float_size = 4

    if size_only:
        return (numWords, dim)

    # make best guess about byte size of floats in file
    #float_size = 4

    chunksize = 10*float_size*1024
    curIx, nextChunk = inf.tell(), inf.read(chunksize)
    #while len(nextChunk) > 0 and len(words) < numWords:
    while len(nextChunk) > 0:
        inf.seek(curIx)

        splitix = nextChunk.index(b' ')
        #print('splitIx: %d   nextChunk: %s' % (splitix, nextChunk[:splitix]))
        word = inf.read(splitix).decode('utf-8')
        #word = inf.read(splitix).decode('utf-8', errors='replace')
        #print('word: %s' % word)
        inf.seek(1,1) # skip the space
        vector = array.array('f', inf.read(dim*float_size))
        #print(vector)
        inf.seek(1,1) # skip the newline

        words.append(word)
        vectors.append(vector)
        curIx, nextChunk = inf.tell(), inf.read(chunksize)
        #print('curIx: %d' % curIx)
        #input()
        #sys.stdout.write('  >> Read %d words\r' % len(words))

    inf.close()

    # verify that we read properly
    assert len(words) == numWords
    return (words, vectors)

def write(embeds, fname, mode=Mode.Binary, verbose=False):
    '''Writes a dictionary of embeddings { term : embed }
    to a file, in the format specified.
    '''
    if mode == Mode.Binary:
        outf = open(fname, 'wb')
        write_str = lambda s: outf.write(s.encode('utf-8'))
    elif mode == Mode.Text:
        outf = codecs.open(fname, 'w', 'utf-8')
        write_str = lambda s: outf.write(s)

    wordmap = embeds

    # write summary info
    keys = list(wordmap.keys())
    vdim = 0 if len(keys) == 0 else len(wordmap.get(keys[0]))
    write_str('%d %d\n' % (len(keys), vdim))

    if verbose:
        sys.stdout.write(' >>> Writing %d-d embeddings for %d words\n' % (vdim, len(keys)))
        sys.stdout.flush()

    # write vectors
    i = 0
    for word in keys:
        write_str(word)
        embedding = wordmap.get(word)
        if mode == Mode.Binary:
            outf.write(b' ')
            # write as 4-byte float 32
            if 'astype' in dir(embedding): embedding.astype('f').tofile(outf)
            else: np.float32(embedding).tofile(outf)
        elif mode == Mode.Text:
            for f in embedding: write_str(' %.8f' % f)
        write_str('\n')
        if verbose: 
            if i % 50 == 0: sys.stdout.write('\r >>> Written %d/%d words' % (i,len(keys)))
            if i % 200 == 0: sys.stdout.flush()
        i += 1
    outf.close()

    if verbose:
        sys.stdout.write('\r >>> Written %d/%d words\n' % (i, len(keys)))
        sys.stdout.flush()