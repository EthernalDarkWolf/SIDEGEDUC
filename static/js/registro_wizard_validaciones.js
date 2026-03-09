// Validación y lógica para el paso de datos personales

document.addEventListener('DOMContentLoaded', function() {
    const nombre1 = document.getElementById('nombre1');
    const nombre2 = document.getElementById('nombre2');
    const apellido1 = document.getElementById('apellido1');
    const apellido2 = document.getElementById('apellido2');
    const fechaNacimiento = document.getElementById('fecha_nacimiento');
    const tipoCedula = document.getElementById('tipo_cedula');
    const btnSig = document.getElementById('btnSig');
    const wizardTipoPersona = document.getElementById('wizard_tipo_persona').value.toLowerCase();

    function calcularEdad(fecha) {
        const hoy = new Date();
        const nacimiento = new Date(fecha);
        let edad = hoy.getFullYear() - nacimiento.getFullYear();
        const m = hoy.getMonth() - nacimiento.getMonth();
        if (m < 0 || (m === 0 && hoy.getDate() < nacimiento.getDate())) {
            edad--;
        }
        return edad;
    }

    function setError(element, message) {
        element.classList.add('error-border');
        const id = element.id;
        const msgDiv = document.getElementById('error-' + id);
        if (msgDiv) msgDiv.textContent = message;
    }

    function clearError(element) {
        element.classList.remove('error-border');
        const id = element.id;
        const msgDiv = document.getElementById('error-' + id);
        if (msgDiv) msgDiv.textContent = '';
    }

    function validarLongitud(element, required = true) {
        const value = element.value.trim();
        clearError(element);
        if (!value) {
            if (required) {
                setError(element, 'Este campo es obligatorio');
                return false;
            }
            return true; // empty but not required
        }
        if (value.length < 3 || value.length > 11) {
            setError(element, 'Debe tener entre 3 y 11 letras');
            return false;
        }
        return true;
    }

    function validarEspejo() {
        // Check if any nombre equals any apellido
        const nombres = [nombre1.value.trim().toLowerCase(), nombre2.value.trim().toLowerCase()].filter(v => v);
        const apellidos = [apellido1.value.trim().toLowerCase(), apellido2.value.trim().toLowerCase()].filter(v => v);
        let hasDuplicate = false;
        nombres.forEach(n => {
            apellidos.forEach(a => {
                if (n && a && n === a) {
                    // Mark both fields
                    if (nombre1.value.trim().toLowerCase() === n) setError(nombre1, 'Error: Los nombres y apellidos no pueden ser iguales');
                    if (nombre2.value.trim().toLowerCase() === n) setError(nombre2, 'Error: Los nombres y apellidos no pueden ser iguales');
                    if (apellido1.value.trim().toLowerCase() === a) setError(apellido1, 'Error: Los nombres y apellidos no pueden ser iguales');
                    if (apellido2.value.trim().toLowerCase() === a) setError(apellido2, 'Error: Los nombres y apellidos no pueden ser iguales');
                    hasDuplicate = true;
                }
            });
        });
        return !hasDuplicate;
    }

    function validarFecha() {
        clearError(fechaNacimiento);
        if (!fechaNacimiento.value) {
            setError(fechaNacimiento, 'La fecha es obligatoria');
            return false;
        }
        const edad = calcularEdad(fechaNacimiento.value);
        if (wizardTipoPersona === 'representante') {
            if (edad < 18 || edad > 65) {
                setError(fechaNacimiento, 'El representante debe ser mayor de edad (máx 65 años)');
                return false;
            }
        }
        return true;
    }

    function actualizarTipoCedula() {
        if (fechaNacimiento.value) {
            const edad = calcularEdad(fechaNacimiento.value);
            if (edad < 18) {
                tipoCedula.value = 'Menor';
            } else {
                tipoCedula.value = 'Adulto';
            }
        } else {
            tipoCedula.value = '';
        }
    }

    function validarForm() {
        // Clear all first
        [nombre1, nombre2, apellido1, apellido2].forEach(clearError);
        clearError(fechaNacimiento);
        let valid = true;
        valid = valid && validarLongitud(nombre1, true);
        valid = valid && validarLongitud(nombre2, false);
        valid = valid && validarLongitud(apellido1, true);
        valid = valid && validarLongitud(apellido2, false);
        valid = valid && validarEspejo();
        valid = valid && validarFecha();
        // Update tipo cedula
        actualizarTipoCedula();
        btnSig.disabled = !valid;
    }

    // Attach listeners
    [nombre1, nombre2, apellido1, apellido2].forEach(el => {
        el.addEventListener('input', validarForm);
    });
    fechaNacimiento.addEventListener('change', function() {
        actualizarTipoCedula();
        validarForm();
    });

    // Initial validation
    validarForm();
});
