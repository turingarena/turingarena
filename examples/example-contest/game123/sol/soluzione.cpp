/**
 *  Soluzione di play123
 *
 *  Autore: Romeo Rizzi
 *
 *  Descrizione: Banale
 */
#include <iostream>
using namespace std;


int play(int n) {
  return n % 4;
}

int main() {
  int n;
  cin >> n;
  cout << play(n) << endl;
  return 0;
}

