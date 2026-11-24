// Filtros de la galería: disponibilidad (filtra) + precio o fecha (ordena).
// Precio, año y estado se leen del propio texto de cada ficha, así no hay que duplicarlos.
(function () {
    const grid = document.querySelector('.works-grid');
    const toggle = document.querySelector('.filter-toggle');
    const panel = document.getElementById('filter-panel');
    if (!grid || !toggle || !panel) return;

    const cards = [...grid.querySelectorAll('.work-card')].map((el, i) => {
        const texts = [...el.querySelectorAll('.work-info p')].map(p => p.textContent);
        const priceText = texts.find(t => t.includes('€')) || '';
        const yearText = texts.find(t => /\b(19|20)\d{2}\b/.test(t)) || '';
        return {
            el,
            // shortcut: con el mismo año, la posición en la página hace de fecha (la primera = la más antigua); añadir mes si hace falta más precisión
            order: i,
            price: parseFloat(priceText.replace(/[^\d,.]/g, '').replace(',', '.')) || 0,
            year: parseInt((yearText.match(/\b(19|20)\d{2}\b/) || [0])[0], 10),
            sold: !!el.querySelector('.status-sold'),
        };
    });

    // contador "13 de 14 disponibles": el texto de cada idioma está en data-template del HTML
    const counter = document.querySelector('.works-count');
    if (counter) {
        counter.textContent = counter.dataset.template
            .replace('{available}', cards.filter(c => !c.sold).length)
            .replace('{total}', cards.length);
    }

    const state = { filter: 'all', sort: null };

    const sorters = {
        'price-desc': (a, b) => b.price - a.price || a.order - b.order,
        'price-asc': (a, b) => a.price - b.price || a.order - b.order,
        'date-old': (a, b) => a.year - b.year || a.order - b.order,
        'date-new': (a, b) => b.year - a.year || b.order - a.order,
    };

    function apply() {
        const sorted = [...cards].sort(sorters[state.sort] || ((a, b) => a.order - b.order));
        sorted.forEach(c => {
            c.el.hidden = (state.filter === 'available' && c.sold) || (state.filter === 'sold' && !c.sold);
            grid.appendChild(c.el);
        });
        panel.querySelectorAll('[data-filter]').forEach(b => b.setAttribute('aria-pressed', b.dataset.filter === state.filter));
        panel.querySelectorAll('[data-sort]').forEach(b => b.setAttribute('aria-pressed', b.dataset.sort === state.sort));
    }

    function setOpen(open) {
        panel.hidden = !open;
        toggle.setAttribute('aria-expanded', open);
    }

    toggle.addEventListener('click', () => setOpen(panel.hidden));

    panel.addEventListener('click', e => {
        const b = e.target.closest('button');
        if (!b) return;
        if (b.dataset.filter) state.filter = b.dataset.filter;
        // pulsar de nuevo el orden activo lo quita y vuelve al orden original
        if (b.dataset.sort) state.sort = state.sort === b.dataset.sort ? null : b.dataset.sort;
        apply();
    });

    document.addEventListener('click', e => {
        if (!panel.hidden && !panel.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && !panel.hidden) { setOpen(false); toggle.focus(); }
    });

    apply();
})();
