"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

class ZioException(Exception):
    """
    Generic ZIO error exception
    """

    def __init__(self, code, message):
        Exception.__init__()
        self.error_code = code
        self.error_message = message

    def __str__(self):
        return "Zio Error {0}: {1}".format(self.code, self.message)


class ZioInvalidControl(ZioException):
    """
    The library raises this error when the application requires to use an
    invalid control
    """

    def __init__(self, ctrl):
        ZioException.__init__(0, "Invalid control")
        self.invalid_ctrl = ctrl


class ZioMissingAttribute(ZioException):
    """
    The library raises this error when the application try to use an attribute
    that does not exists
    """

    def __init__(self, attr_name):
        ZioException.__init__(1, "Missing attribute")
        self.missing_attr_name = attr_name
