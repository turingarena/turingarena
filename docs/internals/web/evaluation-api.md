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

The  specifies which [*packs*](../packs.md)
should be available for the evaluation.
For each pack,
a field is added, with:

- name: `packs[]`,
- value: the pack SHA-1 hash, in lower-case hex.

In order to obtain the content of the packs,
the request also specifies zero or more [*pack repositories*](../packs.md#pack-repositories).
At a minimum, Git repositories should be supported as pack repositories.

For each Git repository to clone, the following fields are to be provided.

- `repositories[<name>][type]`: the constant `git_clone`.
- `repositories[<name>][url]`: the URL of the repo to clone.
- `repositories[<name>][branch]`, optional.
- `repositories[<name>][depth]`, optional.

The value `<name>` is a string identifying the repository.
It must match the following regexp `[_a-zA-Z][_a-zA-Z0-9]*`.

#### Rationale

Requiring the packs SHA-1 hash in the requests allows effective caching.
If they are all available locally, the repositories are not used.

In the future, each pack can be mapped to a repository,
so that only the needed repositories are queried when some pack is not available.
However, since this is an optimization feature,
this map should be specified *aside* the list of packs,
in order not to complicate the unoptimized version of the API.
Giving a name to each repository makes this extension easier.

The repositories could be entirely omitted
if the server contains the provided packs as built-in. 

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