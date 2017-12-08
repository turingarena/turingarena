class ProtocolError(Exception):
    def __init__(self, message, *, parseinfo=None):
        self.message = message
        self.parseinfo = parseinfo

    def get_user_message(self):
        lineinfo = self.parseinfo.buffer.line_info(self.parseinfo.endpos)
        # lines are zero-based-numbered
        return f"{lineinfo.filename}:{lineinfo.line+1}:{lineinfo.col+1}: {self.message}"

