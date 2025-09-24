document.addEventListener("DOMContentLoaded", () => {
    const sideBar = document.querySelector(".side-bar");
    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const closeBtn = document.querySelector(".close-btn");
    let overlay;

    // Create overlay if not exists
    function createOverlay() {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
            
            // Agregar listener al overlay para cerrar el sidebar
            overlay.addEventListener('click', closeSidebar);
        }
    }

    // Initialize overlay
    createOverlay();

    // Function to show the sidebar
    function openSidebar() {
        sideBar.classList.add("active");
        overlay.classList.add("active");
        sidebarToggle.style.opacity = "0";
        setTimeout(() => sidebarToggle.style.visibility = "hidden", 200);
    }

    // Function to close the sidebar
    function closeSidebar() {
        sideBar.classList.remove("active");
        overlay.classList.remove("active");
        setTimeout(() => {
            sidebarToggle.style.visibility = "visible";
            sidebarToggle.style.opacity = "1";
        }, 100);
    }

    // Toggle sidebar
    sidebarToggle.addEventListener("click", openSidebar);
    closeBtn.addEventListener("click", closeSidebar);

    // Function to toggle submenus
    // Function to handle height transitions
    function animateHeight(element, from, to, onComplete) {
        element.style.height = from + 'px';
        element.offsetHeight; // Force reflow
        element.style.height = to + 'px';

        if (onComplete) {
            const onTransitionEnd = () => {
                onComplete();
                element.removeEventListener('transitionend', onTransitionEnd);
            };
            element.addEventListener('transitionend', onTransitionEnd);
        }
    }

    function toggleSubMenu(btn) {
        if (!btn) return;
        
        const subMenu = btn.nextElementSibling;
        const dropdownIcon = btn.querySelector(".dropdown");
        
        if (!subMenu || subMenu.classList.contains('animating')) return;

        const isOpen = subMenu.classList.contains('active');
        subMenu.classList.add('animating');

        // If it's a main menu, close other main menus
        const isMainMenu = btn.closest('.menu > .item > a') === btn;
        if (isMainMenu && !isOpen) {
            const otherMainMenus = Array.from(document.querySelectorAll('.menu > .item > a'))
                .filter(menuBtn => menuBtn !== btn);
                
            otherMainMenus.forEach(menuBtn => {
                const otherSubMenu = menuBtn.nextElementSibling;
                const otherDropdown = menuBtn.querySelector(".dropdown");
                if (otherSubMenu && otherSubMenu.classList.contains('active')) {
                    closeSubMenu(otherSubMenu, otherDropdown);
                }
            });
        }

        if (isOpen) {
            closeSubMenu(subMenu, dropdownIcon);
        } else {
            openSubMenu(subMenu, dropdownIcon);
        }
    }

    function openSubMenu(subMenu, dropdownIcon) {
        // Calculate height
        subMenu.style.display = 'block';
        const height = subMenu.scrollHeight;
        subMenu.style.display = '';
        
        subMenu.classList.add('active');
        animateHeight(subMenu, 0, height, () => {
            subMenu.style.height = 'auto';
            subMenu.classList.remove('animating');
        });
        
        if (dropdownIcon) {
            dropdownIcon.classList.add('rotate');
            // If it's a main menu, rotate also the parent icon
            const parentItem = subMenu.closest('.menu > .item');
            if (parentItem) {
                const parentIcon = parentItem.querySelector('.dropdown');
                if (parentIcon) {
                    parentIcon.classList.add('rotate');
                }
            }
        }
    }

    function closeSubMenu(subMenu, dropdownIcon) {
        if (!subMenu) return;
        
        const height = subMenu.scrollHeight;
        
        // Close child submenus first
        const childSubMenus = Array.from(subMenu.querySelectorAll('.sub-menu.active'));
        childSubMenus.forEach(childMenu => {
            const childDropdown = childMenu.previousElementSibling?.querySelector('.dropdown');
            closeSubMenu(childMenu, childDropdown);
        });
        
        animateHeight(subMenu, height, 0, () => {
            subMenu.classList.remove('active');
            subMenu.classList.remove('animating');
        });
        
        if (dropdownIcon) {
            dropdownIcon.classList.remove('rotate');
            // If it's a main menu, rotate also the parent icon
            const parentItem = subMenu.closest('.menu > .item');
            if (parentItem) {
                const parentIcon = parentItem.querySelector('.dropdown');
                const otherActiveSubMenus = Array.from(parentItem.querySelectorAll('.sub-menu.active'))
                    .filter(menu => menu !== subMenu);
                
                if (parentIcon && otherActiveSubMenus.length === 0) {
                    parentIcon.classList.remove('rotate');
                }
            }
        }
    }

    // Handle clicks on submenu buttons
    document.querySelectorAll(".sub-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            // If it's a real link (has href) and is not a submenu toggle
            const isLink = btn.getAttribute('href') && !btn.nextElementSibling;
            if (isLink) {
                // If it's a real link, allow navigation
                window.location.href = btn.getAttribute('href');
            } else {
                // If it's a submenu toggle, handle it normally
                toggleSubMenu(btn);
            }
        });
    });

    // Handle clicks on submenu items
    document.querySelectorAll(".sub-item").forEach(item => {
        item.addEventListener("click", (e) => {
            // Only stop propagation, not prevent default behavior
            e.stopPropagation();

            // Keep the sidebar open and parent menus expanded
            const parentMenus = item.closest('.sub-menu');
            if (parentMenus) {
                parentMenus.classList.add('keep-open');
            }
        });
    });

    // No need the global click listener since the overlay handles this
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sideBar.classList.contains('active')) {
            closeSidebar();
        }
    });
});