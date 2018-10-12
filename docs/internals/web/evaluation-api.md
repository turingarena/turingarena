# TuringArena Web Evaluation API

A Web API based on SEWI is described,
meant to perform submission evaluations based on TuringArena via Web.

The API supports the following methods.

- *evaluate*, used to start a new evaluation, using a given evaluator and a given submission,
- *evaluation events*, used to get a page of evaluation events of an ongoing evaluation.

Let `base_url` denote the base URL where the API is deployed.

## Evaluate

A call to *evaluate* is SEWI request with:

- URL template: `{+base_url}/evaluate`.

### Request

The request includes the provided submission, with base name `submission`.
See [Submissions in Web APIs](../evaluation/web.md#submissions)

The other parameters are:
- `repository[url]`: the URL of the repo to clone.
- `repository[branch]`, optional.
- `repository[depth]`, optional.
- `commit_oid`, the OID of the commit to consider.
- `directory`, the directory of the problems, optional.
- `evaluator_cmd`, the command to run as evaluator.

The commit OID (SHA-1 hash) is required in the requests for repeatability and caching.

### Response

The response body of *evaluate* is a JSON object, with the following fields.

- `evaluation_id`: a *string* identifying the newly created evaluation.

## Evaluation events

A call to *evaluation events* is an HTTP request as follows.

- Method: `GET`.
- URL template: `{+base_url}/evaluation/{evaluation_id}/events{?after}`,
- Template parameters
    - `evaluation_id`, required, containing the ID of the evaluation,
    - `after`, optional,
    a cursor indicating the beginning of the desired page
    (the cursor is implicitly `null` if this parameter is absent).

In normal conditions, the response body is a page of evaluation events, represented as JSON,
starting at the cursor provided in the `after` parameter
(i.e., the first page if `after` is absent).
The page can be empty.

A request should be repeatable in case of errors,
until the client actually reads *after* the returned page.
More precisely, a call to *evaluation events* (request 1) should succeed as long as
no other requests to *evaluation events* have been performed (request 2),
such that the `after` parameter of request 2 occurs strictly later than the `after` parameter of request 1.
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