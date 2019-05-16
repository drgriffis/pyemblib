import codecs
import array
import sys
import numpy as np
import time
from .common import *

def read(fname, mode=Mode.Binary, size_only=False, first_n=None, separator=' ',
        replace_errors=False, filter_to=None, lower_keys=False, errors='strict',
        skip_parsing_errors=False):
    '''Returns array of words and word embedding matrix

    Parameters
       fname               :: name of embedding file to read
       mode                :: pyemblib.Mode indicator (text or binary format)
       size_only           :: if True, only reads the size of the embeddings and stops
       first_n             :: only read the first n embeddings
       separator           :: character separating the key from the embedding vector
       filter_to           :: only return embeddings whose keys are in this list
       lower_keys          :: lowercase all keys before returning
       errors              :: flag passed to UTF-8 decoding
       skip_parsing_errors :: if True, prints a warning message when a line fails
                              to parse, but continues reading; default behavior
                              aborts on parsing error

    DEPRECATED PARAMETERS
       replace_errors :: if True, uses utf-8 decoding flag "replace"
    '''
    if mode == Mode.Text: output = _readTxt(fname, size_only=size_only,
        first_n=first_n, filter_to=filter_to, lower_keys=lower_keys,
        replace_errors=replace_errors, errors=errors, separator=separator,
        skip_parsing_errors=skip_parsing_errors)
    elif mode == Mode.Binary: output = _readBin(fname, size_only=size_only,
        first_n=first_n, separator=separator, replace_errors=replace_errors,
        filter_to=filter_to, lower_keys=lower_keys, errors=errors)
    return output

def _readTxt(fname, size_only=False, first_n=None, filter_to=None, lower_keys=False,
        replace_errors=False, errors='strict', separator=' ', skip_parsing_errors=False):
    '''Returns array of words and word embedding matrix
    '''
    words, vectors = [], []
    hook = open(fname, 'rb')

    if replace_errors:
        errors = 'replace'

    bsep = bytes(separator, 'utf-8')[0]

    if filter_to:
        if lower_keys:
            filter_set = set([f.lower() for f in filter_to])
            key_filter = lambda k: k.lower() in filter_set
        else:
            filter_set = set(filter_to)
            key_filter = lambda k: k in filter_set
    else:
        key_filter = lambda k: True

    # get summary info about vectors file
    (numWords, dim) = (int(s.strip()) for s in hook.readline().decode('utf-8', errors=errors).split())
    if size_only:
        return (numWords, dim)

    line_ix = 0
    for line in hook:
        line_ix += 1
        if len(line.strip()) > 0:
            try:
                ix = 0
                while line[ix] != bsep:
                    ix += 1
                key = line[:ix].decode('utf-8', errors=errors)
                vector = line[ix+1:].decode('utf-8', errors=errors)
                vector = np.array([float(n) for n in vector.split()])
            except Exception as e:
                if skip_parsing_errors:
                    sys.stderr.write('[WARNING] Line %d: Parsing error -- %s\n' % (line_ix, str(e)))
                    line_ix += 1
                    continue
                else:
                    print("<<< CHUNKING ERROR >>>")
                    print(line)
                    raise e

            #chunks = line.split()
            #try:
            #    key, vector = chunks[0].strip(), np.array([float(n) for n in chunks[1:]])
            if len(vector) == dim - 1 or len(key) == 0:
                sys.stderr.write("[WARNING] Line %d: Read vector without a key, skipping\n" % line_ix)
            elif len(vector) != dim:
                raise ValueError("Read %d-length vector, expected %d" % (len(vector), dim))
            else:
                if key_filter(key):
                    words.append(key)
                    vectors.append(vector)

                if (not first_n is None) and len(words) == first_n:
                    break
            line_ix += 1
    hook.close()

    if not first_n is None:
        assert len(words) == first_n
    elif not filter_to:
        if len(words) != numWords:
            sys.stderr.write("[WARNING] Expected %d words, read %d\n" % (numWords, len(words)))

    return (words, vectors)

