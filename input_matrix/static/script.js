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
    const labels = ["Title", "Amount", "Paid By", "Toggle"]
      .concat(Array(n).fill(null), ["Avg", "Buttons"]);
    
    const fragment = document.createDocumentFragment();
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
      fragment.appendChild(th);
    });
    header.appendChild(fragment);
  }

  function addRow() {
    const n = parseInt(sizeInput.value, 10) || 1;
    rowCount += 1;
    rowCountField.value = rowCount;

    const i = rowCount;
    const row = table.insertRow();
    row.classList.add("data-row");
    row.dataset.row = i;

    const fragment = document.createDocumentFragment();

    // Title
    let cell = document.createElement("td");
    const title = document.createElement("input");
    title.type = "text"; 
    title.name = `title_${i}`; 
    title.required = true;
    cell.appendChild(title);
    fragment.appendChild(cell);

    // Amount
    cell = document.createElement("td");
    const amount = document.createElement("input");
    amount.type = "number"; 
    amount.name = `amount_${i}`;
    amount.min = "0"; 
    amount.step = "any"; 
    amount.value = "0";
    amount.addEventListener("input", () => recalcRow(i));
    cell.appendChild(amount);
    fragment.appendChild(cell);

    // Paid By
    cell = document.createElement("td");
    const paidBy = document.createElement("select");
    paidBy.name = `paidby_${i}`;
    populatePaidByOptions(paidBy);
    cell.appendChild(paidBy);
    fragment.appendChild(cell);

    // Toggle
    cell = document.createElement("td");
    const toggle = document.createElement("input");
    toggle.type = "checkbox"; 
    toggle.name = `toggle_${i}`;
    toggle.addEventListener("change", () => handleToggle(i));
    cell.appendChild(toggle);
    fragment.appendChild(cell);

    // Checkboxes
    for (let j = 1; j <= n; j++) {
      cell = document.createElement("td");
      const chk = document.createElement("input");
      chk.type = "checkbox"; 
      chk.name = `chk_${i}_${j}`;
      chk.addEventListener("change", () => recalcRow(i));
      cell.appendChild(chk);
      fragment.appendChild(cell);
    }

    // Avg
    cell = document.createElement("td");
    const avg = document.createElement("input");
    avg.type = "number"; 
    avg.name = `avg_${i}`;
    avg.readOnly = true; 
    avg.value = "0";
    cell.appendChild(avg);
    fragment.appendChild(cell);

    // Buttons: All & Clear
    cell = document.createElement("td");
    const allBtn = document.createElement("button");
    allBtn.type = "button"; 
    allBtn.textContent = "All";
    allBtn.addEventListener("click", () => {
      clearRow(i, false);
      const n = parseInt(sizeInput.value, 10) || 1;
      for (let j = 1; j <= n; j++) {
        document.querySelector(`[name="chk_${i}_${j}"]`).checked = true;
      }
      recalcRow(i);
    });
    cell.appendChild(allBtn);

    const clrBtn = document.createElement("button");
    clrBtn.type = "button"; 
    clrBtn.textContent = "Clear";
    clrBtn.addEventListener("click", () => clearRow(i, true));
    cell.appendChild(clrBtn);
    fragment.appendChild(cell);

    row.appendChild(fragment);
  }

  function addColumn() {
    let n = parseInt(sizeInput.value, 10) || 1;
    n += 1; 
    sizeInput.value = n; 
    sizeField.value = n;

    // Header: before Avg
    const header = table.rows[0];
    const th = document.createElement("th");
    const colIdx = n;
    const inp = document.createElement("input");
    inp.type = "text"; 
    inp.name = `colname_${colIdx}`;
    inp.value = `Name ${colIdx}`; 
    inp.addEventListener("input", updateAllPaidBys);
    th.appendChild(inp);
    header.insertBefore(th, header.cells[header.cells.length - 2]);

    // Each data-row: insert checkbox
    const dataRows = document.querySelectorAll("tr.data-row");
    dataRows.forEach(row => {
      const rowIdx = row.dataset.row;
      const td = document.createElement("td");
      const chk = document.createElement("input");
      chk.type = "checkbox"; 
      chk.name = `chk_${rowIdx}_${colIdx}`;
      chk.addEventListener("change", () => recalcRow(rowIdx));
      td.appendChild(chk);
      row.insertBefore(td, row.cells[row.cells.length - 2]);
    });

    // Each detail-row: insert detail input
    const detailRows = document.querySelectorAll("tr.detail-row");
    detailRows.forEach(detail => {
      const prevData = detail.previousElementSibling;
      const rowIdx = prevData.dataset.row;
      const td = document.createElement("td");
      const inp = document.createElement("input");
      inp.type = "number"; 
      inp.min = "0"; 
      inp.step = "any";
      inp.name = `detail_${rowIdx}_${n}`;
      inp.addEventListener("input", () => handleDetailInput(rowIdx, n, inp));
      td.appendChild(inp);
      detail.insertBefore(td, detail.cells[detail.cells.length - 2]);
    });

    updateAllPaidBys();
  }

  function clearRow(i, removeDetail) {
    const checkboxes = document.querySelectorAll(`[name^="chk_${i}_"]`);
    checkboxes.forEach(cb => cb.checked = false);
    
    const avgInput = document.querySelector(`[name="avg_${i}"]`);
    if (avgInput) avgInput.value = "0";
    
    if (removeDetail) {
      const det = document.getElementById(`detail_${i}`);
      if (det) det.remove();
    }
  }

  function getColNames() {
    const inputs = document.querySelectorAll("input[name^='colname_']");
    return Array.from(inputs, inp => inp.value || "");
  }

  function populatePaidByOptions(sel) {
    const colNames = getColNames();
    const currentValue = sel.value;
    
    sel.innerHTML = "";
    const fragment = document.createDocumentFragment();
    
    colNames.forEach(name => {
      const opt = document.createElement("option");
      opt.value = name; 
      opt.textContent = name;
      fragment.appendChild(opt);
    });
    
    sel.appendChild(fragment);
    
    // Restore selection if still valid
    if (currentValue && colNames.includes(currentValue)) {
      sel.value = currentValue;
    }
  }

  function updateAllPaidBys() {
    const dataRows = document.querySelectorAll("tr.data-row");
    const colNames = getColNames();
    
    dataRows.forEach(row => {
      const i = row.dataset.row;
      const sel = row.querySelector(`select[name="paidby_${i}"]`);
      if (sel) {
        const currentValue = sel.value;
        sel.innerHTML = "";
        const fragment = document.createDocumentFragment();
        
        colNames.forEach(name => {
          const opt = document.createElement("option");
          opt.value = name; 
          opt.textContent = name;
          fragment.appendChild(opt);
        });
        
        sel.appendChild(fragment);
        
        if (currentValue && colNames.includes(currentValue)) {
          sel.value = currentValue;
        }
      }
    });
  }

  function handleToggle(rowIndex) {
    const toggleInput = document.querySelector(`[name="toggle_${rowIndex}"]`);
    const on = toggleInput.checked;
    const dataRow = document.querySelector(`tr.data-row[data-row="${rowIndex}"]`);
    const detId = `detail_${rowIndex}`;

    // always clear first
    clearRow(rowIndex, true);

    if (on) {
      const n = parseInt(sizeInput.value, 10) || 1;
      const detail = document.createElement("tr");
      detail.id = detId;
      detail.classList.add("detail-row");

      const fragment = document.createDocumentFragment();

      // blank under Title, Amount, PaidBy, Toggle
      for (let k = 0; k < 4; k++) {
        fragment.appendChild(document.createElement("td"));
      }

      // detail inputs for each checkbox col
      for (let j = 1; j <= n; j++) {
        const td = document.createElement("td");
        const inp = document.createElement("input");
        inp.type = "number"; 
        inp.min = "0"; 
        inp.step = "any";
        inp.name = `detail_${rowIndex}_${j}`;
        inp.addEventListener("input", () => handleDetailInput(rowIndex, j, inp));
        td.appendChild(inp);
        fragment.appendChild(td);
      }

      // Amount-Left cell under Avg
      const leftCell = document.createElement("td");
      leftCell.innerHTML = `<div class="amount-left" id="left_${rowIndex}">Amount left: 0.00</div>`;
      fragment.appendChild(leftCell);

      // blank under Buttons
      fragment.appendChild(document.createElement("td"));

      detail.appendChild(fragment);
      dataRow.insertAdjacentElement("afterend", detail);
      recalcRow(rowIndex);
    }
  }

  function handleDetailInput(rowIndex, colJ, inp) {
    const n = parseInt(sizeInput.value, 10) || 1;
    const amountInput = document.querySelector(`[name="amount_${rowIndex}"]`);
    const amount = parseFloat(amountInput.value) || 0;

    // clamp sum(detail) ≤ amount
    let sumOthers = 0;
    for (let k = 1; k <= n; k++) {
      if (k !== colJ) {
        const detailInput = document.querySelector(`[name="detail_${rowIndex}_${k}"]`);
        sumOthers += parseFloat(detailInput.value) || 0;
      }
    }
    
    let val = parseFloat(inp.value) || 0;
    if (sumOthers + val > amount) {
      val = amount - sumOthers;
      inp.value = val.toFixed(2);
    }

    // auto-check box
    const checkbox = document.querySelector(`[name="chk_${rowIndex}_${colJ}"]`);
    checkbox.checked = val > 0;
    
    recalcRow(rowIndex);
  }

  function recalcRow(i) {
    const amountInput = document.querySelector(`[name="amount_${i}"]`);
    const amount = parseFloat(amountInput.value) || 0;
    
    const toggleInput = document.querySelector(`[name="toggle_${i}"]`);
    const on = toggleInput.checked;
    
    const n = parseInt(sizeInput.value, 10) || 1;

    // Gather checked boxes
    const checked = [];
    const checkboxes = document.querySelectorAll(`tr.data-row[data-row="${i}"] input[name^="chk_${i}_"]`);
    checkboxes.forEach(cb => {
      const [, , j] = cb.name.split("_");
      if (cb.checked) checked.push(Number(j));
    });

    let totalAllocated = 0;

    if (on) {
      // UNEQUAL SPLIT: sum all detail values for checked boxes
      checked.forEach(j => {
        const detailInput = document.querySelector(`[name="detail_${i}_${j}"]`);
        const v = parseFloat(detailInput.value) || 0;
        totalAllocated += v;
      });
      
      // Update Amount-Left display
      const left = amount - totalAllocated;
      const leftDiv = document.getElementById(`left_${i}`);
      if (leftDiv) {
        leftDiv.textContent = `Amount left: ${left.toFixed(2)}`;
      }

      // Fill in empty detail fields with remaining amount divided equally
      const emptyDetails = checked.filter(j => {
        const detailInput = document.querySelector(`[name="detail_${i}_${j}"]`);
        return !parseFloat(detailInput.value);
      });

      if (emptyDetails.length > 0 && left > 0) {
        const perEmpty = left / emptyDetails.length;
        emptyDetails.forEach(j => {
          const detailInput = document.querySelector(`[name="detail_${i}_${j}"]`);
          detailInput.value = perEmpty.toFixed(2);
        });
        totalAllocated = amount; // After filling, total is the full amount
      }
    } else {
      // EQUAL SPLIT: total allocated is the full amount
      totalAllocated = amount;
    }

    // Calculate ACTUAL average per checked person
    const avgInput = document.querySelector(`[name="avg_${i}"]`);
    if (checked.length > 0) {
      const actualAvg = totalAllocated / checked.length;
      avgInput.value = actualAvg.toFixed(2);
    } else {
      avgInput.value = "0";
    }
  }
});