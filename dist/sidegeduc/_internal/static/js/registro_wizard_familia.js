// Validación ligera y habilitación del botón "Siguiente" para el paso de familia del wizard

document.addEventListener('DOMContentLoaded', function() {
    const cedula = document.getElementById('cedula');
    const numHijos = document.getElementById('num_hijos');
    const relacion = document.getElementById('relacion_familiar');
    const btn = document.getElementById('btn_siguiente');

    if (!cedula || !numHijos || !relacion || !btn) return;

    function validarCedula(valor) {
        // Ejemplo: cédula venezolana (7-8 dígitos)
        return /^\d{7,8}$/.test(valor);
    }

    function validar() {
        const cedulaValida = validarCedula(cedula.value);
        const hijosValidos = parseInt(numHijos.value, 10) >= 1;
        const relacionValida = relacion.value !== "";
        if (cedulaValida && hijosValidos && relacionValida) {
            btn.disabled = false;
            btn.classList.add('btn-activo');
        } else {
            btn.disabled = true;
            btn.classList.remove('btn-activo');
        }
    }

    cedula.addEventListener('input', validar);
    numHijos.addEventListener('input', validar);
    relacion.addEventListener('change', validar);

    // Inicializar estado del botón
    validar();
});
