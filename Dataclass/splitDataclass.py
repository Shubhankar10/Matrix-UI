from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json
from dataclasses import is_dataclass


@dataclass
class Transaction:
    title: Optional[str] = None
    amount: Optional[float] = None
    paid_by: Optional[str] = None
    even_split: Optional[bool] = None
    checked_names: List[str] = field(default_factory=list)
    category: Optional[str] = None

    # Populated later
    avg: Optional[float] = None
    checked_map: Dict[str, float] = field(default_factory=dict)
    uneven_split_map: Dict[str, float] = field(default_factory=dict)  # For non-even splits


@dataclass
class Participant:
    total_paid: Optional[float] = 0.0
    total_owed: Optional[float] = 0.0
    net_balance: Optional[float] = 0.0
    # transactions: List[Transaction] = field(default_factory=list)
    transactions: List[Dict[str, float]] = field(default_factory=list)
    # each transaction can store { "title": ..., "total_amount": ..., "share": ..., "paid_by": ... }



@dataclass
class MoneySplit:
    name_count: Optional[int] = None
    names: List[str] = field(default_factory=list)
    names_map: Dict[str, Participant] = field(default_factory=dict)
    transactions: List[Transaction] = field(default_factory=list)
    metadata: Dict[str, Optional[str]] = field(default_factory=lambda: {"split_name": None})


def parse_initial_input(input_json: dict) -> MoneySplit:
    print("Parsing initial input...")
    ms = MoneySplit()
    ms.name_count = input_json.get("name_count")
    ms.names = input_json.get("names", [])
    if not ms.names:
        raise ValueError("MoneySplit must have at least one participant.")
    ms.metadata = input_json.get("metadata", {"split_name": None})

    # Initialize transactions
    tx_list = input_json.get("transactions", [])
    for tx in tx_list:
        transaction = Transaction(
            title=tx.get("title"),
            amount=tx.get("amount"),
            paid_by=tx.get("paid_by"),
            even_split=tx.get("even_split"),
            checked_names=tx.get("checked_names", []),
            category=tx.get("category"),
            uneven_split_map=tx.get("uneven_split_map", {})  # Non-even split amounts
        )
        ms.transactions.append(transaction)

    if not ms.transactions:
        raise ValueError("At least one transaction must be provided!")

    # Initialize empty participants map
    for name in ms.names:
        ms.names_map[name] = Participant()

    # print("Initial MoneySplit object created:")
    # print(json.dumps(asdict(ms), indent=2))
    return ms


