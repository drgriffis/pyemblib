# pyemblib

A module for reading, writing, and using trained word embeddings.

## Installation

Install as a module in your Python path.  For example, if you clone the repository to `~/Software/pyemblib`, add the following to your `.bashrc`:

```bash
export PYTHONPATH=${HOME}/Software/pyemblib:${PYTHONPATH}
```

## Usage

This package currently supports word embeddings trained by the following packages:

- [word2vec](https://code.google.com/archive/p/word2vec/)
- [GloVe](https://nlp.stanford.edu/projects/glove/)

### Reading

Both text-format and binary embedding files are supported.

The example below shows reading each format of embedding:
```python
## import text embeddings
text_embs = pyemblib.read('/tmp/text_embeddings.txt', mode=pyemblib.Mode.Text)
## import binary embeddings
bin_embs = pyemblib.read('/tmp/bin_embeddings.bin', mode=pyemblib.Mode.Binary)
```

Embeddings are read as a `pyemblib.Embeddings` object, which inherits from Python's dictionary class; keys are words, and values are the embedding arrays.

To get the word vector for "python", just use dictionary access:
```python
vec = embs['python']
print(vec)
# [ 0.001 -0.237 ... ]
```

### Writing

The same text and binary modes can be used for writing out embedding files as for reading.

```python
embs = { 'a' : np.array([0.3 0.1 -0.2]), 'b' : np.array([-0.9, -0.2, -0.2]) }
## write as text
pyemblib.write(embs, '/tmp/text_embeddings.txt', mode=pyemblib.Mode.Text)
## write as binary
pyemblib.write(embs, '/tmp/bin_embeddings.bin', mode=pyemblib.Mode.Binary)
```

## Feedback
Please report any issues you encounter to the [Github Issues page](https://github.com/drgriffis/pyemblib/issues)!
