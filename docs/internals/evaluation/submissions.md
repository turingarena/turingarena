## Submissions

A **submission** is a collection of **fields**.
Each field is identified by a **field name** and is mapped to a **submission file**.

### Field names

Field names are ASCII strings, which must:

- contain only 
    - lowercase letters (`a-z`),
    - numbers (`0-9`),
    - underscores (`_`);
- start with a letter;
- be unique inside a submission (they are associated to a single value).

### Submission files

A submission file is a regular file (i.e., an array of bytes)
in an unspecified format.
Besides the file content, a submission file also specifies a *filename*.

The directory components of the filename, if any,
should not be taken into account in evaluators. 

### Rationale

The format of submissions is chosen so that it maps naturally to HTML *forms*,
and the `multipart/form-data` content type in HTTP requests, for Web based APIs.
(See [Web/Submissions](web/submissions.md) for more info.)
