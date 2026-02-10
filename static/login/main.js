// Interacciones para la pantalla de login: alternar pestañas, mostrar/ocultar contraseña y validación ligera
(function(){
    function togglePassword(btn){
        const container = btn.closest('.password-field');
        if(!container) return;
        const input = container.querySelector('input[type="password"], input[type="text"]');
        if(!input) return;
        if(input.type === 'password'){
            input.type = 'text';
            btn.setAttribute('aria-label','Ocultar contraseña');
            btn.classList.add('active');
        } else {
            input.type = 'password';
            btn.setAttribute('aria-label','Mostrar contraseña');
            btn.classList.remove('active');
        }
        input.focus();
    }

    function setActiveTab(tab){
        // mirrors inline function but using class toggles so transitions apply
        const loginTab = document.getElementById('tab-login');
        const regTab = document.getElementById('tab-register');
        const panelLogin = document.getElementById('panel-login');
        const panelReg = document.getElementById('panel-register');
        if(!panelLogin || !panelReg) return;
        if(tab === 'register'){
            loginTab && loginTab.classList.remove('active');
            regTab && regTab.classList.add('active');
            panelLogin.classList.add('hidden');
            panelReg.classList.remove('hidden');
        } else {
            regTab && regTab.classList.remove('active');
            loginTab && loginTab.classList.add('active');
            panelReg.classList.add('hidden');
            panelLogin.classList.remove('hidden');
        }
    }

    document.addEventListener('DOMContentLoaded', function(){
        // wire pw toggles
        document.querySelectorAll('.pw-toggle').forEach(function(btn){
            btn.addEventListener('click', function(e){ togglePassword(btn); });
        });

        // enhance tab buttons to use transitions
        const tLogin = document.getElementById('tab-login');
        const tReg = document.getElementById('tab-register');
        if(tLogin) tLogin.addEventListener('click', ()=>setActiveTab('login'));
        if(tReg) tReg.addEventListener('click', ()=>setActiveTab('register'));

        // link anchors already present: ensure they call our tab sets
        const lShowReg = document.getElementById('link-show-register');
        const lShowLogin = document.getElementById('link-show-login');
        if(lShowReg) lShowReg.addEventListener('click', (e)=>{e.preventDefault(); setActiveTab('register'); document.getElementById('reg-usuario').focus();});
        if(lShowLogin) lShowLogin.addEventListener('click', (e)=>{e.preventDefault(); setActiveTab('login'); document.getElementById('usuario').focus();});

        // lightweight form validation: show modal if required fields empty
        document.querySelectorAll('form').forEach(function(form){
            form.addEventListener('submit', function(e){
                const required = form.querySelectorAll('[required]');
                for(let i=0;i<required.length;i++){
                    const el = required[i];
                    if(el.type === 'checkbox'){
                        if(!el.checked){
                            e.preventDefault();
                            if(typeof showModal === 'function') showModal('Atención','Debe aceptar los términos antes de continuar.');
                            el.focus();
                            return false;
                        }
                    } else if(!el.value || !String(el.value).trim()){
                        e.preventDefault();
                        if(typeof showModal === 'function') showModal('Atención','Completa todos los campos requeridos.');
                        el.focus();
                        return false;
                    }
                }
                // allow submit to proceed if all good
            });
        });

        // set initial active based on existing inline server variable if present
        try{
            // inline template may set `active` var; if not, default handled server-side
            if(typeof active !== 'undefined'){
                setActiveTab(active);
            }
        }catch(e){ /* ignore */ }

        // small parallax on mouse move for hero (if present)
        const hero = document.querySelector('.hero .overlay');
        if(hero){
            document.querySelector('.hero').addEventListener('mousemove', function(ev){
                const rect = this.getBoundingClientRect();
                const x = (ev.clientX - rect.left)/rect.width - 0.5;
                const y = (ev.clientY - rect.top)/rect.height - 0.5;
                hero.style.transform = `translate(${x*6}px, ${y*6}px)`;
            });
            document.querySelector('.hero').addEventListener('mouseleave', function(){ hero.style.transform = ''; });
        }
    });
})();
