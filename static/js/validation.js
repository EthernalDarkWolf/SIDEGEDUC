// validation.js
// Manejador de eventos reutilizable para validaciones en tiempo real

/**
 * Valida la entrada de un campo según reglas definidas en data-attributes.
 * - data-rule: "numbers" | "letters" | "alphanumeric" (otros si es necesario)
 * - data-minlength / data-maxlength: límites de caracteres
 * - data-duplicate-group: nombre del grupo para chequear duplicados dentro del mismo formulario
 *
 * Se puede asociar directamente a los eventos `input` o `change` de los campos.
 * Ejemplo de uso:
 *   <input name="cedula" data-rule="numbers" data-minlength="7" data-maxlength="9" />
 *   <input name="primer_nombre" data-rule="letters" data-minlength="5" data-maxlength="10" data-duplicate-group="nombres" />
 *
 * La función bloquea físicamente caracteres inválidos y marca el borde en rojo con un
 * mensaje de error en caso de invalidación.
 */

(function(window, document) {
    'use strict';

    // Regexes base
    const regexMap = {
        numbers: /[^0-9]/g,
        letters: /[^a-zA-Z\u00C0-\u017F\s]/g, // incluye acentos y espacios
        alphanumeric: /[^a-zA-Z0-9\u00C0-\u017F\s]/g
    };

    /**
     * Crea (o recupera) un mensaje de error debajo del input.
     */
    function getErrorElement(input) {
        let err = input.nextElementSibling;
        if (!err || !err.classList.contains('validation-error')) {
            err = document.createElement('div');
            err.className = 'validation-error';
            err.style.color = 'red';
            err.style.fontSize = '0.85em';
            input.parentNode.insertBefore(err, input.nextSibling);
        }
        return err;
    }

    /**
     * Comprueba si un valor está dentro de los límites de longitud.
     */
    function checkLength(val, min, max) {
        if (min && val.length < min) return false;
        if (max && val.length > max) return false;
        return true;
    }

    /**
     * Controla que no haya duplicados en un grupo de campos dentro del mismo formulario.
     * Se ejecuta cada vez que cambia algún campo con data-duplicate-group.
     */
    function checkDuplicateWithinGroup(form, groupName) {
        const selector = `[data-duplicate-group="${groupName}"]`;
        const inputs = Array.from(form.querySelectorAll(selector));
        const values = inputs.map(i => i.value.trim().toLowerCase());
        inputs.forEach((input, idx) => {
            const val = values[idx];
            const err = getErrorElement(input);
            if (val && values.filter(v => v === val).length > 1) {
                input.style.borderColor = 'red';
                err.textContent = 'Valor duplicado en este grupo.';
            } else {
                // reaplicar otras reglas si existen
                err.textContent = '';
                input.style.borderColor = '';
            }
        });
    }

    /**
     * El manejador principal que se puede asociar a oninput/onchange.
     */
    function realTimeValidator(event) {
        const input = event.target;
        const rule = input.dataset.rule;
        const min = input.dataset.minlength ? parseInt(input.dataset.minlength, 10) : null;
        const max = input.dataset.maxlength ? parseInt(input.dataset.maxlength, 10) : null;
        const dupGroup = input.dataset.duplicateGroup;
        const form = input.form || document;

        let val = input.value;

        // eliminar caracteres prohibidos en vivo
        if (rule && regexMap[rule]) {
            const cleaned = val.replace(regexMap[rule], '');
            if (cleaned !== val) {
                val = cleaned;
                input.value = cleaned;
            }
        }

        // verificar longitud
        const errEl = getErrorElement(input);
        if (val && !checkLength(val, min, max)) {
            input.style.borderColor = 'red';
            errEl.textContent = 'No se permiten letras/números o caracteres especiales en este campo';
        } else {
            input.style.borderColor = '';
            errEl.textContent = '';
        }

        // si corresponde, chequear duplicados en el grupo
        if (dupGroup) {
            checkDuplicateWithinGroup(form, dupGroup);
        }
    }

    // Exponer la función globalmente para que pueda usarse en los formularios.
    window.realTimeValidator = realTimeValidator;

})(window, document);
