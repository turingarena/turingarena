from abc import ABC, abstractmethod


class EventConsumer(ABC):
    """
    Receives a stream of evaluation events (to show/store them).
    """

    @abstractmethod
    def on_new_event(self, event):
        """
        Called when a new event is produces.
        """

    @abstractmethod
    def close(self):
        """
        Called when the stream of events is finished.
        """


class EvaluationBackend:
    def __init__(self, event_consumer: EventConsumer):
        self.event_consumer = event_consumer

    def evaluate(self, submission):
        pass
