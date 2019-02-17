#include "assert.h"
#include "limits.h"

#define MAXN 10000

//Data structures employed to solve the problem:
int len[MAXN+2]; // len[i] = max length of a subsequence taking element i as its last element. This defines the family of subproblems we will solve iteratively (dynamic programming approach).
int prev[MAXN+2]; // to reconstruct the optimal subsequence. For every i, we store in prev[i] the second last element in some maximum length subsequence taking element i as its last element. 
int slast_for_len[MAXN+2]; // we read and add the elements of the input sequence s one by one, each time mantaining updated this vector so that, after element s[i] has been taken in (that is, with reference to the prefix s[0..i] of the input sequence) slast_for_len[MAXN+2] contains the smallest possible value for the last element of an increasing subsequence of length at least i. 
int slast_ele_len[MAXN+2]; // slast_ele_len[i] = the name of the element of smallest value that can and an increasing subsequence of length i. 

//Data structures to support the max_length() and takes() query functions: 
int max_len;
int taken[MAXN+2];

int smallest_len_such_that_slast_for_len_greater_than_val_of(int i, int val[]) {
  int left = 0;
  int right = max_len+1;
  while(slast_for_len[left] < val[i]) {
    assert(left <= right);
    assert(slast_for_len[right] > val[i]);
    int mid = (left+right)/2;
    if(slast_for_len[mid] > val[i])
      right = mid;
    else
      left = mid+1;
  }
  return left;
}

void compute(int n, int *s) {
    int val[n+2];
    for(int i = 0; i < n; i++) val[i+1] = s[i];
    val[n+1] = INT_MAX-1; // append a last element. Now every optimal solution takes the last (dummy) element and len[n+1] will eventullly contain the length of an optimal solution.
    val[0] = INT_MIN; // append a first element. This will also belong to every optimal solution and acts as sentinel for the binary searches.

    len[0] = 1; // the maximum subsequence ending with the first element (element 0) has length 1
    max_len = 1; // at least 1
    slast_ele_len[1] = 0; // the current prefix has only the first element, there is only one subsequence of it of length 1, and it takes this first element.
    slast_for_len[1] = val[0];
    for(int i = 1; i <= n+1; i++)
      slast_for_len[i] = INT_MAX;

    for(int i = 1; i <= n+1; i++) {
      int pos_ins = smallest_len_such_that_slast_for_len_greater_than_val_of(i,val); 
	
	// maintain the invariant (defining property of the slast vectors):
	slast_ele_len[pos_ins] = i;
	slast_for_len[pos_ins] = val[i];

        if(pos_ins > max_len)  max_len += 1;
	
	prev[i] = slast_ele_len[pos_ins-1];
        len[i] = len[prev[i]] + 1;
    }

// We can already answer the max_length() query:
    max_len = len[n+1] -2;

// set up the data structure to support the takes() query function: 
    int last_taken = n+1;
    while(last_taken > 0) {
        taken[last_taken] = 1;
        last_taken = prev[last_taken];
    }

}

int max_length() {
    return max_len;
}

int takes(int i) {
    return taken[i+1];
}

int color_of(int i) {
    return 32;
}


