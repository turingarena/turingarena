# Example problems

Before creating your first problem,
have a look at some of the examples problems
provided along with TuringArena itself.
They all share the same directory structure,
but they also highlight different features of the TuringArena system.

Let's start with the simplest problem first:
`sum_of_two_numbers`,
that you can find in the directory `examples/sum_of_two_numbers/`
in the TuringArena repository.
In this problem,
one is asked to write a function (called `sum`)
that computes the sum of two numbers given as arguments.

You can find examples of correct solutions in the `solutions/` subdirectory,
written in several programming languages.
For example, in C++, a correct solution is:
```c++
int sum(int a, int b) {
    return a + b;
}
```

You can test this solution by running
```bash
turingarena evaluate solution/correct.cpp
```

## Try it yourself!

To start working on your own problem,
copy the example problem in a new directory.

```bash
# we are currently in the repository folder
mkdir $HOME/my_turingarena_problems  # create a folder in your home directory
cp -r examples/sum_of_two_numbers/ $HOME/my_turingarena_problems/  # copy the example problem
cd $HOME/my_turingarena_problems  # move into the new folder
git init  # create a Git repository here (needed for TuringArena to work)
cd sum_of_two_numbers
turingarena evaluate solutions/correct.cpp

```

Now write your own solution, in the `solutions` directory, and test it!
