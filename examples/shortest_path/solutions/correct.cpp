#include <vector>
#include <queue>
#include <climits>

using namespace std;

int N; // number of nodes
int* D; // node degree
int** A; // adjacency
int** W; // weights

void init(int _N, int _Q, int _D, int _A, int _W) {
    N = _N;
    D = _D;
    A = _A;
    W = _W;
}

int dijkstra(int source, int destination) {
    priority_queue<pair<int, int> > Q;
    vector<int> dist(N, INT_MAX); // set initial distance to infinity

    dist[source] = 0; // dist source to itself = 0
    Q.push(make_pair(0, source)); // put source in the queue

    while (!Q.empty()) {
        int u = Q.top().second; // node with shortest distance from source
        Q.pop();

        for (int i = 0; i < D[u]; i++) {
            int v = A[u][i];
            int w = W[u][i];

            if (dist[v] > dist[u] + w) { // if it costs less to go to v trough u
                dist[v] = dist[u] + w;   // update v distance
                Q.push(make_pair(dist[v], v)); // put v in queue
            }
        }
    }

    return dist[destination];
}


int shortest_path(int u, int v) {
    int dist = dijkstra(u, v);
    if (dist == INT_MAX)
        return -1;
    else
        return dist;
}
