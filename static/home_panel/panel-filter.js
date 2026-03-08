// Lógica de filtrado para el panel de control
// Puedes adaptar la fuente de datos según tu backend o frontend

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('panel-filter-input');
    const suggestions = document.getElementById('panel-filter-suggestions');

    // Ejemplo de datos (puedes reemplazar por AJAX)
    const data = [
        { tipo: 'Estudiante', nombre: 'Juan Pérez', url: '/consultas/personas/list?role=estudiante' },
        { tipo: 'Profesor', nombre: 'Ana Gómez', url: '/consultas/personas/list?role=profesor' },
        { tipo: 'Representante', nombre: 'Carlos Ruiz', url: '/consultas/personas/list?role=representante' },
        { tipo: 'Empleado', nombre: 'María López', url: '/consultas/personas/list?role=empleado' },
        // ...puedes agregar más ejemplos o cargar dinámicamente
    ];

    input.addEventListener('input', function() {
        const value = this.value.trim().toLowerCase();
        if (!value) {
            suggestions.style.display = 'none';
            suggestions.innerHTML = '';
            return;
        }
        // Filtrar por nombre o tipo
        const filtered = data.filter(item =>
            item.nombre.toLowerCase().includes(value) ||
            item.tipo.toLowerCase().includes(value)
        ).slice(0, 5); // máximo 5 sugerencias

        if (filtered.length === 0) {
            suggestions.style.display = 'none';
            suggestions.innerHTML = '';
            return;
        }
        suggestions.innerHTML = filtered.map(item =>
            `<a href="${item.url}" class="list-group-item list-group-item-action">${item.tipo}: ${item.nombre}</a>`
        ).join('');
        suggestions.style.display = 'block';
    });

    // Ocultar sugerencias al perder foco
    input.addEventListener('blur', function() {
        setTimeout(() => { suggestions.style.display = 'none'; }, 150);
    });
    input.addEventListener('focus', function() {
        if (suggestions.innerHTML) suggestions.style.display = 'block';
    });
});
