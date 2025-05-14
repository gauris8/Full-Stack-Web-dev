// Auto-dismiss alerts after 3 seconds
window.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    });
});

// Optional: Show a loader or feedback on form submit
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        // You can add a loader or disable the button here
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Submitting...';
        }
    });
});

// Recipe tabs for dashboard (server-rendered tab content)
document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach((btn, idx) => {
        btn.addEventListener('click', function() {
            // Remove active from all buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            // Hide all tab contents
            tabContents.forEach(tc => tc.style.display = 'none');
            // Activate this button
            btn.classList.add('active');
            // Show the corresponding tab content
            const tabId = 'tab-' + btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.style.display = '';
            }
        });
    });
    // On load, show only the first tab content and set first tab as active
    tabBtns.forEach((b, i) => b.classList.toggle('active', i === 0));
    tabContents.forEach((tc, i) => tc.style.display = i === 0 ? '' : 'none');
}); 