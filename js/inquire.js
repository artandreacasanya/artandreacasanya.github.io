// Botones "Adquirir obra": además de abrir el programa de correo (mailto:), muestran debajo
// un aviso con un enlace al formulario de contacto (con el nombre de la obra ya escrito),
// por si el visitante no tiene ningún programa de correo configurado.
// El aviso desaparece solo a los 20 segundos o con la ×.
(function () {
    const en = document.documentElement.lang === 'en';
    // las páginas de obra están dentro de obras/
    const base = location.pathname.includes('/obras/') ? '../' : '';
    const contacto = base + (en ? 'contact-en.html' : 'contacto.html');

    document.querySelectorAll('.work-actions a.btn-inquire[href^="mailto:"]').forEach(link => {
        link.addEventListener('click', () => {
            const email = link.getAttribute('href').slice(7).split('?')[0];
            const actions = link.closest('.work-actions');
            const tituloEl = link.closest('.work-card')?.querySelector('.work-title strong')
                || document.querySelector('.obra-titulo');
            const titulo = tituloEl ? tituloEl.textContent.trim() : '';
            const formulario = `${contacto}?obra=${encodeURIComponent(titulo)}#formulario`;

            let note = actions.querySelector('.inquire-note');
            if (!note) {
                note = document.createElement('p');
                note.className = 'inquire-note';
                note.setAttribute('role', 'status');
                actions.appendChild(note);
            }

            const close = () => {
                note.classList.add('is-hiding');
                note.removeTimer = setTimeout(() => note.remove(), 400);
            };

            note.innerHTML = en
                ? `Didn’t your email open? Write to me using the <a href="${formulario}">contact form</a> or at <strong>${email}</strong>.`
                : `¿No se ha abierto tu correo? Escríbeme desde el <a href="${formulario}">formulario de contacto</a> o a <strong>${email}</strong>.`;
            note.insertAdjacentHTML('beforeend',
                ` <button type="button" class="inquire-note-close" aria-label="${en ? 'Close' : 'Cerrar'}">×</button>`);
            note.querySelector('.inquire-note-close').addEventListener('click', close);

            clearTimeout(note.hideTimer);
            clearTimeout(note.removeTimer);
            note.classList.remove('is-hiding');
            note.hideTimer = setTimeout(close, 20000);
        });
    });
})();
