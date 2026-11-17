import queue
import sys
import types
import psycopg


class SimpleConnectionPool:
    """
    Pool de conexiones liviano y seguro para hilos para desarrollo con runserver
    y bases remotas (Neon). Reutiliza conexiones TCP/SSL abiertas entre hilos
    en lugar de abrir una conexión nueva en cada petición de un worker.
    """
    def __init__(self, conninfo='', *, kwargs=None, min_size=1, max_size=5, timeout=30.0, open=True, configure=None, check=None, **other):
        self.conninfo = conninfo
        self.kwargs = kwargs or {}
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self.configure = configure
        self.check = check
        self._pool = queue.Queue(maxsize=max_size)
        self._open = False
        if open:
            self.open()

    @staticmethod
    def check_connection(conn):
        try:
            return not conn.closed
        except Exception:
            return False

    def open(self, wait=False, timeout=None):
        self._open = True

    def close(self, timeout=None):
        self._open = False
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Exception:
                pass

    def getconn(self, timeout=None):
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if not conn.closed:
                    if self.check and not self.check(conn):
                        try:
                            conn.close()
                        except Exception:
                            pass
                        continue
                    conn._pool = self
                    return conn
            except queue.Empty:
                break
        if self.conninfo:
            conn = psycopg.connect(self.conninfo, **self.kwargs)
        else:
            conn = psycopg.connect(**self.kwargs)
        if self.configure:
            self.configure(conn)
        conn._pool = self
        return conn

    def putconn(self, conn):
        if not self._open or conn.closed:
            try:
                conn.close()
            except Exception:
                pass
            return
        try:
            self._pool.put_nowait(conn)
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
