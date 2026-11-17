import queue
import select
import sys
import time
import types
import psycopg
from psycopg.pq import ConnStatus, TransactionStatus


class SimpleConnectionPool:
    """
    Pool de conexiones liviano y seguro para hilos para desarrollo con runserver
    y bases remotas (Neon). Reutiliza conexiones TCP/SSL abiertas entre hilos
    en lugar de abrir una conexión nueva en cada petición de un worker.
    Descarta conexiones con inactividad superior a max_idle_seconds (20s) y
    verifica la salud del socket SSL antes de entregarlas para evitar errores
    por cierre de socket remoto en PgBouncer/Neon.
    """
    def __init__(
        self,
        conninfo='',
        *,
        kwargs=None,
        min_size=1,
        max_size=5,
        timeout=30.0,
        max_idle=20.0,
        max_idle_seconds=None,
        open=True,
        configure=None,
        check=None,
        **other,
    ):
        self.conninfo = conninfo
        self.kwargs = kwargs or {}
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        if max_idle_seconds is not None:
            self.max_idle_seconds = float(max_idle_seconds)
        elif max_idle is not None:
            self.max_idle_seconds = float(max_idle)
        else:
            self.max_idle_seconds = 20.0
        self.configure = configure
        self.check = check or self.check_connection
        self._pool = queue.Queue(maxsize=max_size)
        self._open = False
        if open:
            self.open()

    @staticmethod
    def check_connection(conn):
        """
        Verifica si la conexión está abierta y sana:
        1. Comprueba flags de cierre/rotura locales.
        2. Comprueba status libpq (ConnStatus.OK) y estado de transacción (TransactionStatus.IDLE).
        3. Realiza un sondeo no bloqueante sobre el socket con select() para detectar si el
           servidor remoto (Neon/PgBouncer) cerró la conexión por inactividad (TCP FIN/RST).
        """
        try:
            if conn is None or getattr(conn, 'closed', True) or getattr(conn, 'broken', False):
                return False
            if hasattr(conn, 'info'):
                if conn.info.status != ConnStatus.OK:
                    return False
                if conn.info.transaction_status != TransactionStatus.IDLE:
                    try:
                        conn.rollback()
                    except Exception:
                        return False
            # Detección inmediata de cierre remoto sin incurrir en latencia de red adicional
            if hasattr(conn, 'fileno'):
                fileno = conn.fileno()
                if fileno is not None and fileno >= 0:
                    r, _, _ = select.select([fileno], [], [], 0)
                    if r:
                        # Hay notificación de lectura pendiente en el socket IDLE (típicamente EOF/cierre SSL)
                        if hasattr(conn, 'pgconn') and hasattr(conn.pgconn, 'consume_input'):
                            conn.pgconn.consume_input()
                        if conn.info.status != ConnStatus.OK or getattr(conn, 'broken', False):
                            return False
            return True
        except Exception:
            return False

    def is_connection_healthy(self, conn):
        if not self.check_connection(conn):
            return False
        if self.check and self.check != self.check_connection:
            try:
                return bool(self.check(conn))
            except Exception:
                return False
        return True

    def open(self, wait=False, timeout=None):
        self._open = True

    def close(self, timeout=None):
        self._open = False
        while not self._pool.empty():
            try:
                item = self._pool.get_nowait()
                conn = item[0] if isinstance(item, tuple) else item
                conn.close()
            except Exception:
                pass

    def getconn(self, timeout=None):
        now = time.monotonic()
        while not self._pool.empty():
            try:
                item = self._pool.get_nowait()
                if isinstance(item, tuple):
                    conn, last_used = item
                else:
                    conn, last_used = item, now

                # 1. Descartar conexiones con inactividad prolongada (recicladas por PgBouncer)
                idle_seconds = now - last_used
                if self.max_idle_seconds is not None and idle_seconds > self.max_idle_seconds:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    continue

                # 2. Verificar que la conexión tomada siga viva y sana
                if not self.is_connection_healthy(conn):
                    try:
                        conn.close()
                    except Exception:
                        pass
                    continue

                conn._pool = self
                return conn
            except queue.Empty:
                break

        # Crear una nueva conexión si ninguna en el pool está disponible o sana
        if self.conninfo:
            conn = psycopg.connect(self.conninfo, **self.kwargs)
        else:
            conn = psycopg.connect(**self.kwargs)
        if self.configure:
            self.configure(conn)
        conn._pool = self
        return conn

    def putconn(self, conn):
        if not self._open or getattr(conn, 'closed', True) or getattr(conn, 'broken', False):
            try:
                conn.close()
            except Exception:
                pass
            return
        if not self.check_connection(conn):
            try:
                conn.close()
            except Exception:
                pass
            return
        now = time.monotonic()
        try:
            self._pool.put_nowait((conn, now))
        except queue.Full:
            try:
                conn.close()
            except Exception:
                pass


def enable_connection_pooling():
    if 'psycopg_pool' not in sys.modules:
        try:
            import psycopg_pool
        except ImportError:
            mod = types.ModuleType('psycopg_pool')
            mod.ConnectionPool = SimpleConnectionPool
            sys.modules['psycopg_pool'] = mod
