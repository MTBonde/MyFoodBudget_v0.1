

function calculatePricePerUnit(quantity, price, unit) {
    let pricePerUnit = 0;
    if (quantity > 0 && price > 0) {
        switch (unit) {
            case 'grams':
            case 'milliliters':
                pricePerUnit = price / (quantity / 1000);
                break;
            case 'kilograms':
            case 'liters':
                pricePerUnit = price / quantity;
                break;
            case 'teaspoons':
                pricePerUnit = (price / (quantity / 202)); // Approx. conversion from teaspoons to liters
                break;
            case 'tablespoons':
                pricePerUnit = (price / (quantity / 67.628)); // Approx. conversion from tablespoons to liters
                break;
            default:
                pricePerUnit = price / quantity;
                break;
            }
            let pricePerStandardUnit = (unit === 'grams' || unit === 'milliliters') ? ' per kg' : ' per liter';
            return pricePerUnit.toFixed(2) + pricePerStandardUnit;
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
