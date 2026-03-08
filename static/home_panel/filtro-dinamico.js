// Filtro dinámico con sugerencias y resaltado
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function resaltarCoincidencias(texto, filtro) {
  if (!filtro) return texto;
  const partes = filtro.trim().split(/\s+/).filter(Boolean);
  let resaltado = texto;
  partes.forEach(palabra => {
    if (palabra.length > 0) {
      const re = new RegExp('(' + escapeRegExp(palabra) + ')', 'gi');
      resaltado = resaltado.replace(re, '<span class="filtro-resaltado">$1</span>');
    }
  });
  return resaltado;
}

document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById('filtro-listado');
  if (!input) return;
  // Eliminar cualquier sugerencia flotante existente
  let sugerencias = document.getElementById('filtro-sugerencias');
  if (sugerencias) {
    sugerencias.remove();
  }

  // Obtener filas originales
  const tabla = document.querySelector('table');
  if (!tabla) return;
  const filasOriginales = Array.from(tabla.querySelectorAll('tbody tr'));

  input.addEventListener('input', function() {
    const filtro = this.value.trim().toLowerCase();
    if (!filtro) {
      filasOriginales.forEach(fila => fila.style.display = '');
      // Quitar resaltado
      filasOriginales.forEach(fila => {
        fila.innerHTML = fila.innerText;
      });
      return;
    }
    // Filtrar filas y resaltar coincidencias
    filasOriginales.forEach(fila => {
      if (fila.innerText.toLowerCase().includes(filtro)) {
        fila.style.display = '';
        // Resaltar coincidencias en la tabla
        Array.from(fila.children).forEach((td, idx) => {
          if (idx === fila.children.length - 1) return; // No resaltar acciones
          td.innerHTML = resaltarCoincidencias(td.innerText, filtro);
        });
      } else {
        fila.style.display = 'none';
      }
    });
  });

  input.addEventListener('blur', function() {
    setTimeout(() => { sugerencias.style.display = 'none'; }, 150);
  });
  input.addEventListener('focus', function() {
    if (sugerencias.innerHTML) sugerencias.style.display = 'block';
  });
});
