document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });
});
