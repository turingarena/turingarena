WARNING: this document contains old ideas which are not currently implemented in TuringArena.

# TuringArena packs

A TuringArena **pack** is a collection of software components, which can be:

- distributed, and
- provided to TuringArena when performing operations.

### Examples

- A pack which defines one or more problems.
- A pack which contains a library which can be used by other problems.
- A pack which contains a private add-on for a public problem, providing the correct solutions needed for a full evaluation.

## Format of packs

A pack is essentially a directory of files.
More precisely, a pack is represented as a
[Git tree object](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects#_tree_objects) and is identified by its SHA-1 hash.

### Rationale

We use Git tree objects for packs for the following reasons.

- Git tree objects represent the right subset of file metadata (filename, executable bit, symlinks) and are safe to distribute (no users/groups and other inode properties, as in `tar`).
- The secure hashing can be used for caching purposes.
- Git will probably be the most used tool to distribute packs, so the mapping to Git trees is natural.

## Loading packs

When a pack is provided, the root directory of the pack is made available in the Python 3 *path*.
In turn, the Python path is used
(via the `__path__` property of Python packages)
when looking for specific files.

### Rationale

Instead of developing a new module system used to identify, find and load different software components (in the form of files), the Python module system is exploited.
Thanks to *namespace packages* of Python 3, no extra effort is required to map module names to directories in packs,
and portions of the same package can be distributed in different packs.

## Pack repositories

Some mechanisms are presented to load the content of a pack,
identified by its SHA-1 hash,
when it is not available.
Such a mechanism is called a **pack repository**.

### Git

A Git clone is performed with some specified parameters,
including the following.

- Git repository URL, required.
- A Git *ref*, optional, the default is provided by the repository itself.
- The clone *depth*, optional, defaulting to no depth (deep clone).

All the git tree objects present in the repository after the clone
are made available as packs.

### Archive

A provided file archive (e.g., *tar* or *zip*) is extracted.
Then, the content of the archive is added to a Git index and a Git tree object is created.
The tree object obtained and all of its subtrees are made available as packs.

### Archive URL

An URL is used to download a file archive, which is then processed as above. 
