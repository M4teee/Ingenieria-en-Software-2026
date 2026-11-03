const toggles = document.querySelectorAll(".form-check.form-switch .form-check-input");
const scriptComercios = document.currentScript;
const tokenCsrf = document.querySelector('#csrf-form [name="csrfmiddlewaretoken"]')?.value;

toggles.forEach((toggle) => {
    toggle.addEventListener('change', () => cambiarEstadoComercio(toggle));
})

const campoBusqueda = document.getElementById("buscar-comercio");
const filasComercios = document.querySelectorAll(".app-table tbody tr");
const mensajeSinResultados = document.getElementById("sin-resultados-comercios");

campoBusqueda.addEventListener("input", () => {
    const busqueda = campoBusqueda.value
        .trim()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLocaleLowerCase();
    let cantidadVisibles = 0;

    filasComercios.forEach((fila) => {
        const nombre = fila.cells[0].textContent
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLocaleLowerCase();
        const coincide = nombre.includes(busqueda);

        fila.hidden = !coincide;
        if (coincide) cantidadVisibles += 1;
    });

    mensajeSinResultados.hidden = cantidadVisibles > 0;
});
            

async function cambiarEstadoComercio(toggle) {
    toggle.disabled = true;
    const estadoSolicitado = toggle.checked;
    const fila = toggle.closest('tr');
    const spinner = document.createElement('div');
    spinner.classList.add('loader');
    toggle.parentElement.insertAdjacentElement('afterend', spinner);

    try {
        const respuesta = await fetch(scriptComercios.dataset.endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: new URLSearchParams({
                nombre: toggle.dataset.nombre,
                activo: String(estadoSolicitado),
                csrfmiddlewaretoken: tokenCsrf,
            }),
        });
        const resultado = await respuesta.json();
        if (!respuesta.ok) {
            throw new Error(resultado.error || 'No se pudo cambiar el estado del comercio.');
        }

        fila.classList.toggle('activo', resultado.activo);
    } catch (error) {
        toggle.checked = !estadoSolicitado;
        window.alert(error.message || 'No se pudo cambiar el estado del comercio por un error del servidor.');
    } finally {
        spinner.remove();
        toggle.disabled = false;
    }
}
