"""
Defines the module's version, read from the version.txt file.
"""

import os

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.txt'),
    'r'
) as f:
    __version__ = f.read().strip()
