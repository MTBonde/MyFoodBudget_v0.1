/// <summary>
/// Adds a new row for an existing ingredient with a dropdown for ingredient selection,
/// an input for quantity, a dropdown for unit, and a confirm button.
/// </summary>
function addExistingIngredient() {
    const ingredientsList = document.getElementById('ingredients-list');
    const ingredientInput = document.createElement('div');
    ingredientInput.classList.add('ingredient-input');

    // Build dropdown options from the global existingIngredients variable
    let options = '<option value="">Select Ingredient</option>';
    existingIngredients.forEach(function(ingredient) {
        options += `<option value="${ingredient.id}" data-price="${ingredient.price}">${ingredient.name}</option>`;
    });

    ingredientInput.innerHTML = `
        <select class="form-select mb-2" name="existing_ingredients[]" required>
            ${options}
        </select>
        <input type="number" class="form-control mb-2" name="existing_ingredient_quantities[]" placeholder="Quantity" required>
        <select class="form-select mb-2" name="existing_ingredient_units[]" required>
            <option value="grams">grams</option>
            <option value="kilograms">kilograms</option>
            <option value="liters">liters</option>
            <option value="milliliters">milliliters</option>
        </select>
        <button type="button" class="btn btn-success confirm-ingredient-btn mb-2">Add Ingredient</button>
    `;
    ingredientsList.appendChild(ingredientInput);
}

/// <summary>
/// Adds a new row for entering a new ingredient with its name, quantity, unit, and price inputs,
/// plus a confirm button to lock in the ingredient.
/// </summary>
function addNewIngredient() {
    const ingredientsList = document.getElementById('ingredients-list');
    const ingredientInput = document.createElement('div');
    ingredientInput.classList.add('ingredient-input');
    ingredientInput.innerHTML = `
        <input type="text" class="form-control mb-2" name="new_ingredient_names[]" placeholder="Ingredient Name" required>
        <input type="number" class="form-control mb-2" name="new_ingredient_quantities[]" placeholder="Quantity" required>
        <select class="form-select mb-2" name="new_ingredient_units[]" required>
            <option value="grams">grams</option>
            <option value="kilograms">kilograms</option>
            <option value="liters">liters</option>
            <option value="milliliters">milliliters</option>
        </select>
        <input type="number" class="form-control mb-2" name="new_ingredient_prices[]" placeholder="Price" required>
        <button type="button" class="btn btn-success confirm-ingredient-btn mb-2">Add Ingredient</button>
    `;
    ingredientsList.appendChild(ingredientInput);
}

/// <summary>
/// Updates the displayed total recipe cost by summing the cost of all confirmed ingredient rows.
/// For existing ingredients, it uses the global existingIngredients array; for new ingredients, it uses the hidden inputs.
/// </summary>
function updateTotalCost() {
    let totalCost = 0;
    // Get all confirmed ingredient rows
    const ingredientRows = document.querySelectorAll('.ingredient-input.confirmed');
    ingredientRows.forEach(row => {
        // Check if it's an existing ingredient row by looking for a hidden input with name "existing_ingredients[]"
        const hiddenExistingId = row.querySelector('input[type="hidden"][name="existing_ingredients[]"]');
        if (hiddenExistingId) {
            const hiddenQuantity = row.querySelector('input[type="hidden"][name="existing_ingredient_quantities[]"]');
            let quantity = parseFloat(hiddenQuantity.value) || 0;
            // Find the ingredient in the existingIngredients array
            let ingredient = existingIngredients.find(ing => ing.id == hiddenExistingId.value);
            if (ingredient) {
                totalCost += ingredient.price * quantity;
            }
        } else {
            // It's a new ingredient row
            const hiddenPrice = row.querySelector('input[type="hidden"][name="new_ingredient_prices[]"]');
            const hiddenQuantity = row.querySelector('input[type="hidden"][name="new_ingredient_quantities[]"]');
            if (hiddenPrice && hiddenQuantity) {
                let price = parseFloat(hiddenPrice.value) || 0;
                let quantity = parseFloat(hiddenQuantity.value) || 0;
                totalCost += price * quantity;
            }
        }
    });
    // Update the total cost display element
    const totalCostElement = document.getElementById("total-cost");
    if (totalCostElement) {
        totalCostElement.innerText = totalCost.toFixed(2);
    }
}

/// <summary>
/// Listens for clicks on any "confirm ingredient" button. When clicked, it validates that all fields
/// in that ingredient row are filled out, then creates hidden inputs (if they don't already exist),
/// disables the visible inputs, hides the confirm button, marks the row as confirmed, and updates the total cost.
/// </summary>
document.addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('confirm-ingredient-btn')) {
        const ingredientDiv = event.target.closest('.ingredient-input');
        // Validate that all inputs/selects in the row are filled
        const inputs = ingredientDiv.querySelectorAll('input, select');
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
        // For each input, check if a hidden input with the same name already exists; if not, create one, then disable the visible input.
        inputs.forEach(function(input) {
            if (!ingredientDiv.querySelector(`input[type="hidden"][name="${input.name}"]`)) {
                let hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = input.name;
                hidden.value = input.value;
                ingredientDiv.appendChild(hidden);
            }
            input.disabled = true;
        });
        // Hide the confirm button so it's not triggered twice
        event.target.style.display = 'none';
        // Mark the row as confirmed
        ingredientDiv.classList.add('confirmed');
        // Update the total cost display
        updateTotalCost();
    }
});
