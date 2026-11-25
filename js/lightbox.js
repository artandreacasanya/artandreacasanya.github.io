// Visor de obras: al pulsar una foto se ve en grande, con su título y ficha.
// Se pasa de obra con las flechas (teclado o pantalla) o deslizando el dedo en el móvil.
// Solo recorre las obras visibles y en el orden actual (respeta los filtros).
(function () {
    const grid = document.querySelector('.works-grid');
    if (!grid) return;

    const en = document.documentElement.lang === 'en';
    const t = en
        ? { close: 'Close', prev: 'Previous work', next: 'Next work', open: 'View larger', of: 'of', viewer: 'Work viewer' }
        : { close: 'Cerrar', prev: 'Obra anterior', next: 'Obra siguiente', open: 'Ver en grande', of: 'de', viewer: 'Visor de obras' };

    // --- estructura del visor ---
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.hidden = true;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', t.viewer);
    box.innerHTML = `
        <button type="button" class="lightbox-btn lightbox-close" aria-label="${t.close}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>
        </button>
        <button type="button" class="lightbox-btn lightbox-prev" aria-label="${t.prev}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4l-8 8 8 8"/></svg>
        </button>
        <figure class="lightbox-figure">
            <img class="lightbox-img" alt="">
            <figcaption class="lightbox-caption">
                <span class="lightbox-title"></span>
                <span class="lightbox-details"></span>
                <span class="lightbox-counter"></span>
            </figcaption>
        </figure>
        <button type="button" class="lightbox-btn lightbox-next" aria-label="${t.next}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4l8 8-8 8"/></svg>
        </button>`;
    document.body.appendChild(box);

    const img = box.querySelector('.lightbox-img');
    const figure = box.querySelector('.lightbox-figure');
    const titleEl = box.querySelector('.lightbox-title');
    const detailsEl = box.querySelector('.lightbox-details');
    const counterEl = box.querySelector('.lightbox-counter');
    const prevBtn = box.querySelector('.lightbox-prev');
    const nextBtn = box.querySelector('.lightbox-next');

    let list = [];      // obras visibles en el orden actual
    let index = 0;
    let lastFocus = null;
    let isOpen = false;
    let revealTimer = null;

    const visibleCards = () => [...grid.querySelectorAll('.work-card')].filter(c => !c.hidden);

    // título y ficha (técnica · medidas · año) se leen de la propia tarjeta
    function describe(card) {
        const title = card.querySelector('.work-title strong')?.textContent.trim() || '';
        const details = [...card.querySelectorAll('.work-info > p:not([class]) strong')]
            .map(s => s.textContent.trim())
            .filter(s => !s.includes('€'));
        const sold = card.querySelector('.status-text')?.textContent.trim();
        if (sold) details.push(sold);
        return { title, details: details.join(' · ') };
    }

    function show(i) {
        index = (i + list.length) % list.length;
        const card = list[index];
        const source = card.querySelector('.work-image');
        const info = describe(card);

        const swap = () => {
            img.src = source.currentSrc || source.src;
            img.alt = source.alt;
            titleEl.textContent = info.title;
            detailsEl.textContent = info.details;
            counterEl.textContent = `${index + 1} ${t.of} ${list.length}`;
            const reveal = () => { clearTimeout(revealTimer); figure.classList.remove('is-changing'); };
            img.onload = reveal;
            if (img.complete) reveal();
            revealTimer = setTimeout(reveal, 800);   // por seguridad: nunca se queda oculta
        };
        if (isOpen) {
            figure.classList.add('is-changing');
            setTimeout(swap, 180);
        } else {
            swap();
        }

        const single = list.length < 2;
        prevBtn.hidden = single;
        nextBtn.hidden = single;
    }

    function open(card) {
        list = visibleCards();
        lastFocus = document.activeElement;
        box.classList.remove('is-closing');
        box.hidden = false;
        document.documentElement.classList.add('lightbox-lock');
        show(list.indexOf(card));
        isOpen = true;
        box.querySelector('.lightbox-close').focus();
    }

    function close() {
        isOpen = false;
        box.classList.add('is-closing');
        document.documentElement.classList.remove('lightbox-lock');
        setTimeout(() => {
            if (isOpen) return;   // se volvió a abrir mientras se cerraba
            box.hidden = true;
            box.classList.remove('is-closing');
            img.removeAttribute('src');
        }, 300);
        if (lastFocus) lastFocus.focus();
    }

    // --- abrir: clic (o Enter) en la foto de una obra ---
    grid.querySelectorAll('.work-card .work-image').forEach(image => {
        image.setAttribute('tabindex', '0');
        image.setAttribute('role', 'button');
        image.setAttribute('aria-label', `${t.open}: ${image.alt}`);
        image.addEventListener('click', () => open(image.closest('.work-card')));
        image.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(image.closest('.work-card')); }
        });
    });

    // --- controles ---
    box.querySelector('.lightbox-close').addEventListener('click', close);
    prevBtn.addEventListener('click', () => show(index - 1));
    nextBtn.addEventListener('click', () => show(index + 1));

    // clic en el fondo (fuera de la foto y de los botones) cierra
    box.addEventListener('click', e => {
        if (e.target === box || e.target === figure) close();
    });

    document.addEventListener('keydown', e => {
        if (box.hidden) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft') show(index - 1);
        else if (e.key === 'ArrowRight') show(index + 1);
        else if (e.key === 'Tab') {
            // mantener el foco dentro del visor
            const items = [...box.querySelectorAll('button:not([hidden])')];
            const first = items[0], last = items[items.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    });

    // deslizar en el móvil
    let startX = null, startY = null;
    box.addEventListener('touchstart', e => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    }, { passive: true });
    box.addEventListener('touchend', e => {
        if (startX === null) return;
        const dx = e.changedTouches[0].clientX - startX;
        const dy = e.changedTouches[0].clientY - startY;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1));
        else if (dy > 90 && Math.abs(dy) > Math.abs(dx)) close();   // deslizar hacia abajo cierra
        startX = startY = null;
    });
})();
