The main block is a tree of statements (corresponding to its AST).

The tree of statements is transformed as follows.

1. Expansion phase.
    1. A `call` statements is transformed into up to three nodes:
        - a `call_arguments` node, if the function accepts any non-redundant argument,
        - a `callbacks` node, if the function accepts callbacks,
        - a `call_return` node, if the function returns a value.
    1. At the beginning of each callback, a `callback_arguments` node is inserted.
1. Contraction phase.
    - Leaf nodes have one of two types:
        - *input* (`read`, `call_arguments` and `return`), or
        - *output* (`write`, `checkpoint`, `call_return` and `callback_arguments`).
    - A transformation is applied bottom-up which transforms subtrees into macro-leaves.
    - A macro-leaf can be either of type *input* or *output*.
    - All the leaf grouped into a macro-leaf have the same type as the macro-leaf.
    - Steps:
        1. Consecutive leaves of the same type are joined into a macro-leaf.
        1. A `for` cycle which does not have local variables and contains a single (macro-)leaf
        is into converted to a macro-leaf.
        1. `if` and `switch` statements where each of the branches/cases
        contains a single (macro-)leaf,
        and these leaves have the same type,
        are converted to a macro-leaf of that type.
        (`if` and `switch` statements cannot ever have local variables.)
        1. `callbacks` and`loop` nodes are never transformed.

The tree is now executed normally, but
each macro-leaf is executed twice.

- *input* macro-leaf.
    - In the first execution, the `read` leaves are ignored.
    - In the second execution, only the `read` leaves are executed.
- *output* macro-leaf.
    - In the first execution, only the `write` and `checkpoint` leaves are executed.
    - In the second execution, the `write` and `checkpoint` leaves are ignored.

In the first execution of input macro-leaves,
it is possible to peek the next request to resolve `if`/`switch` branches/cases.
