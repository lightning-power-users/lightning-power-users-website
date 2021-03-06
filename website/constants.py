import os
import platform
from datetime import timedelta
from decimal import Decimal
from os.path import expanduser
from typing import Dict


class StringConstant(object):
    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

    def __ne__(self, other):
        return str(other).lower() != self.name

    def __repr__(self):
        return self.name


class OperatingSystem(StringConstant):
    pass


DARWIN: OperatingSystem = OperatingSystem('darwin')
LINUX: OperatingSystem = OperatingSystem('linux')
WINDOWS: OperatingSystem = OperatingSystem('windows')
OPERATING_SYSTEM = OperatingSystem(platform.system())

IS_MACOS = OPERATING_SYSTEM == DARWIN
IS_LINUX = OPERATING_SYSTEM == LINUX
IS_WINDOWS = OPERATING_SYSTEM == WINDOWS

# Only relevant for Windows
LOCALAPPDATA = os.path.abspath(os.environ.get('LOCALAPPDATA', ''))
APPDATA = os.path.abspath(os.environ.get('APPDATA', ''))
PROGRAMS = os.environ.get('Programw6432', '')

FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']

WEBSITE_DATA_PATHS: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Node Website/'),
    LINUX: expanduser('~/.node_website'),
    WINDOWS: os.path.join(LOCALAPPDATA, 'Node Website')
}
WEBSITE_DATA_PATH = WEBSITE_DATA_PATHS[OPERATING_SYSTEM]

if not os.path.exists(WEBSITE_DATA_PATH):
    os.mkdir(WEBSITE_DATA_PATH)

CACHE_PATH = os.path.join(WEBSITE_DATA_PATH, 'cache')

if not os.path.exists(CACHE_PATH):
    os.mkdir(CACHE_PATH)

EXPECTED_BYTES = 500

CAPACITY_CHOICES = [500000, 1000000, 2000000, 5000000, 16777215]

CAPACITY_FEE_RATES = [
    (Decimal('0'), 'Three days free', timedelta(days=3)),
    (Decimal('0.005'), 'Three days 0.5%', timedelta(days=3)),
    (Decimal('0.01'), 'Two weeks 1%', timedelta(weeks=2)),
    (Decimal('0.03'), 'One month 3%', timedelta(days=31))
]

if IS_WINDOWS:
    from keyring.backends.Windows import WinVaultKeyring

    keyring = WinVaultKeyring()

if IS_MACOS:
    from keyring.backends.OS_X import Keyring

    keyring = Keyring()

if IS_LINUX:
    from keyring.backends.SecretService import Keyring

    keyring = Keyring()
