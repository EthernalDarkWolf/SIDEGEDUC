document.addEventListener('DOMContentLoaded', function(){
    console.log('form-controls.js loaded, attaching validators');
    // Form controls helper: normalize date inputs display (DD/MM/YYYY helper)
    function formatDateYYYYtoDDMMYYYY(val){
        if(!val) return '';
        // val expected 'YYYY-MM-DD'
        const parts = val.split('-');
        if(parts.length !== 3) return val;
        return parts[2] + '/' + parts[1] + '/' + parts[0];
    }

    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // wrap input in .date-field if not already
        if(!input.closest('.date-field')){
            const wrapper = document.createElement('div');
            wrapper.className = 'date-field';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            // add calendar icon
            const icon = document.createElement('span');
            icon.className = 'date-icon';
            icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none"><path d="M7 11h5v5H7z" fill="currentColor" opacity=".08"></path><path d="M7 11h5v5H7z" stroke="currentColor" stroke-width="0"></path><path d="M17 3v2M7 3v2M3 7h18M21 21H3V7h18v14z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>';
            wrapper.appendChild(icon);

            // add helper text under input
            const help = document.createElement('span');
            help.className = 'date-helper';
            const formatted = formatDateYYYYtoDDMMYYYY(input.value);
            help.textContent = formatted || 'DD/MM/AAAA';
            wrapper.appendChild(help);

            // update helper on change
            input.addEventListener('input', function(){
                help.textContent = formatDateYYYYtoDDMMYYYY(this.value) || 'DD/MM/AAAA';
            });

            // on focus, hint placeholder style
            input.addEventListener('focus', function(){
                help.style.opacity = '0.9';
            });
            input.addEventListener('blur', function(){
                help.style.opacity = '0.8';
            });
        }
    });

    // Also support inputs with data-type="date" (if some templates use text-backed date controls)
    const fakeDateInputs = document.querySelectorAll('input[data-type="date"]');
    fakeDateInputs.forEach(input => {
        if(!input.closest('.date-field')){
            const wrapper = document.createElement('div');
            wrapper.className = 'date-field';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            const icon = document.createElement('span');
            icon.className = 'date-icon';
            icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none"><path d="M7 11h5v5H7z" fill="currentColor" opacity=".08"></path><path d="M7 11h5v5H7z" stroke="currentColor" stroke-width="0"></path><path d="M17 3v2M7 3v2M3 7h18M21 21H3V7h18v14z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>';
            wrapper.appendChild(icon);

            const help = document.createElement('span');
            help.className = 'date-helper';
            help.textContent = input.getAttribute('placeholder') || 'DD/MM/AAAA';
            wrapper.appendChild(help);

            // If the input value is in YYYY-MM-DD, convert and show
            input.addEventListener('input', function(){
                // try to parse
                const v = this.value;
                const maybe = formatDateYYYYtoDDMMYYYY(v);
                help.textContent = maybe || this.getAttribute('placeholder') || 'DD/MM/AAAA';
            });
        }
    });
    
    // Also support inputs with data-flatpickr (we add icon and helper for UX)
    const flatpickrInputs = document.querySelectorAll('input[data-flatpickr]');
    flatpickrInputs.forEach(input => {
        if(!input.closest('.date-field')){
            const wrapper = document.createElement('div');
            wrapper.className = 'date-field';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            // calendar icon
            const icon = document.createElement('span');
            icon.className = 'date-icon';
            icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none"><path d="M7 11h5v5H7z" fill="currentColor" opacity=".08"></path><path d="M17 3v2M7 3v2M3 7h18M21 21H3V7h18v14z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>';
            wrapper.appendChild(icon);

            const help = document.createElement('span');
            help.className = 'date-helper';
            help.textContent = input.getAttribute('placeholder') || 'DD/MM/AAAA';
            wrapper.appendChild(help);

            // clicking icon focuses input (opens calendar)
            icon.addEventListener('click', function(){ input.focus(); input.click(); });
        }
    });

    // generic input validation (letters vs numbers, uppercase first letter, red highlight)
    function setupFieldValidators(){
        const nameBasedLetters = /nombre|apellido|razon|direccion|lugar|ciudad|estado|municipio|titulo/i;
        const nameBasedNumbers = /cedula|numero|tel|edad|hijos|matricula|codigo|cantidad|anio|ano|id_/i;

        document.querySelectorAll('input:not(.no-validation)').forEach(function(input){
            let isLetters = false;
            let isNumbers = false;

            if(input.pattern){
                if(/[A-Za-zÀ-ÖØ-öø-ÿ]/.test(input.pattern)) isLetters = true;
                if(/[0-9\\d]/.test(input.pattern)) isNumbers = true;
            }
            if(input.type === 'number'){
                isNumbers = true;
            }
            if(nameBasedLetters.test(input.name)){
                isLetters = true;
            }
            if(nameBasedNumbers.test(input.name)){
                isNumbers = true;
            }
            // if both detected, give up (ambiguous)
            if(isLetters && isNumbers){
                isLetters = isNumbers = false;
            }

            if(isLetters || isNumbers){
                console.log('validator attach:', input.name, 'letters=', isLetters, 'numbers=', isNumbers);
                const sanitize = function(val){
                    let out = val;
                    if(isLetters){
                        out = out.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ ]/g,'');
                    }
                    if(isNumbers){
                        out = out.replace(/\D/g,'');
                    }
                    return out;
                };

                input.addEventListener('input', function(){
                    const v = this.value;
                    const clean = sanitize(v);
                    if(clean !== v){
                        this.value = clean;
                        addError(this, isLetters ? 'solo letras' : 'solo números');
                    } else {
                        clearError(this);
                    }
                });

                input.addEventListener('blur', function(){
                    if(isLetters && this.value){
                        // uppercase first letter of each word
                        this.value = this.value.split(/\s+/).map(w=> w? w.charAt(0).toUpperCase()+w.slice(1).toLowerCase(): '').join(' ');
                    }
                });
            }
        });
    }

    function addError(input, msg){
        input.classList.add('invalid');
        input.setAttribute('title', msg);
        let span = input.nextElementSibling;
        if(!span || !span.classList.contains('validation-error')){
            span = document.createElement('small');
            span.className = 'validation-error';
            input.parentNode.insertBefore(span, input.nextSibling);
        }
        span.textContent = msg;
    }

    function clearError(input){
        input.classList.remove('invalid');
        input.removeAttribute('title');
        let span = input.nextElementSibling;
        if(span && span.classList.contains('validation-error')){
            span.remove();
        }
    }

    setupFieldValidators();
});