def compute_allocations(ms):
    """
    Combined, robust compute_allocations function.

    - Accepts a MoneySplit dataclass (ms).
    - Handles transactions as either dicts or dataclass Transaction objects.
    - Fills/computes for each transaction:
        - checked_map (per-transaction mapping participant -> amount)
        - avg (per-transaction average for unspecified participants)
    - Updates per-participant:
        - total_paid
        - total_owed
        - net_balance
        - transactions (list of simplified dicts: title, total_amount, share, paid_by)
    - Prints progress and final summary.
    - Returns the updated MoneySplit instance.
    """
    print("Computing allocations...")

    # reset participant totals and transactions to ensure idempotency
    for pname, p in ms.names_map.items():
        p.total_paid = 0.0
        p.total_owed = 0.0
        p.net_balance = 0.0
        p.transactions = []

    for raw_tx in ms.transactions:
        # Normalize read access for both dict and dataclass transaction representations
        if isinstance(raw_tx, dict):
            title = raw_tx.get("title")
            # support either "total_amount" or "amount"
            total_amount = raw_tx.get("total_amount", raw_tx.get("amount"))
            paid_by = raw_tx.get("paid_by")
            checked_names = raw_tx.get("checked_names", []) or []
            even_split = raw_tx.get("even_split", raw_tx.get("toggle", True))
            # support both "detail_map" and "uneven_split_map" naming
            detail_map = raw_tx.get("detail_map", raw_tx.get("uneven_split_map", {})) or {}
        else:
            # dataclass Transaction object
            title = getattr(raw_tx, "title", None)
            total_amount = getattr(raw_tx, "amount", None)
            paid_by = getattr(raw_tx, "paid_by", None)
            checked_names = getattr(raw_tx, "checked_names", []) or []
            even_split = getattr(raw_tx, "even_split", getattr(raw_tx, "toggle", True))
            detail_map = getattr(raw_tx, "detail_map", getattr(raw_tx, "uneven_split_map", {})) or {}

        # Basic validation: skip if missing crucial data
        if not checked_names or total_amount is None or paid_by is None:
            print(f"Skipping transaction '{title}' because of missing fields.")
            # still ensure transaction has checked_map / avg fields set to defaults
            if isinstance(raw_tx, dict):
                raw_tx.setdefault("checked_map", {})
                raw_tx.setdefault("avg", None)
            else:
                raw_tx.checked_map = getattr(raw_tx, "checked_map", {})
                raw_tx.avg = getattr(raw_tx, "avg", None)
            continue

        # Only proceed if payer exists in names_map (otherwise skip)
        if paid_by not in ms.names_map:
            print(f"Skipping transaction '{title}': payer '{paid_by}' not in participants.")
            if isinstance(raw_tx, dict):
                raw_tx.setdefault("checked_map", {})
                raw_tx.setdefault("avg", None)
            else:
                raw_tx.checked_map = getattr(raw_tx, "checked_map", {})
                raw_tx.avg = getattr(raw_tx, "avg", None)
            continue

        # Compute checked_map and avg depending on even_split value
        checked_map = {}
        avg_unspecified = None

        if even_split:
            # equal division among all checked participants
            share = total_amount / len(checked_names) if len(checked_names) > 0 else 0.0
            for n in checked_names:
                checked_map[n] = share
            avg_unspecified = share
        else:
            # Non-even split:
            total_specified = sum(detail_map.values()) if detail_map else 0.0
            unspecified_names = [n for n in checked_names if n not in detail_map]
            unspecified_count = len(unspecified_names)

            if unspecified_count > 0:
                avg_unspecified = (total_amount - total_specified) / unspecified_count
            else:
                # If everything specified, avg_unspecified is 0
                avg_unspecified = 0.0

            for n in checked_names:
                if n in detail_map:
                    checked_map[n] = detail_map[n]
                else:
                    checked_map[n] = avg_unspecified

        # Store computed checked_map and avg back into transaction (preserve type)
        if isinstance(raw_tx, dict):
            raw_tx["checked_map"] = checked_map
            raw_tx["avg"] = avg_unspecified
        else:
            raw_tx.checked_map = checked_map
            raw_tx.avg = avg_unspecified

        # Update participants: total_owed and append simplified transaction entries
        for name, amt in checked_map.items():
            participant = ms.names_map.get(name)
            if participant is None:
                # Skip unknown participant names
                continue
            # ensure numeric
            participant.total_owed = (participant.total_owed or 0.0) + float(amt)
            # append simplified transaction record
            participant.transactions.append({
                "title": title,
                "total_amount": float(total_amount),
                "share": float(amt),
                "paid_by": paid_by
            })

        # Update payer's total_paid
        payer_participant = ms.names_map.get(paid_by)
        payer_participant.total_paid = (payer_participant.total_paid or 0.0) + float(total_amount)

        print(f"Processed transaction '{title}': paid_by={paid_by}, total_amount={total_amount}")
        for n in checked_names:
            print(f"  {n} -> {checked_map.get(n, 0.0):.2f}")

    # After processing all transactions compute net balances
    for pname, participant in ms.names_map.items():
        participant.net_balance = (participant.total_paid or 0.0) - (participant.total_owed or 0.0)

    # Final structured print for verification (convert dataclass to dict safely)
    try:
        ms_dict = asdict(ms) if is_dataclass(ms) else ms
    except Exception:
        # fallback safe conversion
        ms_dict = {}
        ms_dict["names"] = ms.names
        ms_dict["names_map"] = {
            k: {
                "total_paid": v.total_paid,
                "total_owed": v.total_owed,
                "net_balance": v.net_balance,
                "transactions": v.transactions
            } for k, v in ms.names_map.items()
        }
        ms_dict["transactions"] = []
        for tx in ms.transactions:
            if isinstance(tx, dict):
                ms_dict["transactions"].append(tx)
            else:
                # convert dataclass txn -> dict
                tx_dict = {
                    "title": getattr(tx, "title", None),
                    "amount": getattr(tx, "amount", None),
                    "paid_by": getattr(tx, "paid_by", None),
                    "checked_names": getattr(tx, "checked_names", []),
                    "even_split": getattr(tx, "even_split", True),
                    "detail_map": getattr(tx, "detail_map", {}),
                    "checked_map": getattr(tx, "checked_map", {}),
                    "avg": getattr(tx, "avg", None),
                }
                ms_dict["transactions"].append(tx_dict)

    # print("Computed MoneySplit object:")
    # print(json.dumps(ms_dict, indent=2))

    return ms


