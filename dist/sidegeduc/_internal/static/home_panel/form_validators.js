// shared input masking and validation utilities for registration forms
(function(){
    'use strict';

    // helpers -----------------------------------------------------------------
    function computeAgeFromDobString(dobStr){
        if(!dobStr) return NaN;
        var parts = dobStr.split('-');
        var dob;
        if(parts.length===3){
            var y = parseInt(parts[0],10), m=parseInt(parts[1],10)-1, d=parseInt(parts[2],10);
            dob = new Date(y,m,d);
        } else {
            parts = dobStr.split('/');
            if(parts.length===3){
                var d = parseInt(parts[0],10), m=parseInt(parts[1],10)-1, y=parseInt(parts[2],10);
                dob = new Date(y,m,d);
            } else {
                return NaN;
            }
        }
        var today = new Date();
        var age = today.getFullYear() - dob.getFullYear();
        var m2 = today.getMonth() - dob.getMonth();
        if(m2 < 0 || (m2 === 0 && today.getDate() < dob.getDate())) age--;
        return age;
    }

    function markInvalid(el, isInvalid){
        if(!el) return;
        if(isInvalid) el.classList.add('invalid');
        else el.classList.remove('invalid');
    }

    function showWittyNameMessage(){
        // mensagem especial cuando el usuario intenta meter números en nombres
        if(typeof showStatusModal === 'function'){
            showStatusModal('¡Buen intento!', '¡Buen intento! Pero los humanos usamos letras en nuestros nombres, no números.');
        }
    }

    // input masking -----------------------------------------------------------
    function onlyDigits(evt){
        if(evt.type === 'keydown'){
            if(evt.ctrlKey||evt.metaKey||evt.altKey) return;
            var k = evt.key;
            if(k && !/^\d$/.test(k)){
                evt.preventDefault();
            }
        } else if(evt.type === 'paste'){
            evt.preventDefault();
            var text = (evt.clipboardData || window.clipboardData).getData('text') || '';
            var digits = text.replace(/\D+/g,'');
            var el = evt.target;
            var start = el.selectionStart, end = el.selectionEnd;
            var newval = el.value.slice(0,start) + digits + el.value.slice(end);
            el.value = newval;
            el.dispatchEvent(new Event('input'));
        }
    }

    function onlyLetters(evt){
        if(evt.type === 'keydown'){
            if(evt.ctrlKey||evt.metaKey||evt.altKey) return;
            var k = evt.key;
            if(k && !/^[A-Za-záéíóúÁÉÍÓÚñÑ ]$/.test(k) && k.length === 1){
                evt.preventDefault();
                showWittyNameMessage();
            }
        } else if(evt.type === 'paste'){
            evt.preventDefault();
            var text = (evt.clipboardData || window.clipboardData).getData('text') || '';
            var letters = text.replace(/[^A-Za-záéíóúÁÉÍÓÚñÑ ]+/g,'');
            var el = evt.target;
            var start = el.selectionStart, end = el.selectionEnd;
            var newval = el.value.slice(0,start) + letters + el.value.slice(end);
            el.value = newval;
            el.dispatchEvent(new Event('input'));
        }
    }

    // field validators --------------------------------------------------------
    function validateCedula(el){
        if(!el) return false;
        var v = (el.value||'').trim();
        if(!/^\d+$/.test(v)) return false;
        return v.length >= 7 && v.length <= 9;
    }

    function validateName(el){
        if(!el) return false;
        var v = (el.value||'').trim();
        if(!v) return false;
        if(!/^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$/.test(v)) return false;
        return v.length >= 5 && v.length <= 10;
    }

    function validateDuplicates(){
        var pn = document.querySelector('input[name="primer_nombre"]');
        var sn = document.querySelector('input[name="segundo_nombre"]');
        var pa = document.querySelector('input[name="primer_apellido"]');
        var sa = document.querySelector('input[name="segundo_apellido"]');
        pn = pn ? pn.value.trim() : '';
        sn = sn ? sn.value.trim() : '';
        pa = pa ? pa.value.trim() : '';
        sa = sa ? sa.value.trim() : '';
        // compare pairwise
        if(pn && sn && pn === sn) return false;
        if(pn && pa && pn === pa) return false;
        if(pn && sa && pn === sa) return false;
        if(sn && pa && sn === pa) return false;
        if(sn && sa && sn === sa) return false;
        if(pa && sa && pa === sa) return false;
        return true;
    }

    function validateAge(){
        var dobEl = document.getElementById('fecha_nacimiento');
        var tipoEl = document.getElementById('tipo_persona');
        if(!dobEl || !dobEl.value || !tipoEl) return true;
        var age = computeAgeFromDobString(dobEl.value);
        var tipo = tipoEl.value;
        if(tipo === 'estudiante'){
            return age >= 3 && age <= 18;
        }
        if(tipo === 'representante' || tipo === 'profesor'){
            return age >= 18;
        }
        return true;
    }

    // public helpers for each form -------------------------------------------
    function updatePersonaSubmitState(){
        var form = document.getElementById('personaForm');
        if(!form) return;
        var valid = true;
        // cedula
        var ced = form.querySelector('input[name="numero_cedula"]');
        if(ced){
            var ok = validateCedula(ced);
            markInvalid(ced, !ok);
            if(!ok) valid = false;
        }
        // nombres/apellidos
        ['primer_nombre','segundo_nombre','primer_apellido','segundo_apellido'].forEach(function(name){
            var el = form.querySelector('input[name="'+name+'"]');
            if(el && el.value.trim()){
                var ok = validateName(el);
                markInvalid(el, !ok);
                if(!ok) valid = false;
            }
        });
        // duplicados
        if(!validateDuplicates()){
            valid = false;
            // mark all four fields invalid to draw user attention
            ['primer_nombre','segundo_nombre','primer_apellido','segundo_apellido'].forEach(function(name){
                var el = form.querySelector('input[name="'+name+'"]');
                if(el) markInvalid(el, true);
            });
        }
        // edad/rol
        if(!validateAge()){
            valid = false;
            var dobEl = document.getElementById('fecha_nacimiento');
            markInvalid(dobEl, true);
        } else {
            var dobEl = document.getElementById('fecha_nacimiento');
            markInvalid(dobEl, false);
        }
        // enable/disable button
        var btn = form.querySelector('button[type="submit"]');
        if(btn){
            btn.disabled = !valid;
            if(btn.disabled){
                btn.dataset.origText = btn.textContent;
                btn.textContent = 'Corrige errores para continuar';
            } else {
                if(btn.dataset.origText) btn.textContent = btn.dataset.origText;
            }
        }
    }

    function updatePlantelSubmitState(){
        var form = document.getElementById('plantelForm');
        if(!form) return;
        var valid = true;
        var code = form.querySelector('input[name="codigo_pa"]');
        if(code){
            var v = (code.value||'').trim();
            var ok = /^\d+$/.test(v) && v.length > 0;
            markInvalid(code, !ok);
            if(!ok) valid = false;
        }
        var name = form.querySelector('input[name="nombre_plantel_nomina"]');
        if(name){
            var nv = (name.value||'').trim();
            var okName = nv.length > 0 && /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/.test(nv);
            markInvalid(name, !okName);
            if(!okName) valid = false;
        }
        var btn = form.querySelector('button[type="submit"]');
        if(btn){
            btn.disabled = !valid;
            if(btn.disabled){
                btn.dataset.origText = btn.textContent;
                btn.textContent = 'Corrige errores para continuar';
            } else {
                if(btn.dataset.origText) btn.textContent = btn.dataset.origText;
            }
        }
    }

    // hook up events once the DOM is ready
    document.addEventListener('DOMContentLoaded', function(){
        document.querySelectorAll('input[data-rule="numbers"]').forEach(function(el){
            el.addEventListener('keydown', onlyDigits);
            el.addEventListener('paste', onlyDigits);
            el.addEventListener('input', function(){
                updatePersonaSubmitState();
                updatePlantelSubmitState();
            });
        });
        document.querySelectorAll('input[data-rule="letters"]').forEach(function(el){
            el.addEventListener('keydown', onlyLetters);
            el.addEventListener('paste', onlyLetters);
            el.addEventListener('input', function(){
                updatePersonaSubmitState();
                updatePlantelSubmitState();
            });
        });
        var personaForm = document.getElementById('personaForm');
        if(personaForm){
            personaForm.addEventListener('input', updatePersonaSubmitState);
            updatePersonaSubmitState();
        }
        var plantelForm = document.getElementById('plantelForm');
        if(plantelForm){
            plantelForm.addEventListener('input', updatePlantelSubmitState);
            updatePlantelSubmitState();
        }
    });

})();