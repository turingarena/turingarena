import java.util.*;

class Solution extends Skeleton {

    class Edge implements Comparable {
        public int to;
        public int weight;

        Edge(int to, int weight) {
            this.to = to; 
            this.weight = weight;
        }

        public int compareTo(Object other) {
            Edge o = (Edge) other;
            return o.weight - this.weight;
        }
    }

    List[] adj; 
    boolean initialized = false; 

    Solution() {
        // init adj
        adj = new List[N];
        for (int i = 0; i < N; i++) {
            adj[i] = new ArrayList<Edge>();
        }
    }

    int dijkstra(int from, int to) {
        PriorityQueue<Edge> Q = new PriorityQueue<>();
        int d[] = new int[N];

        // initialize d to infinite 
        for (int i = 0; i < N; i++) {
            d[i] = Integer.MAX_VALUE;
        }

        d[from] = 0;
        Q.add(new Edge(from, 0));

        while (!Q.isEmpty()) {
            int u = Q.poll().to;
            
            for (Edge e : (List<Edge>) adj[u]) {
                int v = e.to;
                int w = e.weight;
                
                if (d[v] > d[u] + w) {
                    d[v] = d[u] + w;
                    Q.add(new Edge(v, d[v]));
                }
            }
        }

        return d[to];
    }

    void add_edge(int from, int to, int weight) {
        System.err.println("Add edge " + from + " <-> " + to + " weight " + weight);
        adj[from].add(new Edge(to, weight));
        adj[to].add(new Edge(from, weight));
    }
 
    int shortest_path(int from, int to) {
        int res = dijkstra(from, to);
        if (res == Integer.MAX_VALUE) 
            res = -1;
        System.err.println("Shortest path " + from + " -> " + to + " = " + res);
        return res;
    }
}