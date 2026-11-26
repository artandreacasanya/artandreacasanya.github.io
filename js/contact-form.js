// Formulario de contacto (contacto.html / contact-en.html).
// - Si se llega desde una obra (contacto.html?obra=Pont%20Neuf#formulario), deja el mensaje empezado.
// - Después de enviar, FormSubmit devuelve a la visitante a ?enviado=1: se muestra el agradecimiento.
(function () {
    const wrap = document.getElementById('formulario');
    if (!wrap) return;

    const form = wrap.querySelector('.contact-form');
    const sent = wrap.querySelector('.form-sent');
    const params = new URLSearchParams(location.search);
    const en = document.documentElement.lang === 'en';

    if (params.get('enviado') === '1') {
        form.hidden = true;
        sent.hidden = false;
        return;
    }

    const obra = params.get('obra');
    if (obra) {
        const mensaje = form.querySelector('[name="mensaje"]');
        const asunto = form.querySelector('[name="_subject"]');
        mensaje.value = en
            ? `Hello Andrea,\n\nI would like to acquire the artwork "${obra}".\n\n`
            : `Hola Andrea,\n\nMe gustaría adquirir la obra "${obra}".\n\n`;
        asunto.value = en ? `Purchase inquiry — ${obra}` : `Consulta de adquisición — ${obra}`;
        // el cursor empieza en el nombre, que es lo primero que falta
        form.querySelector('[name="nombre"]').focus({ preventScroll: true });
    }
})();
