from flask import Blueprint, render_template, request
import numpy as np
from services.matrix_ops import (
    build_names, build_matrix, process_pipeline
)

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
def index():
    n = 4
    default_names = [f"P{i+1}" for i in range(n)]
    matrix = np.zeros((n, n))
    names  = default_names
    result = None
    sidebar = {}

    if request.method == "POST":
        names   = build_names(request.form, default_names)
        matrix  = build_matrix(request.form, n)
        mats    = process_pipeline(matrix, names)
        result  = mats["Final Matrix"].tolist()
        sidebar = {k: v.tolist() for k, v in mats.items() if k != "Final Matrix"}

    return render_template(
        "index.html",
        n=n,
        matrix=matrix.tolist(),
        names=names,
        result=result,
        sidebar=sidebar
    )
