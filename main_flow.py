from Dataclass.splitDataclass import get_matrix
from logic.split_logics import process_matrix
import json
import numpy as np

# GET JSON DATA
with open('Dataclass\min_transaction.json', 'r') as file:
    data = json.load(file)


# JSON TO MATRIX 
matrix,label = get_matrix(data)

np_matrix = np.array(matrix, dtype=float)
list_label = [name for name, _ in sorted(label.items(), key=lambda x: x[1])]


# REDUCE MATRIX TO SPLIT
process_matrix(np_matrix,list_label)