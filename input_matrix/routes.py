# routes.py
from flask import Blueprint, render_template, request
from ops import parse_form

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@bp.route("/matrix", methods=["POST"])
def matrix_view():
    # Parse form data into rows and column names
    size, colnames, rows = parse_form(request.form)
    print("Parsed Rows:")   
    for r in rows:
        print(r)
    # Compute the settlement matrix
    name_to_idx = {name: i for i, name in enumerate(colnames)}
    n = len(colnames)
    matrix = [[0.0] * n for _ in range(n)]
    for entry in rows:
        payer = entry["paid_by"]
        if payer not in name_to_idx:
            continue
        pc = name_to_idx[payer]
        for owe_name, amt in entry["checked_map"].items():
            if owe_name not in name_to_idx:
                continue
            orow = name_to_idx[owe_name]
            if orow == pc:
                continue
            matrix[orow][pc] += amt
    print("Name to Index Mapping:")
    print(name_to_idx)

    # Render the matrix template
    print(matrix)
    return render_template(
        "matrix.html",
        colnames=colnames,
        matrix=matrix
    )