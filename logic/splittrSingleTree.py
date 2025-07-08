import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def build_graph(matrix, labels):
    G = nx.DiGraph()
    size = len(matrix)
    for i in range(size):
        for j in range(size):
            if matrix[i][j] != 0:
                G.add_edge(labels[i], labels[j], weight=matrix[i][j])
    return G

def print_graph(matrix, labels, title="Graph"):
    G = build_graph(matrix, labels)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    edge_labels = {(labels[i], labels[j]): matrix[i][j] for i in range(len(matrix)) for j in range(len(matrix)) if matrix[i][j] != 0}
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_weight='bold', arrowsize=20, connectionstyle='arc3, rad=0.2')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', label_pos=0.6, bbox=dict(facecolor='white', edgecolor='none', pad=1))
    plt.title(title)
    plt.show()

def print_summary(matrix, labels):
    row_sum = np.sum(matrix, axis=1)
    col_sum = np.sum(matrix, axis=0)
    net = col_sum - row_sum
    print(f"{'TO GIVE':<20}{'TO GET':<20}{'NET'}")
    for i, label in enumerate(labels):
        print(f"{label:<10}{row_sum[i]:<10.0f}{label:<10}{col_sum[i]:<10.0f}{net[i]:+.0f}")
    return net

def print_matrix(matrix, labels, step_name):
    print(f"\n=== {step_name} ===")
    print("\t" + "\t".join(labels))
    for i, row in enumerate(matrix):
        print(f"{labels[i]}\t" + "\t".join(str(int(x)) if x != 0 else "-" for x in row))
    print_summary(matrix, labels)
    print_graph(matrix, labels, title=step_name)

def remove_self_loops(matrix):
    mat = matrix.copy()
    np.fill_diagonal(mat, 0)
    return mat

def reduce_bidirectional(matrix):
    mat = matrix.copy()
    size = len(mat)
    for i in range(size):
        for j in range(i + 1, size):
            a, b = mat[i][j], mat[j][i]
            if a and b:
                if a > b:
                    mat[i][j] = a - b
                    mat[j][i] = 0
                else:
                    mat[j][i] = b - a
                    mat[i][j] = 0
    return mat

def settle_on_tree(matrix, labels):
    net = np.sum(matrix, axis=1) - np.sum(matrix, axis=0)
    net_map = {i: net[i] for i in range(len(net)) if net[i] != 0}
    nodes = list(net_map.keys())

    # Build undirected tree (chain for simplicity)
    edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    tree = nx.Graph()
    tree.add_edges_from(edges)

    # Direct the tree arbitrarily from first node
    root = nodes[0]
    directed_tree = nx.DiGraph()
    visited = set()

    def dfs(u):
        visited.add(u)
        for v in tree.neighbors(u):
            if v not in visited:
                directed_tree.add_edge(u, v)
                dfs(v)
    dfs(root)

    # Push flows from leaves to root
    flow_mat = np.zeros_like(matrix)
    net_flow = net.copy()

    def post_order(u):
        for v in list(directed_tree.successors(u)):
            post_order(v)
            if net_flow[v] != 0:
                flow = net_flow[v]
                if flow > 0:
                    flow_mat[v][u] = flow
                else:
                    flow_mat[u][v] = -flow
                net_flow[u] += flow
                net_flow[v] = 0
    post_order(root)
    return flow_mat

def main():
    
    # labels = ['BO', 'Sh', 'Ru', 'Avi']
    # mat = np.array([
    #     [0,   210,  50,  173],
    #     [158,   0,   25,   73],
    #     [143,  120,   0,   40],
    #     [125,    0,   25,    0]
    # ], dtype=float)

    # labels = ["Ru", "Sh", "Bo", "Avi", "Sneha", "Ash"]
    # mat = np.array([
    #     [0,   0,  20,   0,   0,   0],
    #     [153, 0,  70,  20,   0,   0],
    #     [200, 0,   0,   0,   0,   0],
    #     [180, 0,   0,   0,   0, 175],
    #     [103, 200, 0,  40,   0,   0],
    #     [20,  20, 20,   0,   0,   0]
    # ])

    labels = [
        'Shubhankar', 'Bobby', 'Avikalp', 'Ashwini', 'Sneha',
        'Rujhil', 'Vinay', 'Mayuri', 'Shrishti', 'Heeram'
    ]
    mat = np.array([
        [  0,   0,  44,   0,   0,  50,  31,   0,   0,   0],
        [ 90,   0,   0,   0,   0,  50,  31,   0,   0,   0],
        [110,  69,   0,   0,   0,  50,  31,   0,   0,   0],
        [ 90,  89,  44,   0,   0,  50,  31,   0,   0,   0],
        [167,  27,   0,   0,   0,  50,   0,   0,   0,   0],
        [167,   0,  44,   0,   0,   0,  31,   0,   0,   0],
        [ 57,  27,   0,   0,   0,   0,   0,   0,   0,   0],
        [ 90,  89,  44,   0,   0,  50,  31,   0,   0,   0],
        [ 90,  89,  44,   0,   0,  50,  31,   0,   0,   0],
        [ 90, 116,   0,   0,   0,  50,  31,   0,   0,   0]
    ], dtype=float)

    print_matrix(mat, labels, "Original Matrix")

    # Step 1: Remove self-loops
    mat1 = remove_self_loops(mat)
    print_matrix(mat1, labels, "Step 1: Remove Self Loops")

    # Step 2: Reduce bidirectional flows
    mat2 = reduce_bidirectional(mat1)
    print_matrix(mat2, labels, "Step 2: Remove Bidirectional Flows")

    # Step 3: Build tree-based settlement
    mat3 = settle_on_tree(mat2, labels)
    print_matrix(mat3, labels, "Step 3: Tree-based Settlement")

if __name__ == "__main__":
    main()
