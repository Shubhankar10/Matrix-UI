# Matrix-UI

## TODO
- Make Paid by as a Dict, Agar kuch alag alag transaction hai jo same logo mai split hona hai usse ek mai he daal sake, Compute Allocations mai bas change akr k har ek ko alag alag transacction bana dena hai.


## Templates
### Even Split
```
    {
      "title": "Dinner",
      "amount": 120.0,
      "paid_by": "Alice",
      "even_split": true,
      "checked_names": ["Alice", "Bob", "Charlie"],
      "category": "Food"
    }
```

### Uneven Split

``` 
    {
      "title": "Snacks",
      "amount": 90.0,
      "paid_by": "Bob",
      "even_split": false,
      "checked_names": ["Alice", "Bob", "Charlie"],
      "category": "Food",
      "uneven_split_map": {
        "Alice": 50,
        "Charlie": 20
      }
    }
```