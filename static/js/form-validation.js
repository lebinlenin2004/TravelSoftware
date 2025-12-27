// Form Validation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Phone number validation - only allow digits and limit to 10
    const phoneInputs = document.querySelectorAll('input[type="text"][pattern="[0-9]{10}"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Remove non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            // Limit to 10 digits
            if (value.length > 10) {
                value = value.substring(0, 10);
            }
            e.target.value = value;
        });
        
        input.addEventListener('blur', function(e) {
            if (e.target.value.length !== 10 && e.target.value.length > 0) {
                e.target.setCustomValidity('Phone number must be exactly 10 digits');
                e.target.classList.add('is-invalid');
            } else {
                e.target.setCustomValidity('');
                e.target.classList.remove('is-invalid');
            }
        });
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            const email = e.target.value.trim();
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (email && !emailRegex.test(email)) {
                e.target.setCustomValidity('Please enter a valid email address');
                e.target.classList.add('is-invalid');
            } else {
                e.target.setCustomValidity('');
                e.target.classList.remove('is-invalid');
            }
        });
    });
    
    // Number input validation - prevent negative values
    const numberInputs = document.querySelectorAll('input[type="number"][min="0"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            if (e.target.value < 0) {
                e.target.value = 0;
            }
        });
    });
    
    // Percentage validation (0-100)
    const percentageInputs = document.querySelectorAll('input[type="number"][max="100"]');
    percentageInputs.forEach(function(input) {
        if (input.getAttribute('min') === '0' || input.getAttribute('min') === null) {
            input.addEventListener('input', function(e) {
                let value = parseFloat(e.target.value);
                if (value > 100) {
                    e.target.value = 100;
                }
                if (value < 0) {
                    e.target.value = 0;
                }
            });
        }
    });
    
    // Travel date validation - cannot be in the past
    const travelDateInputs = document.querySelectorAll('input[type="date"][min="today"]');
    travelDateInputs.forEach(function(input) {
        // Set min to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
        
        input.addEventListener('change', function(e) {
            const selectedDate = new Date(e.target.value);
            const todayDate = new Date();
            todayDate.setHours(0, 0, 0, 0);
            
            if (selectedDate < todayDate) {
                e.target.setCustomValidity('Travel date cannot be in the past');
                e.target.classList.add('is-invalid');
            } else {
                e.target.setCustomValidity('');
                e.target.classList.remove('is-invalid');
            }
        });
    });
    
    // Form submission validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Show validation errors
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(function(field) {
                    field.classList.add('is-invalid');
                });
                
                // Scroll to first invalid field
                if (invalidFields.length > 0) {
                    invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    invalidFields[0].focus();
                }
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation feedback
    const allInputs = document.querySelectorAll('input, textarea, select');
    allInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            if (e.target.checkValidity()) {
                e.target.classList.remove('is-invalid');
                e.target.classList.add('is-valid');
            } else {
                e.target.classList.remove('is-valid');
                e.target.classList.add('is-invalid');
            }
        });
        
        input.addEventListener('input', function(e) {
            if (e.target.checkValidity()) {
                e.target.classList.remove('is-invalid');
                e.target.classList.add('is-valid');
            }
        });
    });
});

