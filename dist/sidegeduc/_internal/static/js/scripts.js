// scripts.js
// Código común para la interfaz (sidebar, mensajes, validaciones en tiempo real)
(function(window, document){
    'use strict';

    function initSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menu-toggle');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const overlay = document.querySelector('.sidebar-overlay');
        const storageKey = 'sidebarHidden';

        if (!sidebar) return;

        function setSidebarHidden(hidden) {
            if (hidden) {
                sidebar.classList.add('hidden');
                localStorage.setItem(storageKey, 'true');
            } else {
                sidebar.classList.remove('hidden');
                localStorage.setItem(storageKey, 'false');
            }
        }

        function toggleSidebar() {
            const isHidden = sidebar.classList.contains('hidden');
            setSidebarHidden(!isHidden);
        }

        try {
            const stored = localStorage.getItem(storageKey);
            if (stored === 'true') {
                setSidebarHidden(true);
            }
        } catch (e) {
            // Ignore localStorage errors (privacy mode, etc.)
        }

        if (menuToggle) {
            menuToggle.addEventListener('click', toggleSidebar);
        }
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', toggleSidebar);
        }
        if (overlay) {
            overlay.addEventListener('click', function () {
                setSidebarHidden(true);
            });
        }

        // Close sidebar on mobile when clicking a link
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 768) {
                    setSidebarHidden(true);
                }
            });
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                const isHidden = sidebar.classList.contains('hidden');
                if (isHidden && localStorage.getItem(storageKey) !== 'true') {
                    setSidebarHidden(false);
                }
            }
        });
    }

    function initRealTimeValidation() {
        if (typeof window.realTimeValidator !== 'function') return;
        document.querySelectorAll('input[data-rule]').forEach(el =>
            el.addEventListener('input', window.realTimeValidator)
        );
    }

    function showMessageFromQuery() {
        const msgEl = document.getElementById('message');
        if (!msgEl) return;

        const params = new URLSearchParams(window.location.search);
        const message = params.get('message');
        if (!message) return;

        const span = msgEl.querySelector('span');
        if (span) {
            span.textContent = message;
        }
        msgEl.style.display = 'block';

        setTimeout(() => {
            msgEl.style.display = 'none';
        }, 2000);
    }

    document.addEventListener('DOMContentLoaded', function () {
        initSidebarToggle();
        initRealTimeValidation();
        showMessageFromQuery();
    });

})(window, document);
