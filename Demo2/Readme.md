# Datos de ejemplo para la Demo 2

## Operario

- Usuario: `admin`
- Contraseña: `operario`

## Repartidores

| Usuario | Nombre | Vehículo | PIN | Disponibilidad |
|---|---|---|---|---|
| `bicicleta1` | Bicicleta Uno | bicicleta | `1111` | Disponible |
| `bicicleta2` | Bicicleta Dos | bicicleta | `1222` | Disponible |
| `bicicleta3` | Bicicleta Tres | bicicleta | `1333` | No disponible |
| `moto1` | Moto Uno | moto | `2111` | No disponible |
| `moto2` | Moto Dos | moto | `2222` | Disponible |
| `moto3` | Moto Tres | moto | `2333` | No disponible |
| `auto1` | Auto Uno | auto | `3111` | Disponible |
| `auto2` | Auto Dos | auto | `3222` | Disponible |
| `auto3` | Auto Tres | auto | `3333` | No disponible |
| `camion1` | Camion Uno | camion | `4111` | No disponible |
| `camion2` | Camion Dos | camion | `4222` | No disponible |
| `camion3` | Camion Tres | camion | `4333` | No disponible |

## Comercios

| Nombre | Dirección | Contacto | Estado |
|---|---|---|---|
| Comercio 1 | Avenida 1 nro. 1111 | 221 111-1111 | Activo |
| Comercio 2 | Avenida 2 nro. 2222 | 221 222-2222 | Activo |
| Comercio 3 | Avenida 3 nro. 3333 | 221 333-3333 | Activo |
| Comercio 4 | Avenida 4 nro. 4444 | 221 444-4444 | Activo |
| Comercio 5 | Avenida 5 nro. 5555 | 221 555-5555 | Activo |
| Comercio 6 | Avenida 6 nro. 6666 | 221 666-6666 | Activo |
| Comercio 7 | Avenida 7 nro. 7777 | 221 777-7777 | Activo |
| Comercio 8 | Avenida 8 nro. 8888 | 221 888-8888 | Activo |
| Comercio 9 | Avenida 9 nro. 9999 | 221 999-9999 | Activo |

## Pedidos

| Código | Estado | Comercio | Vehículo requerido | Repartidor |
|---|---|---|---|---|
| `DEMO20001` | entregado | Comercio 1 | bicicleta | bicicleta1 |
| `DEMO20002` | entregado | Comercio 2 | bicicleta | bicicleta2 |
| `DEMO20003` | entregado | Comercio 3 | bicicleta | bicicleta3 |
| `DEMO20004` | entregado | Comercio 4 | moto | moto1 |
| `DEMO20005` | entregado | Comercio 5 | moto | moto2 |
| `DEMO20006` | entregado | Comercio 6 | moto | moto3 |
| `DEMO20007` | entregado | Comercio 7 | auto | auto1 |
| `DEMO20008` | entregado | Comercio 8 | auto | auto2 |
| `DEMO20009` | entregado | Comercio 9 | auto | auto3 |
| `DEMO20010` | entregado | Comercio 1 | camion | camion1 |
| `DEMO20011` | entregado | Comercio 2 | camion | camion2 |
| `DEMO20012` | fallido | Comercio 3 | camion | camion3 |
| `DEMO20013` | en_viaje | Comercio 4 | moto | moto1 |
