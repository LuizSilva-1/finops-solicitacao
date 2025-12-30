import socket
import sys
import time


def wait_for_db(host: str, port: int, timeout: int = 60):
    for _ in range(timeout):
        try:
            with socket.create_connection((host, port), timeout=2):
                return
        except OSError:
            time.sleep(1)
    print("Database not reachable", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db("db", 5432)
