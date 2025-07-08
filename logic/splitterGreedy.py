import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def build_graph(matrix, labels):
    """Build a directed graph from adjacency matrix."""
    G = nx.DiGraph()
    G.add_nodes_from(labels)
    for i, u in enumerate(labels):
        for j, v in enumerate(labels):
            w = matrix[i, j]
            if w != 0:
                G.add_edge(u, v, weight=w)
    return G

def print_graph(matrix, labels, title):
    """Draw the directed graph with curved edges and weights."""
    G = build_graph(matrix, labels)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6, 6))
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle='->', arrowsize=20,
        connectionstyle='arc3, rad=0.2'
    )
    edge_labels = {(u, v): f"{data['weight']:.0f}"
                   for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels,
        font_size=10, rotate=False,
        bbox=dict(facecolor='white', edgecolor='none', pad=0.3)
    )
    plt.title(title)
    plt.axis('off')
    # plt.show()

def print_summary(matrix, labels):
    """Print To Give, To Get, and Net for each node."""
    to_give = matrix.sum(axis=1)   # outgoing
    to_get  = matrix.sum(axis=0)   # incoming
    net     = to_get - to_give
    print(f"{'Node':<12}{'To Give':>8}{'To Get':>10}{'Net':>10}")
    for lbl, give, get, n in zip(labels, to_give, to_get, net):
        print(f"{lbl:<12}{give:8.0f}{get:10.0f}{n:10.0f}")
    print()
    return net

def print_matrix(matrix, labels, step_name):
    """Print the adjacency matrix, summary and graph."""
    print(f"\n=== {step_name} ===")
    header = "\t" + "\t".join(labels)
    print(header)
    for lbl, row in zip(labels, matrix):
        row_str = "\t".join(str(int(x)) if x != 0 else "-" for x in row)
        print(f"{lbl}\t{row_str}")
    print()
    net = print_summary(matrix, labels)
    print_graph(matrix, labels, step_name)
    return net

def remove_self_loops(matrix):
    """Zero out diagonal entries."""
    M = matrix.copy()
    np.fill_diagonal(M, 0)
    return M

def reduce_bidirectional(matrix,labels):
    """Cancel out two-way flows by netting them."""
    M = matrix.copy()
    n = M.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            a, b = M[i,j], M[j,i]
            if a and b:
                delta = min(a, b)
                print(f"Cancelling {delta:.0f} between {labels[i]}↔{labels[j]}")
                if a > b:
                    M[i,j] -= delta
                    M[j,i]  = 0
                else:
                    M[j,i] -= delta
                    M[i,j]  = 0
    return M

def settle_greedy(matrix, labels):
    """
    Greedy settlement:
      - Compute net balances (incoming minus outgoing).
      - While creditors and debtors remain, match the largest of each.
      - Transfer min(amount_owed, amount_due) from debtor → creditor.
    """
    M = np.zeros_like(matrix)
    net = matrix.sum(axis=0) - matrix.sum(axis=1)
    # Build lists of (idx, balance)
    creditors = [(i, net[i]) for i in range(len(net)) if net[i] > 0]
    debtors   = [(i, -net[i]) for i in range(len(net)) if net[i] < 0]
    # Sort descending by amount
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    step = 1
    while creditors and debtors:
        c_idx, c_amt = creditors[0]
        d_idx, d_amt = debtors[0]
        transfer = min(c_amt, d_amt)
        print(f"Step {step}: {labels[d_idx]} pays {labels[c_idx]} → {transfer:.0f}")
        M[d_idx, c_idx] += transfer

        # Update balances
        c_amt -= transfer
        d_amt -= transfer

        # Pop or update creditor
        if c_amt == 0:
            creditors.pop(0)
        else:
            creditors[0] = (c_idx, c_amt)
        # Pop or update debtor
        if d_amt == 0:
            debtors.pop(0)
        else:
            debtors[0] = (d_idx, d_amt)

        step += 1

    return M

def main():
    lab = [
        'Rujhil',	'Jay',	'Bobby',	'Avikalp',	'Sneha',	'Ashwini'
    ]
    mat = np.array([
    [  0.,  90.,  52.,   0.,   0.,   0.],
    [  0., 154., 135.,   0.,   0.,   0.],
    [  0.,  94., 235.,   0.,   0.,   0.],
    [  0.,  44., 219.,  16.,   0.,   0.],
    [  0.,  94., 166.,  16.,   0.,   0.],
    [  0.,  74.,  50.,  16.,   0.,   0.]], dtype=float)


    # Original
    net0 = print_matrix(mat, lab, "Original Matrix")

    # Step 1: remove self loops
    mat1 = remove_self_loops(mat)
    _ = print_matrix(mat1, lab, "Step 1: Remove Self-Loops")

    # Step 2: cancel bidirectional flows
    mat2 = reduce_bidirectional(mat1,lab)
    _ = print_matrix(mat2, lab, "Step 2: Cancel Bidirectional Flows")

    # Step 3: greedy settlement
    mat3 = settle_greedy(mat2, lab)
    _ = print_matrix(mat3, lab, "Step 3: Greedy Recursive Settlement")

    return 0

    # labels = ['p1','p2','p3']
    # matrix = np.array([
    #     [  10,   15,  1],
    #     [ 10,   0,  500],
    #     [10,  5,   60],
    # ], dtype=float)


    process_matrix(matrix,labels)

def process_matrix(mat, labels):
    print("Got Function")
    print(mat)
    print(labels)

    """Process the input matrix through all steps and return the final settled matrix."""
    print_matrix(mat, labels, "Original Matrix")
    mat1 = remove_self_loops(mat)
    mat2 = reduce_bidirectional(mat1, labels)
    mat3 = settle_greedy(mat2, labels)
    return mat3

def process_matrix(mat, labels):
    """
    Process the input matrix through all steps and
    return a dict of {step_name: matrix}.
    """
    
    print("Got Function")
    print(mat)
    print(labels)

    matrices = {}

    # Original
    matrices['Original Matrix'] = mat.copy()

    # Step 1
    mat1 = remove_self_loops(mat)
    matrices['Step 1: Remove Self-Loops'] = mat1.copy()
    print_matrix(mat1, labels, "Step 1: Remove Self-Loops")

    # Step 2
    mat2 = reduce_bidirectional(mat1, labels)
    matrices['Step 2: Cancel Bidirectional Flows'] = mat2.copy()
    print_matrix(mat2, labels, "Step 2: Cancel Bidirectional Flows")

    # Step 3
    mat3 = settle_greedy(mat2, labels)
    matrices['Final Matrix'] = mat3.copy()
    print_matrix(mat3, labels, "Step 3: Greedy Recursive Settlement")

    print(matrices)
    
    return matrices


if __name__ == "__main__":
    main()
