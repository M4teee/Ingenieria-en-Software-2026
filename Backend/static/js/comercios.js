const toggles = document.querySelectorAll(".form-check.form-switch .form-check-input");
const scriptComercios = document.currentScript;
const tokenCsrf = document.querySelector('#csrf-form [name="csrfmiddlewaretoken"]')?.value;
const campoBusqueda = document.getElementById("buscar-comercio");
const filasComercios = document.querySelectorAll(".app-table tbody tr");
const mensajeSinResultados = document.getElementById("sin-resultados-comercios");
const contenedorMensaje = document.getElementById("mensaje-estado-comercio");
const botonesFiltro = document.querySelectorAll("[data-filtro-estado]");

let filtroEstadoActual = "todos";

function mostrarMensajeEstado(mensaje) {
    if (!contenedorMensaje) return;
    contenedorMensaje.textContent = mensaje;
    contenedorMensaje.classList.remove("d-none");
    contenedorMensaje.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function aplicarFiltros() {
    const busqueda = (campoBusqueda?.value || "")
        .trim()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLocaleLowerCase();
    let cantidadVisibles = 0;

    filasComercios.forEach((fila) => {
        const nombre = (fila.cells[0]?.textContent || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLocaleLowerCase();
        const coincideNombre = nombre.includes(busqueda);
        const esActivo = fila.classList.contains("activo");

        let coincideEstado = true;
        if (filtroEstadoActual === "activos") {
            coincideEstado = esActivo;
        } else if (filtroEstadoActual === "inactivos") {
            coincideEstado = !esActivo;
        }

        const visible = coincideNombre && coincideEstado;
        fila.hidden = !visible;
        if (visible) cantidadVisibles += 1;
    });

    if (mensajeSinResultados) {
        mensajeSinResultados.hidden = cantidadVisibles > 0;
    }
}

if (campoBusqueda) {
    campoBusqueda.addEventListener("input", aplicarFiltros);
}

botonesFiltro.forEach((btn) => {
    btn.addEventListener("click", () => {
        botonesFiltro.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        filtroEstadoActual = btn.dataset.filtroEstado;
        aplicarFiltros();
    });
});

toggles.forEach((toggle) => {
    toggle.addEventListener('change', () => cambiarEstadoComercio(toggle));
});

async function cambiarEstadoComercio(toggle) {
    const estadoSolicitado = toggle.checked;
    const accion = estadoSolicitado ? "reactivar" : "deshabilitar";
    const confirmacion = window.confirm(`¿Estás seguro de que deseas ${accion} el comercio "${toggle.dataset.nombre}"?`);
    if (!confirmacion) {
        toggle.checked = !estadoSolicitado;
        return;
    }

    toggle.disabled = true;
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
        aplicarFiltros();

        const mensaje = resultado.mensaje || (resultado.activo ? 'Comercio reactivado exitosamente' : 'Comercio deshabilitado exitosamente');
        mostrarMensajeEstado(mensaje);
    } catch (error) {
        toggle.checked = !estadoSolicitado;
        window.alert(error.message || 'No se pudo cambiar el estado del comercio por un error del servidor.');
    } finally {
        spinner.remove();
        toggle.disabled = false;
    }
}
