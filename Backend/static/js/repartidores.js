(() => {
    const scriptRepartidores = document.currentScript;
    const toggles = document.querySelectorAll('input[role="switch"][data-username]');
    const tokenCsrf = document.querySelector('#csrf-form [name="csrfmiddlewaretoken"]')?.value;
    const avisoError = document.getElementById('error-estado-repartidor');

    toggles.forEach((toggle) => {
        toggle.addEventListener('change', () => cambiarEstadoRepartidor(toggle));
    });

    async function cambiarEstadoRepartidor(toggle) {
        const estadoSolicitado = toggle.checked;
        if (!estadoSolicitado && !window.confirm(`¿Querés desactivar la cuenta de "${toggle.dataset.username}"? No va a poder ingresar con su PIN.`)) {
            toggle.checked = true;
            return;
        }
        toggle.disabled = true;
        const fila = toggle.closest('tr');
        const texto = toggle.parentElement.querySelector('.interruptor-texto');
        const spinner = document.createElement('span');
        spinner.className = 'loader';
        spinner.setAttribute('aria-hidden', 'true');
        toggle.insertAdjacentElement('afterend', spinner);
        if (avisoError) avisoError.hidden = true;

        try {
            const respuesta = await fetch(scriptRepartidores.dataset.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new URLSearchParams({
                    username: toggle.dataset.username,
                    activo: String(estadoSolicitado),
                    csrfmiddlewaretoken: tokenCsrf,
                }),
            });
            const resultado = await respuesta.json();
            if (!respuesta.ok) {
                throw new Error(resultado.error || 'No se pudo cambiar el estado del repartidor.');
            }

            fila.classList.toggle('activo', resultado.activo);
            fila.querySelector('.persona')?.setAttribute('data-activo', String(resultado.activo));
            if (texto) texto.textContent = resultado.activo ? 'Activo' : 'Inactivo';
        } catch (error) {
            toggle.checked = !estadoSolicitado;
            const mensaje = `${toggle.dataset.username}: ${error.message || 'No se pudo cambiar el estado del repartidor por un error del servidor.'}`;
            if (avisoError) {
                avisoError.textContent = mensaje;
                avisoError.hidden = false;
            } else {
                window.alert(mensaje);
            }
        } finally {
            spinner.remove();
            toggle.disabled = false;
            toggle.focus();
        }
    }
})();
