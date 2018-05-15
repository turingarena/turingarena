# Array output

We have seen how to send an array as input to the solution.
Now let's see how to receive an array as output.

Consider the example problem `sort`,
which asks to implement a function which sorts an array given in input.

## Communication protocol

To provide support for a broad class of programming languages,
TuringArena imposes some restrictions on the interface.
One of this restriction is that *functions can only return scalar values*, i.e., it is not possible to directly return an array from a function.
This limitation is overcome by calling a function multiple times, each time returning a different element of the array.

Look at the file `interface.txt` for the `sort` problem.
It defines two functions:

- `sort`, which takes the number of elements `n` and the array `a`, but does not return anything (it is supposed to store the sorted array in a global variable),
- `get_element`, which takes an index `i` and returns the `i`-th element of the sorted array.

After reading the input array and calling `sort`,
the communication protocol calls the `get_element` function
`n` times, and writes the return value of each call.
Again, a `for` cycle is used for this purpose.

## Motivation

Imagine to define a function `sort` which directly returns an array.
In C++, there are many different ways it can be defined:

```c++
void sort(int n, int[] a, int[] output);
int* sort(int n, int[] a);
std::vector<int> sort(int n, int[] a);
std::array<int, MAXN> sort(int n, int[] a);
```

None of the above is preferable of the others.
Now consider Python:
```python
def sort(n, a):
    # ...
```

What should `sort` return? A `list`? Any instance of `Sequence`? Or `Iterable`? Can it use a generator?

Compare the above with the following.

```c++
#include <vector>
#include <algorithm>

std::vector<int> b;

void sort(int n, int* a) {
    b = {a, a+n};
    std::sort(b.begin(), b.end());
}

int get_element(int i) {
    return b[i];
}
```

```python
def sort(n, a):
    global b
    b = sorted(a)

def get_element(i):
    return b[i]
```

Here both C++ and Python solutions can use whatever data structure they want to store the sorted array,
as long as they are able to provide its elements one by one.

## Try it yourself!

Write a problem which uses arrays both for input and output.
