class ProxyConnection:
    def __init__(self, *, request_pipe, response_pipe):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
