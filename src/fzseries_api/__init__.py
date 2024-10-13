"""
This package does the Lord's work
of automating the process of downloading a series
from fztvseries.live. 

Right from performing `search` query down to downloading
them in your desired format.
"""

from importlib import metadata
import logging

try:
    __version__ = metadata.version("fzseries-api")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Smartwa"
__repo__ = "https://github.com/Simatwa/fzseries-api"

logger = logging.getLogger(__name__)