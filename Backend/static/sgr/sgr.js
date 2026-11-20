/* SGR — interacciones compartidas (vanilla, sin dependencias). */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* Diálogos: <dialog class="dialog">. Se conservan los atributos
     data-bs-toggle/data-bs-target/data-bs-dismiss del marcado original. */
  const abrir = (dialogo, disparador) => {
    if (!dialogo || dialogo.open) return;
    dialogo._disparador = disparador || document.activeElement;
    dialogo.showModal();
    const foco = dialogo.querySelector('[autofocus], input:not([type=hidden]), button.btn[data-variant]');
    if (foco) foco.focus();
  };
  const cerrar = (dialogo) => {
    if (dialogo && dialogo.open) dialogo.close();
  };

  document.addEventListener('click', (evento) => {
    const disparador = evento.target.closest('[data-bs-toggle="modal"], [data-abrir]');
    if (disparador) {
      const destino = disparador.dataset.bsTarget || disparador.dataset.abrir;
      const dialogo = destino && document.querySelector(destino);
      if (dialogo && dialogo.tagName === 'DIALOG') {
        evento.preventDefault();
        if (disparador.dataset.imgUrl) {
          const img = $('img[data-evidencia]', dialogo);
          const enlace = $('a[data-evidencia]', dialogo);
          if (img) img.src = disparador.dataset.imgUrl;
          if (enlace) enlace.href = disparador.dataset.imgUrl;
        }
        abrir(dialogo, disparador);
        return;
      }
    }
    const descartar = evento.target.closest('[data-bs-dismiss="modal"], [data-cerrar]');
    if (descartar) {
      cerrar(descartar.closest('dialog'));
      return;
    }
    // Clic en el fondo (fuera del contenido) cierra el diálogo.
    if (evento.target.tagName === 'DIALOG' && evento.target.classList.contains('dialog')) {
      cerrar(evento.target);
    }
  });

  document.addEventListener('close', (evento) => {
    const dialogo = evento.target;
    if (dialogo.tagName === 'DIALOG' && dialogo._disparador && document.contains(dialogo._disparador)) {
      dialogo._disparador.focus();
    }
  }, true);

  // Diálogos que deben abrirse al cargar (por ejemplo, error al regenerar PIN).
  $$('dialog[data-abrir-al-cargar]').forEach((d) => abrir(d));

  /* Mensajes de django.contrib.messages */
  const descartarMensaje = (mensaje) => {
    mensaje.classList.add('saliendo');
    window.setTimeout(() => mensaje.remove(), 220);
  };
  $$('.mensaje').forEach((mensaje) => {
    const boton = $('button', mensaje);
    if (boton) boton.addEventListener('click', () => descartarMensaje(mensaje));
    if (mensaje.dataset.tono !== 'error') {
      let restante = 7000;
      let inicio = Date.now();
      let temporizador = window.setTimeout(() => descartarMensaje(mensaje), restante);
      const pausar = () => { window.clearTimeout(temporizador); restante -= Date.now() - inicio; };
      const seguir = () => { inicio = Date.now(); temporizador = window.setTimeout(() => descartarMensaje(mensaje), Math.max(restante, 1500)); };
      mensaje.addEventListener('mouseenter', pausar);
      mensaje.addEventListener('mouseleave', seguir);
      mensaje.addEventListener('focusin', pausar);
      mensaje.addEventListener('focusout', seguir);
    }
  });

  /* Envíos: estado ocupado y prevención de doble envío */
  document.addEventListener('submit', (evento) => {
    if (evento.defaultPrevented) return;
    const formulario = evento.target;
    if (formulario.method.toLowerCase() !== 'post') return;
    const boton = evento.submitter || $('[type=submit]', formulario);
    if (formulario.dataset.enviando) { evento.preventDefault(); return; }
    formulario.dataset.enviando = 'true';
    if (boton) {
      boton.setAttribute('aria-busy', 'true');
      // Se deshabilita después del envío para que el valor del botón viaje.
      window.setTimeout(() => { boton.disabled = true; }, 0);
    }
  });
  // Al volver con el botón "atrás" el formulario debe quedar usable.
  window.addEventListener('pageshow', () => {
    $$('form[data-enviando]').forEach((f) => {
      delete f.dataset.enviando;
      $$('[aria-busy="true"]', f).forEach((b) => { b.removeAttribute('aria-busy'); b.disabled = false; });
    });
  });

  /* Selector de archivo con vista previa */
  $$('.archivo input[type=file]').forEach((input) => {
    const contenedor = input.closest('.archivo');
    const texto = $('[data-archivo-nombre]', contenedor);
    const original = texto ? texto.textContent : '';
    input.addEventListener('change', () => {
      const archivo = input.files && input.files[0];
      const previa = $('img', contenedor);
      if (previa) previa.remove();
      if (!archivo) {
        delete contenedor.dataset.lleno;
        if (texto) texto.textContent = original;
        return;
      }
      contenedor.dataset.lleno = 'true';
      if (texto) texto.textContent = archivo.name;
      if (archivo.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.alt = '';
        img.src = URL.createObjectURL(archivo);
        contenedor.insertBefore(img, contenedor.firstChild);
      }
    });
  });

  /* Copiar al portapapeles */
  $$('[data-copiar]').forEach((boton) => {
    boton.addEventListener('click', async () => {
      const origen = document.querySelector(boton.dataset.copiar);
      const salida = document.querySelector(boton.dataset.resultado || '');
      if (!origen) return;
      try {
        await navigator.clipboard.writeText(origen.value || origen.textContent);
        if (salida) salida.textContent = 'Código copiado.';
        boton.dataset.copiado = 'true';
      } catch (_) {
        if (origen.select) origen.select();
        if (salida) salida.textContent = 'No se pudo copiar automáticamente. Seleccioná y copiá el código.';
      }
    });
  });

  /* Búsqueda en la barra (pantallas angostas) */
  const botonBuscar = $('[data-mostrar-busqueda]');
  if (botonBuscar) {
    botonBuscar.addEventListener('click', () => {
      const buscar = $('.barra .buscar');
      buscar.classList.add('abierta');
      $('input', buscar).focus();
    });
    const campo = $('.barra .buscar input');
    if (campo) campo.addEventListener('blur', () => { if (!campo.value) campo.closest('.buscar').classList.remove('abierta'); });
  }

  /* Aviso flotante: se puede cerrar hasta que cambie la lista */
  const alerta = $('#alerta-sin-repartidor');
  if (alerta) {
    const boton = $('.cerrar', alerta);
    if (boton) boton.addEventListener('click', () => {
      alerta.dataset.descartado = $('#alerta-sin-repartidor-lista').textContent.trim();
      alerta.hidden = true;
    });
  }

  /* Resumen de errores: llevar el foco al resumen tras un envío inválido */
  const resumen = $('.resumen-errores');
  if (resumen) { resumen.setAttribute('tabindex', '-1'); resumen.focus({ preventScroll: false }); }

  /* Ayudas de campo: se suman a aria-describedby del control */
  $$('.field .ayuda[id]').forEach((ayuda) => {
    const control = $('input, select, textarea', ayuda.closest('.field'));
    if (!control) return;
    const actuales = (control.getAttribute('aria-describedby') || '').split(' ').filter(Boolean);
    if (!actuales.includes(ayuda.id)) control.setAttribute('aria-describedby', [...actuales, ayuda.id].join(' '));
  });

  /* Teclado y visor de PIN */
  const pin = $('#pin');
  const visor = $('.pin-visor');
  if (pin && visor) {
    // En pantallas táctiles se usa el teclado propio; el del sistema lo taparía.
    if (window.matchMedia('(pointer: coarse)').matches) pin.setAttribute('inputmode', 'none');
    const casillas = $$('span', visor);
    const pintar = () => {
      const largo = pin.value.length;
      casillas.forEach((c, i) => {
        c.toggleAttribute('data-lleno', i < largo);
        c.toggleAttribute('data-actual', document.activeElement === pin && i === Math.min(largo, 3));
      });
    };
    pin.addEventListener('input', () => { pin.value = pin.value.replace(/\D/g, '').slice(0, 4); pintar(); });
    pin.addEventListener('focus', pintar);
    pin.addEventListener('blur', pintar);
    $$('.teclado button').forEach((tecla) => {
      tecla.addEventListener('click', () => {
        if (tecla.dataset.accion === 'borrar') pin.value = pin.value.slice(0, -1);
        else if (tecla.dataset.accion === 'limpiar') pin.value = '';
        else if (pin.value.length < 4) pin.value += tecla.textContent.trim();
        pintar();
        if (pin.value.length === 4) {
          const formulario = pin.form;
          if (formulario.requestSubmit) formulario.requestSubmit(); else formulario.submit();
        }
      });
    });
    pintar();
  }

  /* Precarga al pasar el cursor y barra de progreso al navegar
     (comportamiento heredado de la versión anterior de base.html). */
  const precargados = new Set();
  const precargar = (url) => {
    if (!url || precargados.has(url)) return;
    try {
      const u = new URL(url, window.location.href);
      if (u.origin !== window.location.origin || u.pathname === window.location.pathname) return;
      if (u.pathname.includes('logout') || u.pathname.includes('estado')) return;
      precargados.add(url);
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = url;
      link.as = 'document';
      document.head.appendChild(link);
    } catch (_) { /* URL inválida: se ignora */ }
  };
  let esperaPrecarga = null;
  document.addEventListener('mouseover', (e) => {
    const a = e.target.closest('a');
    if (!a || !a.href) return;
    esperaPrecarga = window.setTimeout(() => precargar(a.href), 65);
  }, { passive: true });
  document.addEventListener('mouseout', () => { if (esperaPrecarga) window.clearTimeout(esperaPrecarga); }, { passive: true });
  document.addEventListener('touchstart', (e) => {
    const a = e.target.closest('a');
    if (a && a.href) precargar(a.href);
  }, { passive: true });
  const barra = document.createElement('div');
  barra.id = 'page-progress-bar';
  barra.setAttribute('aria-hidden', 'true');
  document.body.appendChild(barra);
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a || !a.href || a.target === '_blank' || a.hasAttribute('download') || e.defaultPrevented) return;
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    try {
      const u = new URL(a.href, window.location.href);
      if (u.origin === window.location.origin && u.pathname !== window.location.pathname) barra.classList.add('loading');
    } catch (_) { /* URL inválida: se ignora */ }
  });
  window.addEventListener('pageshow', () => barra.classList.remove('loading'));

  window.SGR = { abrir, cerrar };
})();
