# passwordshaker
Simple password manager, generator based on SHAKE256 hashes

The problem with passwords is well known: password reuse is [unsafe][1], as a
single [breach][2] leads to compromise of all accounts, but having strong,
independently generated passwords for all services necessitates the creation of
a password vault. Whether on-line or off-line, the existence of this vault is
in itself a security hazard.

A password vault can be avoided if passwords share a common structure, by
combining a single memorized master password with a unique but easily
rememberable identifier for the service. Using simple concatenation, for
example, a password 's3cret' can be turned into 's3cretgmail' for Gmail and
's3cretfacebook' for Facebook. The problem with this particular choice of
algorithm is that it is trivially invertible, so a Facebook security breach may
still lead to a compromised Gmail account.

Passwordshaker employs a different algorithm that does not suffer from this
issue: rather than concatenating, the master password and service identifier
are joined using a strong, irreversible hash function (SHAKE256). Though this
comes at the disadvantage of requiring the aid of a computer, what remains is a
secure method of password generation that requires no password vault, and where
a single 3rd party data breach cannot escalate to other accounts.

The name passwordshaker is a play on [passwordmaker][3], a password management
suite that implements the same concept with some implementational differences,
most notably the employed hash function. Note that because of these differences
the generated passwords are mutually incompatible.

## usage: pws

The main passwordmaker component is the (linux) `pws` command line tool. Pws
has a fairly simple interface. The following demonstrates the typical use:

    $ pws facebook
    __  _  __ ___ _ _ __ __  ___ _ _ _ ______
    |_)|_|(_ (_ |_|| ||_)| \(_ |_||_||_/|_ |_)
    |  | |__)__)||||_|| \|_/__)| || || \|__| \_v0.99
    
    shaking ascii32 password for facebook
    master key:
    fingerprint: kufa
    copying to clipboard for 60 seconds
    clipboard cleared

Here, the argument "facebook" is the (easily rememberable) service identifier.
By default a 32 character password is generated out of all printable ascii
characters. The secret master key is hashed using a 2-byte hash and turned into
an 4-character, easily recognizable "fingerprint", which makes it possible to
spot typing mistakes without revealing the key itself. Finally, the generated
password is copied to clipboard and automatically cleared after 60 seconds.

The password length and character set may need to be adapted to the specific
restrictions posed by the service. This is done using the command line
arguments --length=# and --charset=alphanum/extended/ascii. In order to not
have to remember these extra variables, the settings will be transparantly
stored in a directory ~/.config/passwordshaker or ~/.passwordshaker, if it
exists. Stored values per service will override built-in defaults.

To accomodate the situation of forced (or otherwise desired) password renewal,
the --modifier=... overrides the service name for password generation. In
combination with automatic storage this results in a password change without
having to remember a different service identifier. For convenience, leaving the
modifier empty (--modifier=) results in the automatic generation of a
previously unused modifier.

Because it is often useful to have additional related information avaiable when
logging in to a service, such as a user name, any other command line argument
of the type --key=value is stored along with the other settings, and displayed
as key: value before requesting the master key. Values can be updated by
specifying --key=newvalue, or removed using --key=.

Data storage takes place after a master key has been entered, so unwanted
changes can be averted by pressing ^C or enter. Furthermore, data is strictly
appended to the existing file and written in plain ascii, so even in the
situation that unwanted changes are made, previous data is easily retrieved.

## usage: git

The `git-credential-pws` script is available to use passwordshaker in
combination with git. Placed in the executable path, it is activated by adding
the following lines to your global .gitconfig:

    [credential]
      helper=pws

With that in place, instead of asking for a password directly, git will bring
up the passwordshaker interface using the host as service identifier. Settings
are read from the corresponding config file and can be alterad via `pws`.

## usage: other

Embedding passwordshaker into other services is possible by making use of the
Python module. The functions `load_options` and `password` should suffice for
most purposes.

## installation

Passwordshaker does not have any dependencies other than Python 3.6 and can be
used directly from the repository. Alternatively it can be installed system
wide using Python's setuptools:

    python3 setup.py install

Or in ~/.local/bin:

    python3 setup.py install --user

This will install `pws`, `git-credential-pws`, and the passwordshaker Python
module. Pws requires [xsel][4] to be installed for accessing the X clipboard.

[1]: https://xkcd.com/792/
[2]: https://haveibeenpwned.com/
[3]: https://passwordmaker.org/
[4]: http://www.kfish.org/software/xsel/
