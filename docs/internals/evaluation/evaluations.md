# Evaluation

An evaluation is a stream of **events**.
Events can be of two types, **text** and **data**,
and contain a **payload**.

The payload of *text* events is a Unicode string.
The payload string must be non-empty, and either:

- does *not* contain any line-terminator, or
- consist of a single line-terminator only.

The payload of *data* events is any JSON value.

## Evaluation events as JSON

Each evaluation event is represented as a JSON object, with the following fields.

- `type`: a string, with value either `data` or `text`, according to the type of the event.
- `payload`: the event payload, i.e., either a JSON string (for text events) or any JSON value (for data events).

## Evaluation as JSON Lines streams

An evaluation is represented over a stream using the [JSON Lines format](http://jsonlines.org).
