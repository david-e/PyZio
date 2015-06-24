"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

from PyZio.interface import Interface


class Socket(Interface):
    def __init__(self, parent):
        Interface.__init__(self, parent)