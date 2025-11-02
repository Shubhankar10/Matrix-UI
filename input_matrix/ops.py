def parse_form(form):
    size = int(form["size"])
    row_count = int(form["row_count"])
    colnames = [form.get(f"colname_{j}", "") for j in range(1, size + 1)]

    rows = []
    for i in range(1, row_count + 1):
        title = form.get(f"title_{i}", "")
        amount = float(form.get(f"amount_{i}", 0))
        paid_by = form.get(f"paidby_{i}", "")
        toggle = form.get(f"toggle_{i}") == "on"

        checked_names = [
            cname for j, cname in enumerate(colnames, start=1)
            if form.get(f"chk_{i}_{j}") == "on"
        ]

        detail_map = {}
        for j, cname in enumerate(colnames, start=1):
            val = form.get(f"detail_{i}_{j}")
            if val:
                try:
                    detail_map[cname] = float(val)
                except ValueError:
                    pass
        print("Detail Map:", detail_map)

        total_specified = sum(detail_map.values())
        unspecified_count = len(checked_names) - len(detail_map)

        avg = (
            (amount - total_specified) / unspecified_count
            if toggle and unspecified_count > 0
            else (amount / len(checked_names) if checked_names else 0)
        )

        checked_map = {}
        if toggle:
            for name in checked_names:
                checked_map[name] = detail_map[name] if name in detail_map else avg
        else:
            for name in checked_names:
                checked_map[name] = avg

        rows.append({
            "title":         title,
            "amount":        amount,
            "paid_by":       paid_by,
            "toggle":        toggle,
            "checked_names": checked_names,
            "avg":           avg,
            "checked_map":   checked_map
        })

    return size, colnames, rows


def print_split_matrix(rows, colnames):
    n = len(colnames)
    name_to_idx = {name: i for i, name in enumerate(colnames)}
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for entry in rows:
        payer = entry["paid_by"]
        if payer not in name_to_idx:
            continue
        payer_col = name_to_idx[payer]

        for owe_name, amt in entry["checked_map"].items():
            if owe_name not in name_to_idx:
                continue
            owe_row = name_to_idx[owe_name]

            if owe_row == payer_col:
                continue

            matrix[owe_row][payer_col] += amt

    header = ["{:>12}".format("")] + [f"{name:>12}" for name in colnames]
    print("".join(header))
    for i, row_name in enumerate(colnames):
        line = [f"{row_name:>12}"] + [f"{matrix[i][j]:>12.2f}" for j in range(n)]
        print("".join(line))

    return matrix
