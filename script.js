document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Loaded');
    const menuElements = document.querySelectorAll('.menuElementContainer');

    menuElements.forEach(element => {
        element.addEventListener('click', () => {
            console.log('Clicked on:', element);
            // Remove 'active' class from all elements
            menuElements.forEach(el => el.classList.remove('active'));

            // Add 'active' class to the clicked element
            element.classList.add('active');
        });
    });
});