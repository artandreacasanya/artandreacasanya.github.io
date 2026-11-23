const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxX7nNcnJSmsKWZxwU_d49HDtLEJr7m6zwDeiaUCbB9_ihjPMW0fWjf3eTNqPOcsdCIZQ/exec";

document.addEventListener("DOMContentLoaded", function() {
    const likeButtons = document.querySelectorAll('.btn-like');

    likeButtons.forEach(button => {
        const workId = button.getAttribute('data-work-id');
        const heartImg = button.querySelector('.heart-img');

        if (localStorage.getItem('liked_' + workId) === 'true') {
            button.classList.add('liked');
            heartImg.src = heartImg.getAttribute('data-filled');
        }
    });
});

function enviarLike(workId, action) {
    fetch(SCRIPT_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ id: workId, action: action })
    }).catch(error => {
        console.error('Error al registrar el like:', error);
    });
}

function toggleLike(button) {
    const workId = button.getAttribute('data-work-id');
    const heartImg = button.querySelector('.heart-img');

    if (button.classList.contains('liked')) {
        button.classList.remove('liked');
        heartImg.src = heartImg.getAttribute('data-empty');
        localStorage.setItem('liked_' + workId, 'false');
        enviarLike(workId, 'unlike');
    } else {
        button.classList.add('liked');
        heartImg.src = heartImg.getAttribute('data-filled');
        localStorage.setItem('liked_' + workId, 'true');
        enviarLike(workId, 'like');
    }
}
