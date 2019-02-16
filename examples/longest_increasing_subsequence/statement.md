We are given a sequence of distinct natural numbers, like:

s = 51, 3, 35, 7, 11, 22, 54, 66, 33, 56, 2

A sequence obtained by dropping some of the elements of s is called a <em>subsequence</em> of s, like for example:

35, 54, 66, which is an <em>increasing</em> subsequence, 

or

51, 35, 22, 2, which is a <em>decreasing</em> subsequence.

Write an algorithm that computes a longest possible increasing subsequence for any possible sequence given in input.
Not all algorithms are equally good, here are a few significant goals concerning performances and resource consumption:
(1) exponential time (exhaustive algorithm),
(2) quadratic time and memory,
(3) quadratic time but linear memory,
(4) n log n  time but linear memory.
Other 4 respectively higher goals are achieved by algorithms that, within the same bounds, also return an optimal subsequence and not only its length.  

Notice that the solution may not be unique. For example,

s1 = 3, 7, 11, 22, 54, 66

and

s2 = 3, 7, 11, 22, 54, 56

are both increasing subsequences of s of length 6.

Consider now the following six decreasing subsequences of s:

1. 51, 35, 7, 2
2. 54, 33
3. 66, 56
4. 11, 2
5. 22
6. 3

since every element of s is contained in at least one of these six subsequences, we call them a <em>covering</em> of s by 6 decreasing subsequences.

A neat observation is that a decreasing subsequence and an increasing subsequence can have at most one single element of the original sequence in common.
As such, the above covering of s by 6 decreasing subsequences provides clear evidence that no increasing subsequence of s can contain 7 elements or more. Since such kind of evidence can be easily checked, we consider the 6 decreasing subsequences a <em>certificate of optimality</em> for the two increasing sequences of maximum length (now we know!) s1 and s2 given more above.

As a further goal, your algorithm could also attempt to deliver such a certificate of optimality whenever it exists. We assume each element of s is colored with one of the 6 decreasing subsequence it belongs to. The evaluator program will ask your code the color of each element, check that you only use 6 colors, and check that the elements of a same color form a decreasing subsequence of s. After these checks, the optimality of an increasing subsequence is out of discussion (you have designed and coded a self-certifying algorithm that, whenever it answers, you can be sure of the correctness of its answer).

