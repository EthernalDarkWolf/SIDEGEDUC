// Script para validar y loguear si el select está vacío
window.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('relacion');
    if (select && select.options.length <= 1) {
        console.log('La tabla de parentescos está vacía.');
    }
});
