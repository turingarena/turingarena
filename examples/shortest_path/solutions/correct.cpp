#include <vector>
#include <queue>
#include <climits>

using namespace std;

int N; // number of nodes
int E; // number of edges
int Q; // number of queries

vector<pair<int, int> > adj[10000];

int dijkstra(int source, int destination) {

    priority_queue<pair<int, int> > Q;
    vector<int> dist(N, INT_MAX); // set initial distance to infinity

    dist[source] = 0; // dist source to itself = 0
    Q.push(make_pair(0, source)); // put source in the queue

    while (!Q.empty()) {
        int u = Q.top().second; // node with shortest distance from source
        Q.pop();

        for (auto e : adj[u]) {
            int v = e.first;
            int w = e.second;

            if (dist[v] > dist[u] + w) { // if it costs less to go to v trough u
                dist[v] = dist[u] + w;   // update v distance
                Q.push(make_pair(dist[v], v)); // put v in queue
            }
        }
    }

    return dist[destination];
}

void add_edge(int u, int v, int w) {
    adj[u].push_back(make_pair(v, w));
    adj[v].push_back(make_pair(u, w));
}

int shortest_path(int u, int v) {
    int dist = dijkstra(u, v);
    if (dist == INT_MAX)
        return -1;
    else
        return dist;
}
