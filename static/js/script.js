/* ==========================================================================
   Smart Lender Interactive Client-Side Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar Active State Highlights
    highlightNavbar();

    // 2. Form Validation & Loading Screen Multi-stage Animation
    initFormPredict();

    // 3. Button Ripple Effect
    initRippleEffect();

    // 4. Scroll Reveal Animations
    initScrollAnimations();

    // 5. Statistics Counters (for About page)
    initCounters();
});

/**
 * Highlights the active nav link based on the current URL path.
 */
function highlightNavbar() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-custom .nav-link');
    navLinks.forEach(link => {
        const hrefAttr = link.getAttribute('href');
        if (hrefAttr) {
            // Remove active class first
            link.classList.remove('active');
            
            // Check if matches
            if (currentPath === hrefAttr || (hrefAttr === '/' && currentPath === '') || (currentPath.includes(hrefAttr) && hrefAttr !== '/')) {
                link.classList.add('active');
            }
        }
    });
}

/**
 * Handles the multi-stage loan prediction submission, validation,
 * and loading animation.
 */
function initFormPredict() {
    const form = document.getElementById('loanPredictForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingSteps = document.querySelectorAll('.loading-text-step');

    if (!form || !loadingOverlay) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent standard submit

        // Standard validation check
        if (!validateForm(form)) {
            showToast("Please check the highlighted fields and enter valid inputs.", "danger");
            return;
        }

        // Show loading overlay
        loadingOverlay.classList.add('active');

        // Prepare data
        const formData = new FormData(form);
        const dataObj = {};
        formData.forEach((val, key) => {
            dataObj[key] = val;
        });

        // Trigger loading text cycles
        let currentStep = 0;
        loadingSteps[0].classList.add('active');

        const stepInterval = setInterval(() => {
            if (currentStep < loadingSteps.length - 1) {
                loadingSteps[currentStep].classList.remove('active');
                currentStep++;
                loadingSteps[currentStep].classList.add('active');
            }
        }, 700); // Shift step message every 700ms

        const startTime = Date.now();

        try {
            // Send API call to Flask
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataObj)
            });

            if (!response.ok) {
                throw new Error("Prediction request failed.");
            }

            const resJson = await response.json();

            // Calculate elapsed time to ensure user sees the progress steps
            const elapsed = Date.now() - startTime;
            const minDuration = 2800; // Let the animations run for at least 2.8s
            const delay = Math.max(0, minDuration - elapsed);

            setTimeout(() => {
                clearInterval(stepInterval);
                if (resJson.status === 'success' && resJson.redirect) {
                    window.location.href = resJson.redirect;
                } else {
                    throw new Error(resJson.message || "Unknown error occurred.");
                }
            }, delay);

        } catch (err) {
            clearInterval(stepInterval);
            loadingOverlay.classList.remove('active');
            showToast(err.message || "An unexpected error occurred during prediction. Please try again.", "danger");
        }
    });

    // Reset button handler
    const resetBtn = form.querySelector('button[type="reset"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            const inputs = form.querySelectorAll('.form-control-custom, .form-check-input');
            inputs.forEach(input => {
                input.classList.remove('is-invalid');
                input.classList.remove('is-valid');
            });
            showToast("Form fields reset successfully.", "secondary");
        });
    }
}

/**
 * Validates form fields and marks them visually if invalid.
 */
function validateForm(form) {
    let isValid = true;
    const requiredInputs = form.querySelectorAll('[required]');

    requiredInputs.forEach(input => {
        // Dropdown validation
        if (input.tagName === 'SELECT') {
            if (input.value === "" || input.value === null) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        } 
        // Numeric input validation
        else if (input.type === 'number') {
            const val = parseFloat(input.value);
            if (isNaN(val) || val < 0) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        }
        // Checkbox validation
        else if (input.type === 'checkbox') {
            if (!input.checked) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        }
        // General text validation
        else {
            if (input.value.trim() === "") {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        }
    });

    return isValid;
}

/**
 * Adds premium material design ripple effect to buttons.
 */
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn-grad, .btn-outline-custom, .btn-secondary');
    buttons.forEach(button => {
        button.classList.add('ripple');
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Initializes viewport scroll reveal fade-in/slide-up animations.
 */
function initScrollAnimations() {
    const animElements = document.querySelectorAll('.animate-on-scroll');
    if (animElements.length === 0) return;

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('appear');
                obs.unobserve(entry.target); // Trigger only once
            }
        });
    }, observerOptions);

    animElements.forEach(el => observer.observe(el));
}

/**
 * Renders statistical count-up animations for cards.
 */
function initCounters() {
    const counters = document.querySelectorAll('.counter-anim');
    if (counters.length === 0) return;

    const observerOptions = {
        root: null,
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const targetNum = parseFloat(target.getAttribute('data-target'));
                const duration = 1500; // 1.5s duration
                const isPercentage = target.innerText.includes('%');
                
                let startTimestamp = null;
                const step = (timestamp) => {
                    if (!startTimestamp) startTimestamp = timestamp;
                    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                    const currentVal = progress * targetNum;
                    
                    target.innerText = isPercentage 
                        ? `${currentVal.toFixed(1)}%` 
                        : Math.floor(currentVal);

                    if (progress < 1) {
                        window.requestAnimationFrame(step);
                    } else {
                        target.innerText = isPercentage 
                            ? `${targetNum.toFixed(1)}%` 
                            : Math.floor(targetNum);
                    }
                };

                window.requestAnimationFrame(step);
                obs.unobserve(target);
            }
        });
    }, observerOptions);

    counters.forEach(c => observer.observe(c));
}

/**
 * Displays user feedback toast notifications.
 */
function showToast(message, type = "info") {
    // Check if toast container exists
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.position = 'fixed';
        toastContainer.style.bottom = '20px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '9999';
        toastContainer.style.display = 'flex';
        toastContainer.style.flexDirection = 'column';
        toastContainer.style.gap = '10px';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast-custom border-start border-4 shadow-sm p-3 rounded-3`;
    
    // Theme color mappings
    let bgColor = '#FFFFFF';
    let borderColor = '#2563EB';
    let iconClass = 'bi-info-circle-fill';

    if (type === 'success') {
        borderColor = '#22C55E';
        iconClass = 'bi-check-circle-fill';
    } else if (type === 'danger') {
        borderColor = '#EF4444';
        iconClass = 'bi-exclamation-triangle-fill';
    } else if (type === 'secondary') {
        borderColor = '#64748B';
        iconClass = 'bi-arrow-counterclockwise';
    }

    toast.style.background = bgColor;
    toast.style.borderLeftColor = borderColor;
    toast.style.minWidth = '280px';
    toast.style.maxWidth = '350px';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '12px';
    toast.style.animation = 'slideUp 0.3s ease forwards';

    toast.innerHTML = `
        <i class="bi ${iconClass}" style="color: ${borderColor}; font-size: 1.25rem;"></i>
        <div style="font-size: 0.9rem; font-weight: 500; color: #0F172A;">${message}</div>
    `;

    toastContainer.appendChild(toast);

    // Remove toast after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'fade-out 0.4s ease forwards';
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 4000);
}

// Add CSS keyframe for toast fadeout programmatically
const style = document.createElement('style');
style.innerHTML = `
@keyframes fade-out {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(15px); }
}
.toast-custom {
    border-left-style: solid;
}
`;
document.head.appendChild(style);
