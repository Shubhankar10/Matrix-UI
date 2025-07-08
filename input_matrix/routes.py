from flask import Blueprint, render_template, request
from ops import parse_form, print_split_matrix

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@bp.route("/submit", methods=["POST"])
def submit():
    size, colnames, rows = parse_form(request.form)

    print("=== Submitted Table ===")
    for idx, r in enumerate(rows, start=1):
        print(f"Row {idx}: {r}")
    print("=======================")

    print("=== Settlement Matrix ===")
    print_split_matrix(rows, colnames)
    print("=========================")

    return "<h2>Data received! Check your console.</h2>"
