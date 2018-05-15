from turingarena_impl.api.backend import EventConsumer
from turingarena_impl.api.handler import EvaluationPage


class DynamoDbEventsHandler:
    def evaluation_events(self, evaluation_id: str, after: str) -> EvaluationPage:
        """
        Returns a page of evaluation events,
        reading it from a DynamoDB table.
        """
        # TODO


class DynamoDbEventConsumer(EventConsumer):
    """
    An event consumer which stores events in a DynamoDB table.

    A buffer of events is kept.
    The buffer is regularly flushed, i.e.,
    all the events currently in the buffer, if any is present,
    are stored as one or more DynamoDB Items and added to the table.
    The buffer is flushed using a single API call to DynamoDB.
    The buffer is considered full when, by adding more events to it,
    a single API call is no longer sufficient to store all the events.

    The buffer is flushed in three cases:
    1. when the consumer is closed,
    2. when the buffer is full,
    3. periodically, say, every 100ms.
    """

    def on_new_event(self, event):
        pass  # TODO

    def close(self):
        pass  # TODO