def print_settlement_matrix(ms: MoneySplit):
    print("Matrix.")

    colnames = ms.names
    name_to_idx = {name: i for i, name in enumerate(colnames)}
    n = len(colnames)

    # Initialize empty matrix
    matrix = [[0.0] * n for _ in range(n)]

    # Fill the matrix based on transactions
    for tx in ms.transactions:
        payer = tx.paid_by
        if payer not in name_to_idx:
            continue
        pc = name_to_idx[payer]

        for owe_name, amt in tx.checked_map.items():
            if owe_name not in name_to_idx:
                continue
            orow = name_to_idx[owe_name]
            if orow == pc:  # Skip self-pay
                continue
            matrix[orow][pc] += amt

    # Print matrix header
    header = ["Send To"] + colnames
    print("\t".join(header))
    
    # Print each row
    for i, row_name in enumerate(colnames):
        row_values = [f"{matrix[i][j]:.2f}" for j in range(n)]
        print(f"{row_name}\t" + "\t".join(row_values))

    return matrix,name_to_idx


def print_split_summary(ms):
    """Pretty-print a MoneySplit dataclass in a structured way, safely handling nested dataclasses."""
    if not is_dataclass(ms):
        print("Error: input is not a dataclass instance.")
        return

    print("\n========== MONEY SPLIT SUMMARY ==========")
    print(f"Split Name : {ms.metadata.get('split_name', 'N/A')}")
    print(f"Participants ({ms.name_count}): {', '.join(ms.names)}\n")

    print("---- Participant Details ----")
    for name, p in ms.names_map.items():
        print(f"{name}:")
        print(f"  Total Paid : {p.total_paid}")
        print(f"  Total Owed : {p.total_owed}")
        print(f"  Net Balance: {p.net_balance}")
        if p.transactions:
            print("  Transactions:")
            for t in p.transactions:
                # Convert nested dataclasses safely
                if is_dataclass(t):
                    t = asdict(t)
                print(f"    - {t.get('title', '')} | Paid by: {t.get('paid_by', '')} "
                      f"| Share: {t.get('share', '')} | Total: {t.get('total_amount', '')}")
        else:
            print("  Transactions: None")
        print()

    print("---- Global Transactions ----")
    for tx in ms.transactions:
        # Safely handle dataclass or dict
        if is_dataclass(tx):
            tx = asdict(tx)
        print(json.dumps(tx, indent=4))
    print("==========================================\n")

def get_matrix(input_data: dict) -> List[List[float]]:
    ms = parse_initial_input(input_data)

    updated_ms = compute_allocations(ms)
    # print(updated_ms)
    # print()
    print_split_summary(updated_ms)
    matrix = print_settlement_matrix(updated_ms)
    return matrix


if __name__ == "__main__":
    input_even = {
        "name_count": 3,
        "names": ["Alice", "Bob", "Charlie"],
        "transactions": [
            {
                "title": "Dinner",
                "amount": 120.0,
                "paid_by": "Alice",
                "even_split": True,
                "checked_names": ["Alice", "Bob", "Charlie"],
                "category": "Food"
            },
            {
                "title": "Snacks",
                "amount": 260,
                "paid_by": "Alice",
                "even_split": False,
                "checked_names": ["Alice", "Bob", "Charlie"],
                "category": "Food",
                "uneven_split_map": {
                    "Alice": 60,
                }
            }
        ],
        "metadata": {"split_name": "Weekend Trip"}
    }


    input_uneven = {
        "name_count": 3,
        "names": ["Alice", "Bob", "Charlie"],
        "transactions": [
            {
                "title": "Snacks",
                "amount": 260,
                "paid_by": "Alice",
                "even_split": False,
                "checked_names": ["Alice", "Bob", "Charlie"],
                "category": "Food",
                "uneven_split_map": {
                    "Alice": 60,
                }
            }
        ],
        "metadata": {"split_name": "Weekend Trip"}
    }


    
    print("\n--- EVEN SPLIT ---")
    get_matrix(input_even)  # Example call
    print("\n--- NON-EVEN SPLIT ---")
    # get_matrix(input_uneven)  # Example call