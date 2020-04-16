#!/usr/bin/env python3

import sys, hashlib, math, pathlib, getpass, time

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


def get_config_path():
  '''Return a path object to the (possibly nonexistent) config directory

  Returns a pathlib.Path reference to ~/.config/passwordshaker if it exists,
  otherwise ~/.passwordshaker if it exists, otherwise ~/.config/passwordshaker.'''

  home = pathlib.Path.home()
  path = home / '.config' / 'passwordshaker'
  if not path.is_dir():
    altpath = home / '.passwordshaker'
    if altpath.is_dir():
      return altpath
  return path


def iter_options(service):
  '''Iterate over key, value pairs in a service config file.

  Returns an iterator for ``service``, which can be a string or a path object.
  If the service file does not exist an empty iterator is returned.'''

  if isinstance(service, str):
    service = get_config_path() / service
  if service.is_file():
    with service.open() as lines:
      yield from (line.rstrip().partition(' ')[::2] for line in lines if not line.startswith('#'))


def load_options(service, **args):
  '''Load options from config file and optionally amend them

  Returns a dictionary with the keys 'modifier', 'length' and 'charset', and
  possibly other data. Values are obtained from keyword arguments, a config
  file (if existing), or default values, in decreasing order of priority.'''

  args.update((key, value) for key, value in iter_options(service) if key not in args)
  options = {'modifier': service, 'length': '32', 'charset': 'ascii'} # default values
  options.update((key, value) for key, value in args.items() if value)
  options['charset'] = charsets.get(options['charset'], options['charset'])
  assert options['length'].isdigit(), 'invalid length {!r}'.format(options['length'])
  options['length'] = int(options['length'])
  return options


def save_options(service, options, ask=False):
  '''Store options in config file

  Takes an options dictionary as returned by load_options and stores it in the
  configuration directory, appending to previously existing data in case values
  have changed. Silently returns if no configuration directory exists.'''

  path = get_config_path()
  if options.get('modifier') == service:
    del options['modifier']
  for key, value in dict(iter_options(path/service)).items():
    if key not in options:
      options[key] = ''
    elif str(options[key]) == value:
      del options[key]
  if not options or ask and input('store changed entries? y/[n]') != 'y':
    return
  path.mkdir(parents=True, exist_ok=True, mode=700)
  print('updating', ', '.join(options), file=sys.stderr)
  with (path/service).open('a') as f:
    print('#', time.ctime(), file=f)
    for key, value in options.items():
      print(key, value, file=f)


def generate(key, chars, length):
  '''Generate character string by long division of shake_256 hash

  The core functionality of the passwordshaker module. Hashes the `key` string
  using the shake_256 algorithm, and composes from that a string of speficied
  length and characters.'''

  nchars = len(chars)
  nbytes = math.ceil(length * math.log2(nchars) / 8) # 256**nbytes >= nchars**length
  v = int(hashlib.shake_256(key.encode()).hexdigest(nbytes), 16)
  pw = ''
  for _ in range(length):
    v, n = divmod(v, nchars)
    pw += chars[n]
  assert v < 256
  return pw


def fingerprint(key, length=2):
  '''Generate an easily recognizable fingerprint.

  The fingerprint is made up of a configurable number of consonant+vowel
  digraphs so as to form an legible word, that can be used to confirm that a
  secret is entered correctly without revealing its contents.

  In order to leak a minimum level of information about the secret, the space
  of fingerprints is constructed such that its size is always a power of two,
  so that it maps uniformly from the (much larger) space of secrets.
  '''

  digraphs = [c+v for c in 'bcdfglmnprst' for v in 'aeiouy' if v in 'aeio' or c not in 'bdfs']
  assert len(digraphs) == 64 # 6 bits per digraph
  return generate(key, digraphs, length)


def password(modifier, length, charset, **other):
  '''Convenience function for command line interaction

  Displays the provided information, requests the master key, displays a
  4-syllable fingerprint, and returns the password corresponding to the given
  specifications.'''

  chars = expand(charset)
  print('shaking {:.0f}-bit password for {}'.format(length * math.log2(len(chars)), modifier), file=sys.stderr)
  for key, val in other.items():
    print('{}: {}'.format(key, val), file=sys.stderr)
  secret = getpass.getpass('master key: ')
  if not secret:
    raise KeyboardInterrupt
  print('fingerprint:', fingerprint(secret), file=sys.stderr)
  return generate(key=secret+modifier, chars=chars, length=length)