def _getFileSize(inf):
    curIx = inf.tell()
    inf.seek(0, 2)  # jump to end of file
    file_size = inf.tell()
    inf.seek(curIx)
    return file_size

def _readBin(fname, size_only=False, first_n=None, separator=' ', replace_errors=False, filter_to=None, lower_keys=False, errors='strict'):
    import sys
    words, vectors = [], []

    if filter_to:
        if lower_keys:
            filter_set = set([f.lower() for f in filter_to])
            key_filter = lambda k: k.lower() in filter_set
        else:
            filter_set = set(filter_to)
            key_filter = lambda k: k in filter_set
    else:
        key_filter = lambda k: True

    inf = open(fname, 'rb')

    # get summary info about vectors file
    summary = inf.readline().decode('utf-8', errors=errors)
    summary_chunks = [int(s.strip()) for s in summary.split(' ')]
    (numWords, dim) = summary_chunks[:2]
    if len(summary_chunks) > 2: float_size = 8
    else: float_size = 4

    if size_only:
        return (numWords, dim)

    bsep = separator.encode('utf-8')

    for _ in range(numWords):
        word = []
        while True:
            next_ch = inf.read(1)
            if next_ch == b' ':
                break
            elif next_ch != b'\n':  # some files have \n separator and some do not
                word.append(next_ch)

        if replace_errors:
            word = b''.join(word).decode('utf-8', errors='replace')
        else:
            word = b''.join(word).decode('utf-8', errors=errors)
        vector = np.array(array.array('f', inf.read(dim*float_size)))

        if key_filter(word):
            words.append(word)
            vectors.append(vector)

        if (not first_n is None) and len(words) == first_n:
            break

    inf.close()

    # verify that we read properly
    if not first_n is None:
        assert len(words) == first_n
    elif not filter_to:
        if len(words) != numWords:
            sys.stderr.write("[WARNING] Expected %d words, read %d\n" % (numWords, len(words)))
    return (words, vectors)

def write(embeds, fname, mode=Mode.Binary, verbose=False):
    '''Writes a dictionary of embeddings { term : embed }
    to a file, in the format specified.
    '''
    if mode == Mode.Binary:
        outf = open(fname, 'wb')
    elif mode == Mode.Text:
        outf = codecs.open(fname, 'w', 'utf-8')

    wordmap = embeds

    # write summary info
    keys = list(wordmap.keys())
    vdim = 0 if len(keys) == 0 else len(wordmap.get(keys[0]))
    if mode == Mode.Binary:
        outf.write(('%d %d\n' % (len(keys), vdim)).encode('utf-8'))
    else:
        outf.write('%d %d\n' % (len(keys), vdim))

    if verbose:
        sys.stdout.write(' >>> Writing %d-d embeddings for %d words\n' % (vdim, len(keys)))
        sys.stdout.flush()

    # write vectors
    ctr = {'count':0}
    if verbose:
        def tick(ctr, complete=False):
            if not complete:
                ctr['count'] += 1
            if complete or ctr['count'] % 1000 == 0:
                sys.stdout.write('\r >>> Written %d/%d words' % (ctr['count'], len(keys)))
                if complete or (ctr['count'] % 5000 == 0):
                    sys.stdout.flush()
    else:
        def tick(ctr, complete=False):
            pass

    if mode == Mode.Binary:
        test_emb = wordmap.get(keys[0])
        if 'astype' in dir(test_emb): write_op = lambda e: e.astype('f').tostring()
        else: write_op = lambda e: np.float32(e).tostring()

        time_word, time_lookup, time_emb = 0, 0, 0
        for word in keys:
            embedding = wordmap.get(word)
            outf.write(word.encode('utf-8') + b' ' + write_op(embedding) + b'\n')
            tick(ctr, complete=False)

    elif mode == Mode.Text:
        for word in keys:
            embedding = wordmap.get(word)
            outf.write('%s %s\n' % (word, ' '.join([repr(val) for val in embedding])))
            tick(ctr, complete=False)

    outf.close()

    if verbose:
        tick(ctr, complete=True)
