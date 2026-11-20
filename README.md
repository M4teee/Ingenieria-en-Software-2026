<p align="center">
  <img src="docs/imagenes/banner.svg" alt="SGR, Sistema de Gestión de Repartos" width="100%">
</p>

<p align="center">
  <img alt="Python 3.14" src="https://img.shields.io/badge/Python-3.14-172033?style=flat-square">
  <img alt="Django 6.1" src="https://img.shields.io/badge/Django-6.1-172033?style=flat-square">
  <img alt="SQLite o PostgreSQL" src="https://img.shields.io/badge/DB-SQLite%20%7C%20PostgreSQL-172033?style=flat-square">
  <img alt="Sin paso de build" src="https://img.shields.io/badge/frontend-sin%20build-F2B705?style=flat-square&labelColor=172033">
</p>

SGR coordina entregas de última milla entre comercios, un equipo de operación y repartidores. El operario registra los pedidos y el sistema los asigna, el repartidor avanza cada etapa desde el teléfono con evidencia fotográfica y el cliente sigue su envío con un código, sin crear una cuenta.

<p align="center">
  <img src="docs/imagenes/escritorio/operario_inicio.png" alt="Panel de pedidos en curso" width="100%">
</p>

## Qué hace

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Operación</strong><br>
      Panel en vivo de pedidos en curso, alta con código de seguimiento, despacho automático al repartidor disponible hace más tiempo, asignación manual, cancelación, comercios, repartidores, entregas fallidas y devoluciones.
    </td>
    <td width="33%" valign="top">
      <strong>Reparto</strong><br>
      Ingreso con PIN, cinco minutos para aceptar cada asignación, una acción por etapa con foto opcional, informe de entrega fallida con motivo e historial de entregas.
    </td>
    <td width="33%" valign="top">
      <strong>Seguimiento</strong><br>
      Estado, comercio, llegada estimada mientras el pedido viaja e historial de estados. Sin datos del destinatario, del repartidor ni fotografías.
    </td>
  </tr>
</table>

## Pantallas

<table>
  <tr>
    <td width="50%"><img src="docs/imagenes/escritorio/publico_inicio.png" alt="Portada de seguimiento público"></td>
    <td width="50%"><img src="docs/imagenes/escritorio/operario_detalle_asignado.png" alt="Detalle de un pedido asignado"></td>
  </tr>
  <tr>
    <td align="center"><sub>Seguimiento público</sub></td>
    <td align="center"><sub>Detalle de un pedido con su recorrido</sub></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/imagenes/escritorio/operario_repartidores.png" alt="Gestión de repartidores"></td>
    <td width="50%"><img src="docs/imagenes/escritorio/operario_fallidas.png" alt="Entregas fallidas"></td>
  </tr>
  <tr>
    <td align="center"><sub>Repartidores con disponibilidad en vivo</sub></td>
    <td align="center"><sub>Entregas fallidas y devoluciones</sub></td>
  </tr>
</table>

<p align="center">
  <img src="docs/imagenes/movil/repartidor_asignacion_pendiente.png" alt="Asignación pendiente en el teléfono del repartidor" width="260">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/imagenes/movil/publico_seguimiento_en_viaje.png" alt="Seguimiento de un pedido en viaje desde el teléfono" width="260">
  <br>
  <sub>El repartidor y el cliente usan la aplicación desde el teléfono.</sub>
</p>

<sub>Datos ficticios basados en los <a href="demo/README.md">datos de demostración</a>.</sub>

## Cómo funciona

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Registrado
    Registrado --> Asignado: despacho
    Asignado --> Registrado: rechazo o vencimiento
    Asignado --> Retirado
    Retirado --> EnViaje
    EnViaje --> Entregado
    EnViaje --> Fallido
    Registrado --> Cancelado
    Asignado --> Cancelado
```

Monolito Django con una aplicación por rol (`operario`, `repartidor`, `clienteFinal`) y una interfaz renderizada en el servidor con [Basecoat UI](https://basecoatui.com) y un sistema de diseño propio, sin Node ni paso de build. Detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Empezar

Requisitos: Python 3.14 y Git.

```bash
git clone https://github.com/M4teee/Ingenieria-en-Software-2026.git
cd Ingenieria-en-Software-2026
python3.14 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd Backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrí `http://127.0.0.1:8000/`. Para recorrerla con datos cargados, usá los [datos de demostración](demo/README.md).

| Rol | Entrada | Acceso |
|---|---|---|
| Cliente | `/` | Sin cuenta |
| Operario | `/login/` | Usuario con `is_operario` (se habilita en Django Admin) |
| Repartidor | `/repartidor/login-pin/` | PIN de 4 dígitos, lo crea el operario |
| Administrador | `/admin/` | `createsuperuser` o usuario `is_staff` |

Variables opcionales en `.env` (ver [.env.example](.env.example)): `DJANGO_SECRET_KEY` y `DATABASE_URL` (PostgreSQL; sin ella, SQLite).

```bash
cd Backend
python manage.py test --settings=config.settings_test   # 182 pruebas, SQLite en memoria
```

## Documentación

| | |
|---|---|
| [Instalación y pruebas](docs/instalacion.md) | Windows, PostgreSQL/Neon y errores frecuentes |
| [Arquitectura](docs/arquitectura.md) | Aplicaciones, modelo de datos, flujo de un pedido e interfaz |
| [Sistema de diseño](docs/diseno.md) | Paleta, tipografía y composición por rol |
| [Estado](docs/estado.md) | Cobertura del backlog, decisiones vigentes y limitaciones |
| [Fuentes](docs/fuentes/README.md) | Entrevistas, requisitos y backlog originales |
| [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) | Pautas y reporte de vulnerabilidades |

> La configuración incluida es de **desarrollo** (`DEBUG` activo, sin HTTPS ni límite de intentos para el PIN). Antes de exponerla, seguí [SECURITY.md](SECURITY.md).

---

<sub>Trabajo práctico de Ingeniería en Software, 2026. El repositorio todavía no declara una licencia.</sub>
