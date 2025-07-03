

function calculatePricePerUnit(quantity, price, unit) {
    let pricePerUnit = 0;
    if (quantity > 0 && price > 0) {
        let standardQuantity, displayUnit;
        
        // Determine unit category and convert to standard units
        switch (unit) {
            // WEIGHT UNITS - always show "per kg"
            case 'g':
            case 'grams':
                standardQuantity = quantity / 1000; // Convert grams to kg
                displayUnit = ' per kg';
                break;
                
            case 'kg':
            case 'kilograms':
                standardQuantity = quantity; // Already in kg
                displayUnit = ' per kg';
                break;
                
            // VOLUME UNITS - always show "per L"
            case 'ml':
            case 'milliliters':
                standardQuantity = quantity / 1000; // Convert ml to L
                displayUnit = ' per L';
                break;
                
            case 'cl':
            case 'centiliters':
                standardQuantity = quantity / 100; // Convert cl to L
                displayUnit = ' per L';
                break;
                
            case 'l':
            case 'liters':
                standardQuantity = quantity; // Already in L
                displayUnit = ' per L';
                break;
                
            // COOKING MEASUREMENTS - treat as volume, show "per L"
            case 'teaspoons':
                standardQuantity = quantity / 202; // Convert teaspoons to L
                displayUnit = ' per L';
                break;
                
            case 'tablespoons':
                standardQuantity = quantity / 67.628; // Convert tablespoons to L
                displayUnit = ' per L';
                break;
                
            // COUNT UNITS - show "per unit"
            case 'unit':
            default:
                standardQuantity = quantity;
                displayUnit = ' per unit';
                break;
        }
        
        pricePerUnit = price / standardQuantity;
        return pricePerUnit.toFixed(2) + displayUnit;
    }
    return ''; // Return an empty string if input is invalid
}

document.addEventListener('DOMContentLoaded', function() {
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('price');
    const unitSelect = document.getElementById('quantity_unit');
    const pricePerUnitInput = document.getElementById('price_per_unit');

    // Event listeners for the input fields on the form
    if (quantityInput && priceInput && unitSelect && pricePerUnitInput) {
        quantityInput.addEventListener('input', () => {
            pricePerUnitInput.value = calculatePricePerUnit(parseFloat(quantityInput.value), parseFloat(priceInput.value), unitSelect.value);
        });
        priceInput.addEventListener('input', () => {
            pricePerUnitInput.value = calculatePricePerUnit(parseFloat(quantityInput.value), parseFloat(priceInput.value), unitSelect.value);
        });
        unitSelect.addEventListener('change', () => {
            pricePerUnitInput.value = calculatePricePerUnit(parseFloat(quantityInput.value), parseFloat(priceInput.value), unitSelect.value);
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-ingredient]').forEach((element) => {
        const quantity = parseFloat(element.getAttribute('data-quantity'));
        const price = parseFloat(element.getAttribute('data-price'));
        const unit = element.getAttribute('data-unit');
        element.innerText = calculatePricePerUnit(quantity, price, unit);
    });
});
