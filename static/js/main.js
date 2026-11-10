/* ========================================
   Système de Sécurisation des Équipements
   JavaScript principal - Mobile & Web
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
    // ============ TOOLTIPS & POPOVERS ============
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // ============ MODE SOMBRE/CLAIRE ============
    const darkModeToggle = document.querySelector('input[name="dark_mode"]');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function () {
            const body = document.body;
            if (this.checked) {
                body.setAttribute('data-theme', 'dark');
            } else {
                body.setAttribute('data-theme', 'light');
            }
        });
    }

    // ============ FERMETURE AUTOMATIQUE ALERTES ============
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 6000);

    // ============ SIDEBAR MOBILE ============
    const sidebarToggle = document.querySelector('button[data-bs-toggle="sidebar"], .sidebar-toggle-btn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('show');
        if (overlay) overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (sidebar.classList.contains('show')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Fermer sidebar si clic sur un lien (mobile)
    document.querySelectorAll('.sidebar .nav-link').forEach(function (link) {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                closeSidebar();
            }
        });
    });

    // Fermer sidebar avec touche Échap
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });

    // ============ NOTIFICATIONS TEMPS RÉEL ============
    function updateNotificationCount() {
        fetch('/notifications/api/unread-count')
            .then(response => response.json())
            .then(data => {
                const badges = document.querySelectorAll('.badge.bg-danger.rounded-pill, .badge.bg-danger');
                badges.forEach(function (badge) {
                    badge.textContent = data.count;
                    badge.style.display = data.count > 0 ? 'inline-block' : 'none';
                });
            })
            .catch(() => {});
    }

    setInterval(updateNotificationCount, 30000);
    updateNotificationCount();

    // ============ TOUCH FEEDBACK CARTES ============
    document.querySelectorAll('.card, .btn, .list-group-item').forEach(function (el) {
        el.addEventListener('touchstart', function () {
            this.style.opacity = '0.8';
            this.style.transform = 'scale(0.98)';
        }, { passive: true });
        el.addEventListener('touchend', function () {
            this.style.opacity = '';
            this.style.transform = '';
        }, { passive: true });
    });

    // ============ CONFIRMATION SUPPRESSION ============
    document.querySelectorAll('form').forEach(function (form) {
        if (form.action && (form.action.includes('/delete') || form.querySelector('button[type="submit"][class*="danger"]'))) {
            form.addEventListener('submit', function (e) {
                if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // ============ SWIPE GESTURES SIDEBAR (MOBILE) ============
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', function (e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        // Swipe vers la gauche = fermer sidebar
        if (diff > swipeThreshold && sidebar && sidebar.classList.contains('show')) {
            closeSidebar();
        }
        // Swipe vers la droite depuis le bord = ouvrir sidebar (mobile uniquement)
        if (diff < -swipeThreshold && touchStartX < 30 && sidebar && !sidebar.classList.contains('show') && window.innerWidth < 992) {
            openSidebar();
        }
    }

    // ============ AUTO-RESIZE TEXTAREA ============
    document.querySelectorAll('textarea').forEach(function (textarea) {
        textarea.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // ============ PASSWORD TOGGLE ============
    document.querySelectorAll('.toggle-password').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            }
        });
    });
});

/* ========================================
   Toast notification
   ======================================== */
function showToast(message, type = 'success') {
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', function () {
        document.body.removeChild(toastEl);
    });
}

/* ========================================
   Fin du JavaScript
   ======================================== */
