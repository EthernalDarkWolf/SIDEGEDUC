// Control de interacción en la página de registro de secciones.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('createSectionForm');
    const alertBox = document.getElementById('sectionFormAlert');
    const btnCreate = document.getElementById('btnCreateSection');
    const spinner = btnCreate ? btnCreate.querySelector('.spinner-border') : null;
    const modalEl = document.getElementById('createSectionModal');
    const devModalEl = document.getElementById('devModal');
    const devModalBody = document.getElementById('devModalBody');
    const sectionTableBody = document.getElementById('sectionsTableBody');

    const sectionData = Array.isArray(window.SECCIONES_INITIAL) ? window.SECCIONES_INITIAL : [];

    function showAlert(type, message) {
        if (!alertBox) return;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        alertBox.textContent = message;
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close';
        closeBtn.setAttribute('data-bs-dismiss', 'alert');
        closeBtn.setAttribute('aria-label', 'Cerrar');
        alertBox.appendChild(closeBtn);
        alertBox.classList.remove('d-none');
    }

    function hideAlert() {
        if (!alertBox) return;
        alertBox.classList.add('d-none');
        alertBox.textContent = '';
    }

    function createRow(section) {
        const tr = document.createElement('tr');
        const tdNivel = document.createElement('td');
        const tdGrado = document.createElement('td');
        const tdLetra = document.createElement('td');

        tdNivel.textContent = section.nombre_nivel || section.id_nivel || '—';
        tdGrado.textContent = section.numero_grado || section.id_grado || '—';
        tdLetra.textContent = section.letra || section.id_letra_seccion || '—';

        tr.appendChild(tdNivel);
        tr.appendChild(tdGrado);
        tr.appendChild(tdLetra);
        return tr;
    }

    function addSectionRow(section) {
        if (!sectionTableBody) return;
        // Remove placeholder row if present
        const placeholder = sectionTableBody.querySelector('tr td[colspan]');
        if (placeholder) placeholder.closest('tr').remove();
        sectionTableBody.appendChild(createRow(section));
    }

    function isDuplicate({ id_nivel, id_grado, id_letra_seccion }) {
        return sectionData.some(s => String(s.id_nivel) === String(id_nivel)
            && String(s.id_grado) === String(id_grado)
            && String(s.id_letra_seccion) === String(id_letra_seccion));
    }

    function showDevModal(message) {
        if (!devModalEl || !devModalBody) {
            alert(message);
            return;
        }
        devModalBody.textContent = message;
        const modal = new bootstrap.Modal(devModalEl);
        modal.show();
    }

    document.querySelectorAll('.action-card').forEach(card => {
        card.addEventListener('click', () => {
            const action = card.getAttribute('data-action') || 'Esta acción';
            if (action === 'create_section' && modalEl) {
                const modal = new bootstrap.Modal(modalEl);
                hideAlert();
                if (form) form.reset();
                if (form) form.classList.remove('was-validated');
                modal.show();
                return;
            }
            showDevModal(`${action} está en desarrollo.`);
        });
    });

    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        hideAlert();

        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const payload = {
            id_nivel: form.id_nivel.value,
            id_grado: form.id_grado.value,
            id_letra_seccion: form.id_letra_seccion.value
        };

        if (isDuplicate(payload)) {
            showAlert('warning', 'La sección ya existe. Verifica los valores seleccionados.');
            return;
        }

        if (btnCreate) btnCreate.disabled = true;
        if (spinner) spinner.classList.remove('d-none');

        try {
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            let data;
            try {
                data = await response.json();
            } catch {
                data = null;
            }

            if (data && data.success) {
                showAlert('success', data.message || 'Sección creada correctamente.');
                sectionData.push(payload);
                addSectionRow({
                    ...payload,
                    nombre_nivel: form.id_nivel.selectedOptions[0]?.text,
                    numero_grado: form.id_grado.selectedOptions[0]?.text,
                    letra: form.id_letra_seccion.selectedOptions[0]?.text
                });
                if (modalEl) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    setTimeout(() => modal?.hide(), 800);
                }
                form.reset();
            } else {
                const message = data?.message || 'No se pudo crear la sección. Intenta de nuevo.';
                showAlert('danger', message);
            }
        } catch (err) {
            showAlert('danger', 'Error de red. Verifica tu conexión y vuelve a intentar.');
        } finally {
            if (btnCreate) btnCreate.disabled = false;
            if (spinner) spinner.classList.add('d-none');
        }
    });
});
