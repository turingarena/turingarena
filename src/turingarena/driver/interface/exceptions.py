class CommunicationError(Exception):
    """
    Raised when the communication with a process is interrupted.
    """


class InterfaceExitReached(Exception):
    pass


class DriverStop(Exception):
    pass