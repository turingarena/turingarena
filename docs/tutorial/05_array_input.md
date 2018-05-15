# Array input

Now it's time to create problems with a more complex interface.
Consider the example problem `max_in_sequence`.
It asks to write a function `max_index`,
which accepts an array of values as argument,
and returns the index of the element in the array
with the maximum value.
Actually, the function `max_index` has two arguments:

- `n`, the number of elements in the array,
- `a`, the array of values, containing `n` elements.

In Python, a correct solution is simply
```python
def max_index(n, a):
    return a.index(max(a))
```

Have a look at the `interface.txt` file for this problem.
First, the value `n` is read from input.
Then, `n` values are read from input and saved in the array `a`.
To read `n` values, a `for` cycle is used.

## Try it yourself!

Create a problem which asks to write a function that compares two arrays of the same length,
returning the first index where they differ.
Remember: you need to read the length `n` of the two arrays only *once*.
To read the values of the two arrays, you can either use the same `for` cycle, or two different `for` cycles, the choice is yours.
