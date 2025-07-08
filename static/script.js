document.addEventListener("DOMContentLoaded", () => {
  const sizeInput     = document.getElementById("sizeInput");
  const sizeField     = document.getElementById("sizeField");
  const rowCountField = document.getElementById("rowCountField");
  const table         = document.getElementById("dataTable");
  const addRowBtn     = document.getElementById("addRowBtn");
  const addColBtn     = document.getElementById("addColBtn");

  let rowCount = 0;

  sizeInput.addEventListener("change", rebuildTable);
  addRowBtn.addEventListener("click", addRow);
  addColBtn.addEventListener("click", addColumn);

  rebuildTable();

  function rebuildTable() {
    const n = parseInt(sizeInput.value, 10) || 1;
    sizeField.value = n;
    table.innerHTML = "";
    rowCount = 0;
    rowCountField.value = 0;
    buildHeader(n);
    addRow();
  }

  function buildHeader(n) {
    const header = table.insertRow();
    const labels = ["Title", "Amount", "Paid By", "Toggle"]
      .concat(Array(n).fill(null), ["Avg", "Buttons"]);
    labels.forEach((lab, idx) => {
      const th = document.createElement("th");
      if (idx >= 4 && idx < 4 + n) {
        const colIdx = idx - 3;
        const inp = document.createElement("input");
        inp.type = "text";
        inp.name = `colname_${colIdx}`;
        inp.value = `Name ${colIdx}`;
        inp.addEventListener("input", updateAllPaidBys);
        th.appendChild(inp);
      } else {
        th.textContent = lab;
      }
      header.appendChild(th);
    });
  }

  function addRow() {
    const n = parseInt(sizeInput.value, 10) || 1;
    rowCount += 1;
    rowCountField.value = rowCount;

    const i = rowCount;
    const row = table.insertRow();
    row.classList.add("data-row");
    row.dataset.row = i;

    // Title
    let cell = row.insertCell();
    const title = document.createElement("input");
    title.type = "text"; title.name = `title_${i}`; title.required = true;
    cell.appendChild(title);

    // Amount
    cell = row.insertCell();
    const amount = document.createElement("input");
    amount.type = "number"; amount.name = `amount_${i}`;
    amount.min = "0"; amount.step = "any"; amount.value = "0";
    amount.addEventListener("input", () => recalcRow(i));
    cell.appendChild(amount);

    // Paid By
    cell = row.insertCell();
    const paidBy = document.createElement("select");
    paidBy.name = `paidby_${i}`;
    populatePaidByOptions(paidBy);
    cell.appendChild(paidBy);

    // Toggle
    cell = row.insertCell();
    const toggle = document.createElement("input");
    toggle.type = "checkbox"; toggle.name = `toggle_${i}`;
    toggle.addEventListener("change", () => handleToggle(i));
    cell.appendChild(toggle);

    // Checkboxes
    for (let j = 1; j <= n; j++) {
      cell = row.insertCell();
      const chk = document.createElement("input");
      chk.type = "checkbox"; chk.name = `chk_${i}_${j}`;
      chk.addEventListener("change", () => recalcRow(i));
      cell.appendChild(chk);
    }

    // Avg
    cell = row.insertCell();
    const avg = document.createElement("input");
    avg.type = "number"; avg.name = `avg_${i}`;
    avg.readOnly = true; avg.value = "0";
    cell.appendChild(avg);

    // Buttons: All & Clear
    cell = row.insertCell();
    const allBtn = document.createElement("button");
    allBtn.type = "button"; allBtn.textContent = "All";
    allBtn.addEventListener("click", () => {
      clearRow(i, false);
      for (let j = 1; j <= n; j++) {
        document.querySelector(`[name="chk_${i}_${j}"]`).checked = true;
      }
      recalcRow(i);
    });
    cell.appendChild(allBtn);

    const clrBtn = document.createElement("button");
    clrBtn.type = "button"; clrBtn.textContent = "Clear";
    clrBtn.addEventListener("click", () => clearRow(i, true));
    cell.appendChild(clrBtn);
  }

  function addColumn() {
    let n = parseInt(sizeInput.value, 10) || 1;
    n += 1; sizeInput.value = n; sizeField.value = n;

    // Header: before Avg
    const header = table.rows[0];
    const th = document.createElement("th");
    const colIdx = n;
    const inp = document.createElement("input");
    inp.type = "text"; inp.name = `colname_${colIdx}`;
    inp.value = `Name ${colIdx}`; inp.addEventListener("input", updateAllPaidBys);
    th.appendChild(inp);
    header.insertBefore(th, header.cells[header.cells.length - 2]);

    // Each data-row: insert checkbox
    document.querySelectorAll("tr.data-row").forEach(row => {
      const rowIdx = row.dataset.row;
      const td = document.createElement("td");
      const chk = document.createElement("input");
      chk.type = "checkbox"; chk.name = `chk_${rowIdx}_${colIdx}`;
      chk.addEventListener("change", () => recalcRow(rowIdx));
      td.appendChild(chk);
      row.insertBefore(td, row.cells[row.cells.length - 2]);
    });

    // Each detail-row: insert detail input
    document.querySelectorAll("tr.detail-row").forEach(detail => {
      const prevData = detail.previousElementSibling;
      const rowIdx = prevData.dataset.row;
      const td = document.createElement("td");
      const inp = document.createElement("input");
      inp.type = "number"; inp.min = "0"; inp.step = "any";
      inp.name = `detail_${rowIdx}_${n}`;
      inp.addEventListener("input", () => handleDetailInput(rowIdx, n, inp));
      td.appendChild(inp);
      detail.insertBefore(td, detail.cells[detail.cells.length - 2]);
    });

    updateAllPaidBys();
  }

  function clearRow(i, removeDetail) {
    document.querySelectorAll(`[name^="chk_${i}_"]`).forEach(cb => cb.checked = false);
    document.querySelector(`[name="avg_${i}"]`).value = "0";
    const det = document.getElementById(`detail_${i}`);
    if (det) det.remove();
  }

  function getColNames() {
    return Array.from(
      document.querySelectorAll("input[name^='colname_']"),
      inp => inp.value || ""
    );
  }

  function populatePaidByOptions(sel) {
    sel.innerHTML = "";
    getColNames().forEach(name => {
      const opt = document.createElement("option");
      opt.value = name; opt.textContent = name;
      sel.appendChild(opt);
    });
  }

  function updateAllPaidBys() {
    document.querySelectorAll("tr.data-row").forEach(row => {
      const i = row.dataset.row;
      const sel = row.querySelector(`select[name="paidby_${i}"]`);
      if (sel) populatePaidByOptions(sel);
    });
  }

  function handleToggle(rowIndex) {
    const on = document.querySelector(`[name="toggle_${rowIndex}"]`).checked;
    const dataRow = document.querySelector(`tr.data-row[data-row="${rowIndex}"]`);
    const detId   = `detail_${rowIndex}`;

    // always clear first
    clearRow(rowIndex, true);

    if (on) {
      // === UNEQUAL SPLIT: insert detail row with empty inputs ===
      const detail = document.createElement("tr");
      detail.id    = detId;
      detail.classList.add("detail-row");

      // blank under Title, Amount, PaidBy, Toggle
      for (let k = 0; k < 4; k++) detail.insertCell();

      // detail inputs for each checkbox col
      const n = parseInt(sizeInput.value, 10) || 1;
      for (let j = 1; j <= n; j++) {
        const td  = detail.insertCell();
        const inp = document.createElement("input");
        inp.type = "number"; inp.min = "0"; inp.step = "any";
        inp.name = `detail_${rowIndex}_${j}`;
        inp.addEventListener("input", () => handleDetailInput(rowIndex, j, inp));
        td.appendChild(inp);
      }

      // === NEW: Amount‑Left cell under Avg ===
      const leftCell = detail.insertCell();
      leftCell.innerHTML = `<div class="amount-left" id="left_${rowIndex}">
                              Amount left: 0.00
                            </div>`;

      // blank under Buttons
      detail.insertCell();

      dataRow.insertAdjacentElement("afterend", detail);
      recalcRow(rowIndex);
      // === end UNEQUAL SPLIT ===
    }
  }

  function handleDetailInput(rowIndex, colJ, inp) {
    const n      = parseInt(sizeInput.value, 10) || 1;
    const amount = parseFloat(
      document.querySelector(`[name="amount_${rowIndex}"]`).value
    ) || 0;

    // clamp sum(detail) ≤ amount
    let sumOthers = 0;
    for (let k = 1; k <= n; k++) {
      if (k !== colJ) {
        sumOthers += parseFloat(
          document.querySelector(`[name="detail_${rowIndex}_${k}"]`).value || 0
        );
      }
    }
    let val = parseFloat(inp.value) || 0;
    if (sumOthers + val > amount) {
      val = amount - sumOthers;
      inp.value = val.toFixed(2);
    }

    // auto-check box
    document.querySelector(`[name="chk_${rowIndex}_${colJ}"]`).checked = val > 0;
    recalcRow(rowIndex);
  }

  function recalcRow(i) {
    const amount = parseFloat(
      document.querySelector(`[name="amount_${i}"]`).value
    ) || 0;
    const on     = document.querySelector(`[name="toggle_${i}"]`).checked;
    const n      = parseInt(sizeInput.value, 10) || 1;

    // gather checked indices
    const checked = [];
    document.querySelectorAll(`tr.data-row[data-row="${i}"] input[name^="chk_${i}_"]`)
      .forEach(cb => {
        const [, , j] = cb.name.split("_");
        if (cb.checked) checked.push(Number(j));
      });

    let specifiedSum = 0, specifiedCount = 0;
    if (on) {
      // === UNEQUAL SPLIT: compute specifiedSum & update Amount‑Left ===
      checked.forEach(j => {
        const v = parseFloat(
          document.querySelector(`[name="detail_${i}_${j}"]`).value
        ) || 0;
        if (v > 0) {
          specifiedSum += v;
          specifiedCount++;
        }
      });
      const left = amount - specifiedSum;
      const leftDiv = document.getElementById(`left_${i}`);
      if (leftDiv) leftDiv.textContent = `Amount left: ${left.toFixed(2)}`;
      // === end UNEQUAL SPLIT ===
    }

    // now compute perShare (unchanged)
    let perShare = 0;
    if (!on) {
      perShare = checked.length ? amount / checked.length : 0;
    } else {
      const remaining = checked.length - specifiedCount;
      perShare = remaining > 0 ? (amount - specifiedSum) / remaining : 0;
      checked.forEach(j => {
        const inp = document.querySelector(`[name="detail_${i}_${j}"]`);
        if (!parseFloat(inp.value)) inp.value = perShare.toFixed(2);
      });
    }

    document.querySelector(`[name="avg_${i}"]`).value = perShare.toFixed(2);
  }
});
