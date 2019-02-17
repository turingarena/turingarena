#include <vector>
#include <algorithm>
#include <cassert>
#include <limits>

using std::vector;

//Data structures employed to solve the problem:
vector<int> len; // len[i] = max length of a subsequence taking element i as its last element. This defines the family of subproblems we will solve iteratively (dynamic programming approach).
vector<int> prev; // to reconstruct the optimal subsequence. For every i, we store in prev[i] the second last element in some maximum length subsequence taking element i as its last element. 
vector<vector<int>> antichains; // a vector containing the last element of each antichain would actually suffice, but we also want to reconstruct the certificate of optimality. 

//Data structures to support the max_length(), takes(), and color() query functions: 
int max_len;
vector<int> taken;
vector<int> antichain_of;

void compute(int n, int *s) {
    int values[n+2];
    for(int i = 0; i < n; i++) values[i+1] = s[i];
    values[n+1] = std::numeric_limits<int>::max(); // append a last element. Now every optimal solution takes the last (dummy) element and len[n+1] will eventullly contain the length of an optimal solution.
    values[0] = std::numeric_limits<int>::min(); // append a first element. This will also belong to every optimal solution and acts as sentinel for the binary searches.

    len.resize(n+2);
    prev.resize(n+2);
    antichains.resize(n+2);
    taken.resize(n+2);
    antichain_of.resize(n+2);

    len.push_back(1); // the maximum subsequence ending with the first element has length 1
    antichains[0].push_back(0); // the first dummy element is placed at the beginning of the first antichain (decreasing subsequence)
    antichain_of.push_back(0); //the first dummy element is placed in antichain 0

    for(int i = 1; i <= n+1; i++) {
        auto p = std::upper_bound(antichains.begin(), antichains.end(), i, [&](int i, vector<int>& ac) -> bool {
            return ac.empty() || values[i] < values[ac.back()];
        });
        assert(p > antichains.begin());
        assert(p < antichains.end());
	assert(p[-1].size()>0);

	p[0].push_back(i); // element i is placed on its antichain
	prev.push_back(p[-1].back()); // prev[i] = last element of previous antichain
        len.push_back(len[prev[i]] + 1); // len[i] = len[prev[i]] + 1
    }

// We can already answer the max_length() query:
    max_len = len[n+1] -2;

// set up the data structure to support the takes() query function: 
    for(int i = 0; i <= n+1; i++) taken[i] = false;
    int last_taken = n+1;
    while(last_taken > 0) {
        taken[last_taken] = true;
        last_taken = prev[last_taken];
    }

// set up the data structure to support the color_of() query function: 
    for(int i = 0; i <= n+1; i++)
      for(auto j = antichains[i].begin(); j < antichains[i].end(); j++)
        antichain_of[*j] = i;
}

int max_length() {
    return max_len;
}

int takes(int i) {
    return taken[i+1];
}

int color_of(int i) {
    return antichain_of[i+1];
}

