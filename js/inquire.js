// Botones "Adquirir obra": además de abrir el programa de correo (mailto:),
// copian la dirección y la muestran debajo del botón, por si el visitante
// no tiene ningún programa de correo configurado (p. ej. usa Gmail en el navegador).
(function () {
    const en = document.documentElement.lang === 'en';

    document.querySelectorAll('.work-actions a.btn-inquire[href^="mailto:"]').forEach(link => {
        link.addEventListener('click', () => {
            const email = link.getAttribute('href').slice(7).split('?')[0];
            const actions = link.closest('.work-actions');
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

            const show = copied => {
                note.innerHTML = (en ? 'Didn’t your email open? Write to me at ' : '¿No se ha abierto tu correo? Escríbeme a ')
                    + '<strong>' + email + '</strong>'
                    + (copied ? (en ? ' (address copied).' : ' (dirección copiada).') : '.')
                    + ' <button type="button" class="inquire-note-close" aria-label="' + (en ? 'Close' : 'Cerrar') + '">×</button>';
                note.querySelector('.inquire-note-close').addEventListener('click', close);
            };

            show(false);
            // desaparece sola a los 15 segundos (si se vuelve a pulsar el botón, se reinicia la cuenta)
            clearTimeout(note.hideTimer);
            clearTimeout(note.removeTimer);
            note.classList.remove('is-hiding');
            note.hideTimer = setTimeout(close, 15000);
            if (navigator.clipboard) {
                navigator.clipboard.writeText(email).then(() => show(true), () => {});
            }
        });
    });
})();
