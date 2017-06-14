#!/usr/bin/env python3

import sys

__version__ = '0.99'

header = '''\
__  _  __ ___ _ _ __ __  ___ _ _ _ ______
|_)|_|(_ (_ |_|| ||_)| \(_ |_||_||_/|_ |_)
|  | |__)__)||||_|| \|_/__)| || || \|__| \_v{}
'''.format(__version__)

charsets = {
  'alphanum': '0..9A..Za..z',
  'extended': '0..9A..Za..z!@#$%',
  'ascii': '!..~',
}


def expand(s):
  '''Create a string of characters by expanding dots

  Given an input string of the form "a..e" expands the dots to form "abcde"
  following the order of the ascii table. The full printable ascii table is
  generated from "!..~". The input string can contain multiple sets of dots, as
  in "0..9A..Za..z" which generates the full set of alphanumerical symbols. To
  begin a range with a dot it should be escaped as "./..".'''

  chars, *parts = s.split('..')
  for part in parts:
    chars += ''.join(chr(i) for i in range(ord(chars[-1])+1,ord(part[0]))) + part
  return chars


def get_config_path(service):
  '''Create a path object to the config file for service

  Tests for existence of a ~/.config/passwordshaker or ~/.passwordshaker
  directory, in that order, and returns a pathlib.Path instance to the
  (possibly nonexistent) configuration file within, or None if no directory was
  found to exist.'''

  import pathlib
  home = pathlib.Path.home()
  for path in home/'.config'/'passwordshaker', home/'.passwordshaker':
    if path.is_dir():
      return path / service


def load_options(service, **args):
  '''Load options from config file and optionally amend them

  Returns a dictionary with the keys 'modifier', 'length' and 'charset', and
  possibly other data. Values are obtained from keyword arguments, a config
  file (if existing), or default values, in decreasing order of priority. An
  empty modifier results in automatic generation of a new, previously unused
  modifier. For this a configuration path must be active.'''

  path = get_config_path(service)
  path_items = [line.rstrip().partition(' ')[::2] for line in path.open()] if path and path.is_file() else []
  conf = {'modifier': service, 'length': '32', 'charset': 'ascii'} # default values
  conf.update(path_items) # stored values
  conf.update(args) # newly specified values
  if not conf['modifier']:
    print('automatically selecting new modifier', file=sys.stderr)
    assert path, 'automatic modification requires a config path'
    i = 1
    used_suffices = [value[len(service):] for key, value in path_items if key=='modifier' and value.startswith(service)]
    while str(i) in used_suffices:
      i += 1
    conf['modifier'] = service+str(i)
  # parse options
  options = {key: value for key, value in conf.items() if value} # clear erased values
  assert options['charset'] in charsets, 'invalid character set {!r}; choose from {}'.format(options['charset'], ', '.join(charsets))
  assert options['length'].isdigit(), 'invalid length {!r}'.format(options['length'])
  options['length'] = int(conf['length'])
  return options


def save_options(service, options):
  '''Store options in config file

  Takes an options dictionary as returned by load_options and stores it in the
  configuration directory, appending to previously existing data in case values
  have changed. Silently returns if no configuration directory exists.'''

  path = get_config_path(service)
  if not path:
    return
  conf = {'modifier': service}
  if path.is_file():
    conf.update(line.rstrip().partition(' ')[::2] for line in path.open())
  changes = {key: str(value) for key, value in options.items() if str(value) != conf.pop(key, '')}
  changes.update((key, '') for key, value in conf.items() if value) # clear removed items
  if not changes:
    return
  print('updating', ', '.join(changes), file=sys.stderr)
  with path.open('a') as f:
    for key, value in changes.items():
      print(key, value, file=f)


def generate(key, chars, length):
  '''Generate character string by long division of shake_256 hash

  The core functionality of the passwordshaker module. Hashes the `key` string
  using the shake_256 algorithm, and composes from that a string of speficied
  length and characters.'''

  import hashlib, math
  nchars = len(chars)
  nbytes = math.ceil(length * math.log2(nchars) / 8)
  v = 0
  for b in hashlib.shake_256(key.encode()).digest(nbytes):
    v <<= 8
    v += b
  pw = ''
  for _ in range(length):
    v, n = divmod(v, nchars)
    pw += chars[n]
  assert v < 256
  return pw


def password(modifier, length, charset, **other):
  '''Convenience function for command line interaction

  Displays the provided information, requests the master key, displays a
  4-syllable fingerprint, and returns the password corresponding to the given
  specifications.'''

  import getpass
  print('shaking {}{} password for {}'.format(charset, length, modifier), file=sys.stderr)
  for key, val in other.items():
    print('{}: {}'.format(key, val), file=sys.stderr)
  secret = getpass.getpass('master key: ')
  if not secret:
    raise KeyboardInterrupt
  print('fingerprint:', generate(key=secret, chars=[c+v for c in 'bcdfghjklmnpqrstvwxz' for v in 'aeiouy'], length=2), file=sys.stderr)
  return generate(key=secret+modifier, chars=expand(charsets[charset]), length=length)
