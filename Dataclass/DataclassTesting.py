from splitDataclass import get_matrix


input_json = {
  "name_count": 4,
  "names": ["Alice", "Bob", "Charlie", "David"],
  "transactions": [
    {
      "title": "Dinner",
      "amount": 200.0,
      "paid_by": "Alice",
      "even_split": True,
      "checked_names": ["Alice", "Bob", "Charlie", "David"],
      "category": "Food"
    },
    {
      "title": "Taxi",
      "amount": 80.0,
      "paid_by": "Bob",
      "even_split": False,
      "checked_names": ["Alice", "Bob"],
      "detail_map": {
        "Alice": 50
      },
      "category": "Transport"
    },
    {
      "title": "Movie Tickets",
      "amount": 120.0,
      "paid_by": "Charlie",
      "even_split": True,
      "checked_names": ["Bob", "Charlie"],
      "category": "Entertainment"
    },
    {
      "title": "Coffee",
      "amount": 40.0,
      "paid_by": "David",
      "even_split": False,
      "checked_names": ["Alice"],
      "detail_map": {
        "Alice": 40
      },
      "category": "Food"
    },
    {
      "title": "Lunch",
      "amount": 160.0,
      "paid_by": "Bob",
      "even_split": True,
      "checked_names": ["Alice", "Charlie", "David"],
      "category": "Food"
    }
  ],
  "metadata": {
    "split_name": "Weekend Trip"
  }
}

mat,lab = get_matrix(input_json)

print("Matrix:")
print(mat)
print("\nLabels:" + ", ".join(lab))