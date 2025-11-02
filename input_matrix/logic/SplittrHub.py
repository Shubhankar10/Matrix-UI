import numpy as np
import networkx as nx
from copy import deepcopy

# Utility to pretty-print adjacency matrix with labels
# Calls summary printer at the end
def print_matrix(mat, labels):
    print("Current adjacency matrix:")
    header = "    " + "  ".join(f"{lbl:>4}" for lbl in labels)
    print(header)
    for i, lbl in enumerate(labels):
        row = "  ".join(f"{mat[i, j]:4.0f}" if mat[i, j] != 0 else "   -" for j in range(mat.shape[1]))
        print(f"{lbl:>4}  {row}")
    print()
    print_summary(mat, labels)

# Utility to compute and print row sums (To Give), column sums (To Get), and net difference
# Net = To Get - To Give
def print_summary(mat, labels):
    print("Summary (To Give | To Get | Net):")
    print(f"{'':>4}  {'To Give':>8}  {'To Get':>8}  {'Net':>8}")
    row_sums = mat.sum(axis=1)
    col_sums = mat.sum(axis=0)
    for i, lbl in enumerate(labels):
        to_give = row_sums[i]
        to_get = col_sums[i]
        net = to_get - to_give
        print(f"{lbl:>4}  {to_give:8.0f}  {to_get:8.0f}  {net:8.0f}")
    print()

# Utility to build a directed graph from a matrix
def build_graph(mat, labels):
    G = nx.DiGraph()
    G.add_nodes_from(labels)
    for i, u in enumerate(labels):
        for j, v in enumerate(labels):
            w = mat[i, j]
            if w > 0:
                G.add_edge(u, v, weight=w)
    return G

# Utility to draw the directed graph with curved edges and labels above edges
# Uses matplotlib and networkx

def print_graph(G):
    import matplotlib.pyplot as plt
    # Compute layout
    pos = nx.spring_layout(G)
    plt.figure(figsize=(6, 6))
    # Draw nodes and labels
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_labels(G, pos)
    # Draw curved edges
    nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle='->',
        arrowsize=20,
        connectionstyle='arc3, rad=0.2',
        edge_color='black'
    )
    # Draw edge labels above edges
    edge_labels = {(u, v): f"{data['weight']:.0f}" for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        label_pos=0.5,
        rotate=False,
        font_size=10,
        bbox=dict(facecolor='white', edgecolor='none', pad=0.3)
    )
    plt.title("Current graph")
    plt.axis('off')
    plt.show()

# Main reduction routine
def reduce_to_tree(mat, labels):
    """Perform reduction: remove self-loops, cancel bidirectional arcs, then remove cycles."""
    M = deepcopy(mat)
    step = 1

    # Step 1: Remove self-loops
    print(f"Step {step}: Remove self-loops")
    for i in range(len(labels)):
        if M[i, i] != 0:
            print(f"  Removing self-loop at {labels[i]} of weight {M[i, i]}")
        M[i, i] = 0
    G = build_graph(M, labels)
    print_matrix(M, labels)
    print_graph(G)
    step += 1

    # Step 2: Cancel two-way flows
    print(f"Step {step}: Cancel bidirectional flows")
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            a_ij = M[i, j]
            a_ji = M[j, i]
            if a_ij > 0 and a_ji > 0:
                delta = min(a_ij, a_ji)
                if a_ij > a_ji:
                    M[i, j] -= delta
                    M[j, i] = 0
                    print(f"  Between {labels[i]}<->{labels[j]}, cancel {delta} & net {M[i,j]}")
                else:
                    M[j, i] -= delta
                    M[i, j] = 0
                    print(f"  Between {labels[i]}<->{labels[j]}, cancel {delta} & net {M[j,i]}")
    G = build_graph(M, labels)
    print_matrix(M, labels)
    print_graph(G)
    step += 1

        # Step 3: Hub-based settlement to minimize edges
    print(f"Step {step}: Hub-based settlement")
    # Compute net for each node: To Get - To Give
    row_sums = M.sum(axis=1)
    col_sums = M.sum(axis=0)
    nets = col_sums - row_sums
    # Select hub as node with maximum absolute net
    hub_idx = int(np.argmax(np.abs(nets)))
    hub = labels[hub_idx]
    print(f"  Selected hub node: {hub} (net = {nets[hub_idx]:.0f})")
    # Build new matrix with only hub-based transfers
    M_new = np.zeros_like(M)
    for i, lbl in enumerate(labels):
        if i == hub_idx:
            continue
        amount = nets[i]
        if amount > 0:
            # hub sends to node to satisfy its positive net (node receives)
            print(f"    {hub} -> {lbl} : {amount:.0f}")
            M_new[hub_idx, i] = amount
        elif amount < 0:
            # node sends to hub to satisfy its negative net
            print(f"    {lbl} -> {hub} : {abs(amount):.0f}")
            M_new[i, hub_idx] = abs(amount)
    M = M_new
    G = build_graph(M, labels)
    print_matrix(M, labels)
    print_graph(G)
    return M

# Example usage
def main():
    # labels = ['BO', 'Sh', 'Ru', 'Avi']
    # mat = np.array([
    #     [0,   210,  50,  173],
    #     [158,   0,   25,   73],
    #     [143,  120,   0,   40],
    #     [125,    0,   25,    0]
    # ], dtype=float)

    # labels = ['Ru', 'Sh', 'Bo', 'Avi', 'Sneha', 'Ash']
    # mat = np.array([
    #     [  0,   0,  20,   0,   0,   0],
    #     [153,   0,  70,  20,   0,   0],
    #     [200,   0,   0,   0,   0,   0],
    #     [180,   0,   0,   0,   0, 175],
    #     [103, 200,   0,  40,   0,   0],
    #     [ 20,  20,  20,   0,   0,   0]
    # ], dtype=float)


    lables = [
        'Rujhil',	'Jay',	'Bobby',	'Avikalp',	'Sneha',	'Ashwini'
    ]
    mat = np.array([
    [  0.,  90.,  52.,   0.,   0.,   0.],
    [  0., 154., 135.,   0.,   0.,   0.],
    [  0.,  94., 235.,   0.,   0.,   0.],
    [  0.,  44., 219.,  16.,   0.,   0.],
    [  0.,  94., 166.,  16.,   0.,   0.],
    [  0.,  74.,  50.,  16.,   0.,   0.]], dtype=float)

    print("Original matrix and graph:")
    print_matrix(mat, labels)
    print_graph(build_graph(mat, labels))

    final = reduce_to_tree(mat, labels)
    print("Final reduced (tree) matrix:")
    print_matrix(final, labels)

if __name__ == '__main__':
    main()
