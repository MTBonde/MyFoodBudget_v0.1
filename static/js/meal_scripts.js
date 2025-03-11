
function addExistingIngredient() {
    const ingredientsList = document.getElementById('ingredients-list');
    const ingredientInput = document.createElement('div');
    ingredientInput.classList.add('ingredient-input');

    // Byg dropdown options fra den globale variabel
    let options = '<option value="">Select Ingredient</option>';
    existingIngredients.forEach(function(ingredient) {
        options += `<option value="${ingredient.id}" data-price="${ingredient.price}">${ingredient.name}</option>`;
    });

    ingredientInput.innerHTML = `
        <select class="form-select mb-2" name="existing_ingredients[]">
            ${options}
        </select>
        <input type="number" class="form-control mb-2" name="existing_ingredient_quantities[]" placeholder="Quantity" required>
        <select class="form-select mb-2" name="existing_ingredient_units[]">
            <option value="grams">grams</option>
            <option value="kilograms">kilograms</option>
            <option value="liters">liters</option>
            <option value="milliliters">milliliters</option>
        </select>
    `;
    ingredientsList.appendChild(ingredientInput);
}


function addNewIngredient() {
    const ingredientsList = document.getElementById('ingredients-list');
    const ingredientInput = document.createElement('div');
    ingredientInput.classList.add('ingredient-input');
    ingredientInput.innerHTML = `
        <input type="text" class="form-control mb-2" name="new_ingredient_names[]" placeholder="Ingredient Name" required>
        <input type="number" class="form-control mb-2" name="new_ingredient_quantities[]" placeholder="Quantity" required>
        <select class="form-select mb-2" name="new_ingredient_units[]">
            <option value="grams">grams</option>
            <option value="kilograms">kilograms</option>
            <option value="liters">liters</option>
            <option value="milliliters">milliliters</option>
        </select>
        <input type="number" class="form-control mb-2" name="new_ingredient_prices[]" placeholder="Price" required>
    `;
    ingredientsList.appendChild(ingredientInput);
}

