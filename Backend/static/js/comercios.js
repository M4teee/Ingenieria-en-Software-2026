(() => {
    const scriptComercios = document.currentScript;
    const toggles = document.querySelectorAll('input[role="switch"][data-nombre]');
    const tokenCsrf = document.querySelector('#csrf-form [name="csrfmiddlewaretoken"]')?.value;
    const campoBusqueda = document.getElementById('buscar-comercio');
    const filasComercios = document.querySelectorAll('[data-fila-comercio]');
    const mensajeSinResultados = document.getElementById('sin-resultados-comercios');
    const contenedorMensaje = document.getElementById('mensaje-estado-comercio');
    const conteo = document.getElementById('conteo-comercios');
    const botonesFiltro = document.querySelectorAll('[data-filtro-estado]');

    let filtroEstadoActual = 'todos';

    const normalizar = (texto) => (texto || '')
        .trim()
        .normalize('NFD')
        .replace(/[̀-ͯ]/g, '')
        .toLocaleLowerCase();

    function mostrarMensajeEstado(mensaje, tono = 'exito') {
        if (!contenedorMensaje) return;
        contenedorMensaje.querySelector('[data-texto]').textContent = mensaje;
        contenedorMensaje.dataset.tono = tono;
        contenedorMensaje.setAttribute('role', tono === 'error' ? 'alert' : 'status');
        contenedorMensaje.hidden = false;
    }

    function aplicarFiltros() {
        const busqueda = normalizar(campoBusqueda?.value);
        let cantidadVisibles = 0;

        filasComercios.forEach((fila) => {
            const nombre = normalizar(fila.querySelector('.comercio-nombre')?.textContent);
            const esActivo = fila.classList.contains('activo');
            let coincideEstado = true;
            if (filtroEstadoActual === 'activos') coincideEstado = esActivo;
            else if (filtroEstadoActual === 'inactivos') coincideEstado = !esActivo;

            const visible = nombre.includes(busqueda) && coincideEstado;
            fila.hidden = !visible;
            if (visible) cantidadVisibles += 1;
        });

        if (mensajeSinResultados) mensajeSinResultados.hidden = cantidadVisibles > 0;
        if (conteo) {
            const total = filasComercios.length;
            conteo.textContent = cantidadVisibles === total
                ? `${total} ${total === 1 ? 'comercio' : 'comercios'}`
                : `${cantidadVisibles} de ${total} comercios`;
        }
    }

    campoBusqueda?.addEventListener('input', aplicarFiltros);

    botonesFiltro.forEach((btn) => {
        btn.addEventListener('click', () => {
            botonesFiltro.forEach((b) => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            filtroEstadoActual = btn.dataset.filtroEstado;
            aplicarFiltros();
        });
    });

    toggles.forEach((toggle) => {
        toggle.addEventListener('change', () => cambiarEstadoComercio(toggle));
    });

    async function cambiarEstadoComercio(toggle) {
        const estadoSolicitado = toggle.checked;
        const accion = estadoSolicitado ? 'reactivar' : 'deshabilitar';
        const confirmacion = window.confirm(`¿Querés ${accion} el comercio "${toggle.dataset.nombre}"?`);
        if (!confirmacion) {
            toggle.checked = !estadoSolicitado;
            return;
        }

        toggle.disabled = true;
        const fila = toggle.closest('tr');
        const texto = toggle.parentElement.querySelector('.interruptor-texto');
        const spinner = document.createElement('span');
        spinner.className = 'loader';
        spinner.setAttribute('aria-hidden', 'true');
        toggle.insertAdjacentElement('afterend', spinner);

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
            fila.querySelector('.persona')?.setAttribute('data-activo', String(resultado.activo));
            if (texto) texto.textContent = resultado.activo ? 'Activo' : 'Inactivo';
            aplicarFiltros();
            mostrarMensajeEstado(resultado.mensaje || (resultado.activo
                ? 'Comercio reactivado exitosamente'
                : 'Comercio deshabilitado exitosamente'));
        } catch (error) {
            toggle.checked = !estadoSolicitado;
            mostrarMensajeEstado(error.message || 'No se pudo cambiar el estado del comercio por un error del servidor.', 'error');
        } finally {
            spinner.remove();
            toggle.disabled = false;
            toggle.focus();
        }
    }
})();
