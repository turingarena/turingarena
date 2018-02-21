#include <iostream>
#include <vector>

using namespace std;

int main() 
{
	/* io test */
	cout << "Hello, world!" << endl; 

	/* small vector (10Mb) */
	vector<char> v(10000);
	for (int i = 0; i < v.size(); i++) 
		v[i] = '0';

	/* big memory allocation test (1Gb) */
	vector<char> v2(1000000);
	for (int i = 0; i < v2.size(); i++) 
		v2[i] = '0';

	/* exit test */
	exit(EXIT_SUCCESS);
}