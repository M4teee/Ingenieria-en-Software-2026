const toggles = document.querySelectorAll(".form-check.form-switch .form-check-input");
const scriptRepartidores = document.currentScript;
const tokenCsrf = document.querySelector('#csrf-form [name="csrfmiddlewaretoken"]')?.value;

toggles.forEach((toggle) => {
    toggle.addEventListener('change', () => cambiarEstadoRepartidor(toggle));
})

async function cambiarEstadoRepartidor(toggle) {
    toggle.disabled = true;
    const estadoSolicitado = toggle.checked;
    const fila = toggle.closest('tr');
    const spinner = document.createElement('div');
    spinner.classList.add('loader');
    toggle.parentElement.insertAdjacentElement('afterend', spinner);

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
    } catch (error) {
        toggle.checked = !estadoSolicitado;
        window.alert(error.message || 'No se pudo cambiar el estado del repartidor por un error del servidor.');
    } finally {
        spinner.remove();
        toggle.disabled = false;
    }
}
