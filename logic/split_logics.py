import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
PRINT_GRAPH = False

# FOR GRAPH 
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
    G = build_graph(matrix, labels)
    pos = nx.circular_layout(G)  # fixed-radius, evenly spaced around a circle


    plt.figure(figsize=(6, 6))
    nx.draw_networkx_nodes(G, pos, node_size=2500)  # node circles
    nx.draw_networkx_labels(G, pos)
    
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle='->', arrowsize=25,
        connectionstyle='arc3, rad=0.2',
        width=2.5,
        min_target_margin=25         # Adds margin so arrows stop outside the node
    )
    edge_labels = {(u, v): f"{data['weight']:.0f}"
                   for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels,
        font_size=10, rotate=False,
        bbox=dict(facecolor='white', edgecolor='none', pad=0.1)
    )

    plt.title(title)
    plt.axis('off')
    plt.show()


# FOR PRINTS 
def print_balance(matrix, labels):
    to_give = matrix.sum(axis=1)
    to_get  = matrix.sum(axis=0)
    net     = to_get - to_give

    lines = []
    header = f"{'Node':<12}{'To Give':>8}{'To Get':>10}{'Net':>10}"
    lines.append(header)
    # print(header)

    for lbl, give, get, n in zip(labels, to_give, to_get, net):
        line = f"{lbl:<12}{give:8.0f}{get:10.0f}{n:10.0f}"
        lines.append(line)
        # print(line)

    # print()
    lines.append("")
    return lines

def print_matrix(matrix, labels, step_name):
    lines = []

    header = f"\n=== {step_name} ==="
    lines.append(header)
    # print(header)

    col_header = "\t" + "\t".join(labels)
    lines.append(col_header)
    # print(col_header)

    for lbl, row in zip(labels, matrix):
        row_str = "\t".join(str(int(x)) if x != 0 else "-" for x in row)
        line = f"{lbl}\t{row_str}"
        lines.append(line)
        # print(line)

    # print()
    lines.append("")
    # balance_lines = print_balance(matrix, labels)
    # lines.extend(balance_lines)
    return lines

def print_matrix_and_balance_side_by_side(matrix, labels, step_name):
    # Get structured data instead of printing
    matrix_lines = print_matrix(matrix, labels, step_name)
    balance_lines = print_balance(matrix, labels)

    # Format matrix_lines: replace tabs with space-aligned layout
    max_label_len = max(len(lbl) for lbl in labels)
    col_width = 8
    formatted_matrix_lines = []

    for line in matrix_lines:
        if line.startswith("==="):  # step header
            formatted_matrix_lines.append(line)
            continue
        if line.strip() == "":
            formatted_matrix_lines.append("")
            continue
        if line.startswith(" "):  # column header
            cols = line.strip().split()
            formatted_line = " " * (max_label_len + 2) + "".join(col.ljust(col_width) for col in cols)
        else:
            parts = line.split("\t")
            row_label = parts[0]
            values = parts[1:] if len(parts) > 1 else []
            formatted_line = row_label.ljust(max_label_len + 2) + "".join(val.ljust(col_width) for val in values)
        formatted_matrix_lines.append(formatted_line)

    # Pad shorter list
    max_lines = max(len(formatted_matrix_lines), len(balance_lines))
    formatted_matrix_lines += [""] * (max_lines - len(formatted_matrix_lines))
    balance_lines += [""] * (max_lines - len(balance_lines))

    # Final side-by-side print
    gap = " | "
    for m_line, b_line in zip(formatted_matrix_lines, balance_lines):
        print(f"{m_line:<{max_label_len + col_width * len(labels) + 2}}{gap}{b_line}")

def print_settlement_summary(M, labels):
    step = 1
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j] > 0:
                print(f"{step}: {labels[i]} pays {labels[j]} → {M[i, j]:.0f}")
                step += 1
    return step

# LOGIC : GENERAL
def remove_self_loops(matrix):
    M = matrix.copy()
    np.fill_diagonal(M, 0)
    return M

def reduce_bidirectional(matrix,labels):
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


# LOGIC 1 : GREEDY
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
        # print(f"Step {step}: {labels[d_idx]} pays {labels[c_idx]} → {transfer:.0f}")
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


#LOGIC 2 : Hub
def reduce_to_tree(M, labels):
    """
    Reduce a settlement matrix to a minimal tree:
      - Remove self-loops.
      - Cancel bidirectional flows.
      - Convert to hub-based transfers.
    """
    # Step 1: Remove self-loops
    # M = remove_self_loops(matrix)

    # # Step 2: Cancel bidirectional flows
    # M = reduce_bidirectional(M, labels)

    # Step 3: Hub-based reduction
    row_sums = M.sum(axis=1)
    col_sums = M.sum(axis=0)
    nets = col_sums - row_sums

    hub_idx = int(np.argmax(np.abs(nets)))
    M_new = np.zeros_like(M)

    for i in range(len(labels)):
        if i == hub_idx:
            continue
        amount = nets[i]
        if amount > 0:
            M_new[hub_idx, i] = amount
        elif amount < 0:
            M_new[i, hub_idx] = -amount

    return M_new


#LOGIC 3 : Tree
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


def process_matrix(mat, labels):
    
    
    print_matrix_and_balance_side_by_side(mat, labels, "Original Matrix ")
    mat1 = remove_self_loops(mat)   
    if PRINT_GRAPH:
        print_graph(mat1,labels,"Graph")


    print_matrix_and_balance_side_by_side(mat1, labels, "Step 1: Remove Self-Loops ")
    mat2 = reduce_bidirectional(mat1, labels)
    if PRINT_GRAPH:
        print_graph(mat2,labels,"Graph")

    print_matrix_and_balance_side_by_side(mat2, labels, "Step 2: Cancel Bidirectional Flows ")


    # Change funciton based on logic


    # mat3 = reduce_to_tree(mat2,labels)
    # mat3 = settle_on_tree(mat2,labels) #Useless
    mat3 = settle_greedy(mat2, labels)
    print_matrix_and_balance_side_by_side(mat3, labels, "Step 3: Greedy Recursive Settlement ")
    
    print_settlement_summary(mat3, labels)
    if PRINT_GRAPH:
        print_graph(mat3,labels,"Graph")
    return mat3




if __name__ == "__main__":

    lab = [
        'Rujhil', 'Shubhankar', 'Bobby', 'Avikalp',
        'Sneha', 'Ashwini', 'Satyam', 'Yash', 'Neeraj'
    ]

    mat = np.array([
        [  60, 188,  93,   0,   0,   0,   0,   0,   126],
        [ 100,   0,  92,   0,   0,   0,   24,   0,   0],
        [ 100,   0,  92,   0,   0,   0,   24,   0,   0],
        [   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [ 100, 150,  93,   0,   0,   0,   24,   0,   0],
        [ 200,  80,   0,   0,   0,   0,   24,   0,   126],
        [ 100,  60,   0,   0,   0,   0,   24,   0,   0],
        [ 100, 109,   0,   0,   0,   0,   24,   0,   0],
        [ 100,   0,   0,   0,   0,   0,   24,   0,   0]
    ], dtype=float)

    # mat = mat.T

    print(mat)

    process_matrix(mat,lab)

