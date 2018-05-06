# TuringArena Cloud API

A Web API based on SEWI is described,
meant to perform submission evaluations based on TuringArena in the cloud.

The API supports two methods:

- *evaluate*, used to start a new evaluation, using a given evaluator and a given submission, and
- *evaluation events*, used to get a page of evaluation events of an ongoing evaluation.

Let `base_url` denote the base URL where the API is deployed.

## Evaluate

A call to *evaluate* is SEWI request with:

- URL template: `{+base_url}/evaluate`,
- only one submission with base name `submission`,
- some extra form fields described below.

TODO: extra fields

TODO: response body

## Evaluation events

A call to *evaluation events* is an HTTP request as follows.

- Method: `GET`.
- URL template: `{+base_url}/evaluation/{id}/events{?after}`,
- Template parameters
    - `evaluation`, required, containing the ID of the evaluation,
    - `after`, optional,
    a cursor indicating the beginning of the desired page
    (the cursor is implicitly `null` if this parameter is absent).

In normal conditions, the response body is a page of evaluation events, represented as JSON,
starting at the cursor provided in the `after` parameter
(i.e., the first page if `after` is absent).
The page can be empty.

A request should be repeatable in case of errors,
until the client actually reads *after* the returned page.
More precisely, a call to `evaluation` (request 1) should succeed as long as
no other requests to `evaluation` have been performed (request 2),
with the `after` parameter of request 2 occurring strictly later than the `after` parameter of request 1.
This assumption makes the protocol robust under HTTP errors,
but still allows an implementation to delete the events when it is sure that the client has received those.

## Implementation details

Every time an implementation receives a call to *evaluation events*,
it can delete all the events before the `after` parameter.
In order to be able to safely delete also the last page of events, an implementation may do the following.

- Define a dummy cursor `DUMMY_END`.
- When the last event is sent, set the `end` cursor of the page to `DUMMY_END`.
- When a request is received with `after` equal to `DUMMY_END`, return an empty page with `end` set to `null`,
and remove any remaining data stored for the current evaluation.

## Example

TODO