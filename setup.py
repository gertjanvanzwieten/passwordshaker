#! /usr/bin/env python3

import setuptools

with open('passwordshaker.py') as src:
  version = next(line[13:].strip() for line in src if line.startswith('__version__ ='))

setuptools.setup(
  name='passwordshaker',
  version=version,
  python_requires='>=3.6',
  author='Gertjan van Zwieten',
  py_modules=['passwordshaker'],
  scripts=['pws', 'git-credential-pws'],
)
