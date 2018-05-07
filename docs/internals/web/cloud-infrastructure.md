# TuringArena Cloud Infrastructure

TuringArena should provide a cloud infrastructure,
in source code form and possibly as SaaS,
which performs evaluation of submissions
for challenges created using TuringArena.

Some implementation ideas are presented.

The cloud infrastructure is server-less,
meaning that no cloud resources are used
when no evaluations are performed
(excluding cloud data storage).

## API Gateway

The Amazon Web Services (AWS) [API Gateway](https://aws.amazon.com/api-gateway/)
is used to publish the API over the internet.
Using AWS API Gateway the following limitations are present.

- Requests must be short-lived.
The maximum timeout is 29 second, which is potentially less than the duration of an evaluation. 
- Request/response payload cannot exceed 10MB.
This should be acceptable when sending submissions (via SEWI).
- The response is fully-buffered.

## API backend

To implement the API,
all the requests
can be forwarded to [AWS Lambda](https://aws.amazon.com/lambda/)
using the *HTTP Proxy* integration of AWS API Gateway.
(AWS Lambda can run Python 3.6 applications.)
Using AWS Lambda all the requests must be asynchronous,
since AWS Lambda is billed by time.

## Evaluation storage

The evaluation is stored using [AWS DynamoDB](https://aws.amazon.com/dynamodb/),
which is especially cheap.
The storage format is as follows.
The evaluation events are divided in pages.

The page is stored in a single Item, with the following keys.

- *Partition Key*: the ID of the evaluation.
- *Sort Key*: the index of this page in the evaluation.

The events in the page are represented as [JSON Lines](http://jsonlines.org),
possibly compressed (say, with *gzip*), and represented in a single Binary field.

A new event page is created when either

- the total size of the page exceeds what can be stored in a single DynamoDB Item, or
- a sufficiently long time has passed since the first event in the page (say, ~100ms).

When the end of stream is reached,
a new page is created, containing an end-of-stream marker, and no payload.

### Cursors and queries

Cursors are based on the page index.
(Perhaps, using odd numbers for pages and even numbers for cursors
avoids the ambiguity of strict/non-strict inequalities.)
To get the page after a given cursor,
it is sufficient to make a single DynamoDB Query,
asking for all the items with a given evaluation ID,
and with index staring from the provided cursors.
Then, the item payloads are joined in a single page,
starting from the beginning of the query, until either:

- the end-of-stream marker is reached,
- the end of the query results is reached,
- enough events have been gathered to be returned in a single HTTP response, or
- a page is missing in the results, as determined by page indexes. 

The latter check is needed to avoid problems arising from eventual consistency.

### Rationale

While DynamoDB does not apply naturally to representing streams,
it is a good compromise: it's fast and cheap, and (using eventually consistent reads) 
it should introduce a latency within 1 second
between the creation of an event and its availability for clients.

The payload is represented as JSON Lines (stringified, possibly compressed),
instead of using the DynamoDB data model,
because internal fields of the payload are never used for queries
(which anyhow provide little guarantees when working with non-key fields).
This improves both efficiency and simplifies the implementation.

JSON Lines is chosen instead of JSON arrays so that an implementation
cloud split and join pages of events without the need of parsing JSON.

## Evaluations

The evaluation itself is performed in a Docker container.
The [Hyper.sh](www.hyper.sh) service offers on-demand Docker containers,
billed per-second.
Using Hyper.sh it is possible to start a new container per-evaluation,
keeping the infrastructure server-less
and allowing horizontal scaling.

To implement the *evaluate* API call,
the code running in AWS Lambda
starts a container by calling an Hyper.sh [Func](https://docs.hyper.sh/Feature/container/func.html),
forwarding the request,
and sending other meta-data (e.g., AWS credentials) via HTTP headers.
The call to Hyper.sh Func is asynchronous,
and there is no hard timeout.

The started container should perform the evaluation
and store it directly in DynamoDB.
