#! /usr/bin/env python3

import passwordshaker, setuptools
assert passwordshaker.generate(key='test', chars='1234567890', length=32) == '99966624670202589612394126726588', 'selfcheck failed'

setuptools.setup(
  name='passwordshaker',
  version=passwordshaker.__version__,
  author='Gertjan van Zwieten',
  py_modules=['passwordshaker'],
  scripts=['pws', 'git-credential-pws'],
)
