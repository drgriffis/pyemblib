import setuptools
import pyemblib

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name=pyemblib.name,
    version=pyemblib.version,
    author='Denis Newman-Griffis',
    author_email='denis.newman.griffis@gmail.com',
    description='Lightweight package for reading/writing pre-trained word embedding files',
    long_description=long_description,
    long_description_context_type='text/markdown',
    url='http://github.com/drgriffis/pyemblib',
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
