# Manual de uso

Los pasos describen las interfaces presentes en la aplicación local. Para instalar y arrancar el servidor, seguí la [guía de ejecución y pruebas](GUIA-EJECUCION-Y-PRUEBAS.md). Las pruebas manuales escriben en la base SQLite local; usá nombres y datos ficticios y conservá la base si contiene información útil.

## Preparar datos de prueba

1. Creá un administrador con `python manage.py createsuperuser` y entrá a `/admin/`.
2. En **Comercios**, creá un comercio con información ficticia y activo.
3. En **Usuarios**, creá un usuario de operario y habilitá `is_staff`.
4. Creá otro usuario para el repartidor y un perfil de repartidor asociado. Asignale un PIN local de cuatro dígitos y marcá el perfil disponible. No reutilices un PIN real.
5. Cerrá la sesión administrativa antes de probar cada rol.

El rol administrativo mantiene los datos de configuración. Para operar pedidos, usá las interfaces siguientes en vez de editar el modelo directamente desde el admin.

## Cliente final

1. Abrí `/`. También podés usar `/clienteFinal/` para la misma consulta pública.
2. Escribí el código de seguimiento que te compartió el comercio y elegí **Consultar pedido**.
3. Un código válido abre el estado y el historial persistidos. No necesitás una cuenta.
4. Desde la parte superior podés elegir el ingreso de operario o repartidor; el cliente no tiene herramientas operativas.

## Operario

1. En `/`, elegí **Iniciar sesión como operario** e ingresá con una cuenta activa `is_staff`. Al completar el acceso, se abre `/operario/`. También podés navegar directamente a esa ruta.
2. El panel lista pedidos registrados, asignados, retirados y en viaje, con estado actualizado periódicamente. Usá **Cargar pedido** o `/operario/pedidos/nuevo/`.
3. Seleccioná un comercio activo y completá dirección de destino, especificaciones de traslado y fecha/hora estimadas. Los campos requeridos se validan en el servidor.
4. Presioná **Registrar Pedido**. La pantalla de confirmación presenta el mensaje de éxito y el código de seguimiento, que se puede copiar. El pedido nace como `Registrado`, sin repartidor, y su historial recibe el evento inicial.
5. En el detalle del pedido, elegí un repartidor activo y disponible y presioná **Asignar pedido**. El sistema comprueba nuevamente la disponibilidad y registra el evento de asignación. El pedido queda `Asignado` y el repartidor tiene cinco minutos para aceptar o rechazarlo desde su panel.
6. Si el comercio se inactiva antes de enviar el formulario, el servidor rechaza el alta con el mensaje exigido por HU 12. Si un repartidor ya no está disponible, no se realiza la asignación.
7. Abrí **Repartidores** o `/operario/repartidores/` para consultar usuario, vehículo y disponibilidad. En **Nuevo repartidor** o `/operario/repartidores/nuevo/`, ingresá un usuario y un PIN numérico de cuatro dígitos; nombre, apellido y e-mail son opcionales. El perfil comienza no disponible y su vehículo inicial es moto.

La asignación manual es un puente provisional elegido por el equipo. Las HU 22 y 30 siguen sin implementar y no se consideran completas: no hay cálculo automático ni de cercanía. Tampoco se envía aviso externo; el repartidor ve la solicitud al abrir o actualizar `/repartidor/`.

## Repartidor

1. Abrí `/repartidor/login-pin/` y usá el PIN de prueba vinculado a un perfil activo. La sesión identifica al usuario asociado a ese perfil.
2. En `/repartidor/`, la solicitud asignada muestra el comercio, destino y el tiempo para responder. Aceptala para habilitar el trabajo o rechazala para liberar el pedido.
3. Después de aceptar, avanzá por las acciones disponibles: `Asignado → Retirado → En viaje`. En Retirado, En viaje y Fallido se admite una fotografía opcional.
4. Para cerrar el recorrido, marcá `Entregado` o `Fallido`. La evidencia se guarda con su evento de historial. Los archivos admitidos son JPEG, PNG o WebP, de hasta 10 MB y una imagen por transición.
5. Abrí **Ver detalle e historial** para consultar los eventos y las fotografías del pedido asignado a tu cuenta. Un repartidor no puede abrir los pedidos ni las evidencias de otro.

Las transiciones no permitidas se rechazan. El pedido finalizado aparece en la lista de pedidos cerrados y deja de ser una entrega activa.

## Administrador

Django Admin está en `/admin/` y sirve para mantener usuarios, comercios y perfiles de repartidor. El enlace se muestra en la navegación del operario. El backend conserva los controles de Django: se requiere una cuenta activa con `is_staff` y permisos para las operaciones sobre cada modelo. No se otorgan permisos al iniciar sesión.

Al cerrar sesión, Django vuelve a `/`. Una persona operaria o repartidora con sesión activa que abre `/` es dirigida a su panel; una sesión inválida no recibe acceso a rutas protegidas.

## Pruebas negativas y permisos

- Un usuario anónimo que abre la carga es enviado al inicio de sesión; un usuario autenticado sin `is_staff` recibe 403.
- La lista de comercios excluye los inactivos y el servidor también los rechaza si fueron desactivados antes del envío.
- Intentá un código inexistente en la consulta pública: se presenta un error y no se revela información de otros pedidos.
- Un usuario que no es repartidor recibe acceso denegado al módulo; un repartidor distinto no puede consultar el detalle ni la fotografía de otro.
- Al probar archivos, usá una imagen ficticia de tipo admitido; un formato inválido, varios archivos o un archivo mayor de 10 MB se rechazan.

Las pruebas automatizadas cubren además duplicación por reenvío, colisiones de código, rollback del historial/foto, temporizador de respuesta y transiciones inválidas. Ejecutá `python manage.py test` desde `Backend/`.
