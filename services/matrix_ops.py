import numpy as np
from logic.splitterGreedy import process_matrix

def build_names(form, default_names):
    """Return list of names from form (or defaults)."""
    return [
        form.get(f"row_name_{i}", default_names[i])
        for i in range(len(default_names))
    ]

def build_matrix(form, n):
    """Return n×n numpy array from form inputs."""
    data = [
        [
            float(form.get(f"cell_{i}_{j}", 0) or 0)
            for j in range(n)
        ]
        for i in range(n)
    ]
    return np.array(data)

def process_pipeline(mat_np, names):
    """
    Your existing `process_matrix` wrapper that returns
    {
      'Step 1': np.array(...),
      ...
      'Final Matrix': np.array(...)
    }
    """
    return process_matrix(mat_np, names)  # imported or defined here
