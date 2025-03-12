// Adds a new row for entering a NEW ingredient.
function addNewIngredientRow() {
    const tableBody = document.querySelector('#ingredients-table tbody');
    const row = document.createElement('tr');
    row.classList.add('ingredient-row');

    row.innerHTML = `
      <td>
        <input type="text" class="form-control" name="new_ingredient_names[]" placeholder="Ingredient Name" required>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="new_quantity_purchased[]" placeholder="Quantity Purchased" required>
      </td>
      <td>
        <select class="form-select" name="new_unit[]" required>
          <option value="grams">grams</option>
          <option value="kilograms">kilograms</option>
          <option value="liters">liters</option>
          <option value="milliliters">milliliters</option>
        </select>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="new_ingredient_prices[]" placeholder="Price at Purchase" required>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="new_quantity_used[]" placeholder="Quantity Used" required>
      </td>
      <td>
        <select class="form-select" name="new_used_unit[]" required>
          <option value="grams">grams</option>
          <option value="kilograms">kilograms</option>
          <option value="liters">liters</option>
          <option value="milliliters">milliliters</option>
        </select>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="new_total_cost[]" placeholder="Total Cost" readonly>
      </td>
      <td>
        <button type="button" class="btn btn-success confirm-ingredient-btn">Confirm</button>
      </td>
    `;
    tableBody.appendChild(row);

    // Get references to the inputs in this row.
    const qtyPurchasedInput = row.querySelector('input[name="new_quantity_purchased[]"]');
    const priceInput = row.querySelector('input[name="new_ingredient_prices[]"]');
    const qtyUsedInput = row.querySelector('input[name="new_quantity_used[]"]');
    const totalCostInput = row.querySelector('input[name="new_total_cost[]"]');

    // Calculate total cost = (quantity used / quantity purchased) * price.
    function calculateNewTotal() {
        const qtyPurchased = parseFloat(qtyPurchasedInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const qtyUsed = parseFloat(qtyUsedInput.value) || 0;
        let total = 0;
        if (qtyPurchased > 0) {
            total = (qtyUsed / qtyPurchased) * price;
        }
        totalCostInput.value = total.toFixed(2);
    }

    // Recalculate when any relevant field changes.
    qtyPurchasedInput.addEventListener('input', calculateNewTotal);
    priceInput.addEventListener('input', calculateNewTotal);
    qtyUsedInput.addEventListener('input', calculateNewTotal);
}

// Adds a new row for selecting an EXISTING ingredient.
function addExistingIngredientRow() {
    const tableBody = document.querySelector('#ingredients-table tbody');
    const row = document.createElement('tr');
    row.classList.add('ingredient-row');

    // Build dropdown options using the existingIngredients array.
    let options = '<option value="">Select Ingredient</option>';
    existingIngredients.forEach(function(ingredient) {
        // Assumes each ingredient has id, name, price, and quantity (purchased quantity) properties.
        options += `<option value="${ingredient.id}" data-price="${ingredient.price}" data-quantity="${ingredient.quantity}">${ingredient.name}</option>`;
    });

    row.innerHTML = `
      <td>
        <select class="form-select" name="existing_ingredients[]" required>
          ${options}
        </select>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="existing_quantity_purchased[]" placeholder="Quantity Purchased" readonly required>
      </td>
      <td>
        <select class="form-select" name="existing_ingredient_units[]" required>
          <option value="grams">grams</option>
          <option value="kilograms">kilograms</option>
          <option value="liters">liters</option>
          <option value="milliliters">milliliters</option>
        </select>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="existing_ingredient_prices[]" placeholder="Price at Purchase" readonly required>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="existing_quantity_used[]" placeholder="Quantity Used" required>
      </td>
      <td>
        <select class="form-select" name="existing_used_unit[]" required>
          <option value="grams">grams</option>
          <option value="kilograms">kilograms</option>
          <option value="liters">liters</option>
          <option value="milliliters">milliliters</option>
        </select>
      </td>
      <td>
        <input type="number" step="any" class="form-control" name="existing_total_cost[]" placeholder="Total Cost" readonly>
      </td>
      <td>
        <button type="button" class="btn btn-success confirm-ingredient-btn">Confirm</button>
      </td>
    `;
    tableBody.appendChild(row);

    // Get references to inputs in this row.
    const ingredientSelect = row.querySelector('select[name="existing_ingredients[]"]');
    const qtyPurchasedInput = row.querySelector('input[name="existing_quantity_purchased[]"]');
    const priceInput = row.querySelector('input[name="existing_ingredient_prices[]"]');
    const qtyUsedInput = row.querySelector('input[name="existing_quantity_used[]"]');
    const totalCostInput = row.querySelector('input[name="existing_total_cost[]"]');

    // When an ingredient is selected, autofill quantity purchased and price.
    ingredientSelect.addEventListener('change', function() {
        const selectedOption = ingredientSelect.options[ingredientSelect.selectedIndex];
        const price = selectedOption.getAttribute('data-price') || 0;
        const quantity = selectedOption.getAttribute('data-quantity') || 0;
        priceInput.value = price;
        qtyPurchasedInput.value = quantity;
        calculateExistingTotal();
    });

    // Calculate total cost = (quantity used / quantity purchased) * price.
    function calculateExistingTotal() {
        const qtyPurchased = parseFloat(qtyPurchasedInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const qtyUsed = parseFloat(qtyUsedInput.value) || 0;
        let total = 0;
        if (qtyPurchased > 0) {
            total = (qtyUsed / qtyPurchased) * price;
        }
        totalCostInput.value = total.toFixed(2);
    }

    // Recalculate when quantity used changes.
    qtyUsedInput.addEventListener('input', calculateExistingTotal);
}

// Global event listener for Confirm and Delete buttons.
document.addEventListener('click', function(event) {
    // If the button is a Delete button, remove the row.
    if (event.target && event.target.classList.contains('delete-ingredient-btn')) {
        const row = event.target.closest('tr');
        row.remove();
        updateOverallTotalCost();
        return;
    }
    // If the button is a Confirm button, validate and lock the row.
    if (event.target && event.target.classList.contains('confirm-ingredient-btn')) {
        const row = event.target.closest('tr');
        // Validate that all inputs/selects in the row have values.
        const inputs = row.querySelectorAll('input, select');
        let valid = true;
        inputs.forEach(function(input) {
            if (!input.value) {
                valid = false;
            }
        });
        if (!valid) {
            alert("Please fill out all fields before confirming.");
            return;
        }
        // For each input, create a hidden input if it doesn't exist and disable the visible input.
        inputs.forEach(function(input) {
            if (!row.querySelector(`input[type="hidden"][name="${input.name}"]`)) {
                let hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = input.name;
                hidden.value = input.value;
                row.appendChild(hidden);
            }
            input.disabled = true;
        });
        // Change the Confirm button into a Delete button styled in red.
        event.target.classList.remove('confirm-ingredient-btn', 'btn-success');
        event.target.classList.add('delete-ingredient-btn', 'btn-danger');
        event.target.innerText = 'Delete';
        updateOverallTotalCost();
    }
});

// Updates the overall recipe cost by summing the total cost from all confirmed rows.
function updateOverallTotalCost() {
    let overallCost = 0;
    // Only sum the hidden total cost fields to avoid double-counting.
    const totalCostFields = document.querySelectorAll('input[type="hidden"][name="new_total_cost[]"], input[type="hidden"][name="existing_total_cost[]"]');
    totalCostFields.forEach(function(field) {
        overallCost += parseFloat(field.value) || 0;
    });
    const totalCostElement = document.getElementById("total-cost");
    if (totalCostElement) {
        totalCostElement.innerText = overallCost.toFixed(2);
    }
}

