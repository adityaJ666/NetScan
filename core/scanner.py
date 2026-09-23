import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class PortScanner:

    def __init__(
        self,
        target,
        start_port=1,
        end_port=1024,
        timeout=0.2,
        max_workers=100
    ):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.max_workers = max_workers

    def scan_port(self, ip_address, port):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(self.timeout)

        try:
            connection = sock.connect_ex(
                (ip_address, port)
            )

            if connection == 0:

                try:
                    service = socket.getservbyport(
                        port,
                        "tcp"
                    )
                except OSError:
                    service = "unknown"

                return {
                    "port": port,
                    "state": "Open",
                    "service": service
                }

        except (socket.timeout, OSError):
            pass

        finally:
            sock.close()

        return None

    def scan(self):

        start_time = time.time()

        # Resolve hostname/IP
        ip_address = socket.gethostbyname(
            self.target
        )

        results = []

        ports = range(
            self.start_port,
            self.end_port + 1
        )

        # Scan multiple ports concurrently
        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:

            futures = {
                executor.submit(
                    self.scan_port,
                    ip_address,
                    port
                ): port
                for port in ports
            }

            for future in as_completed(futures):

                result = future.result()

                if result is not None:
                    results.append(result)

        # Keep results ordered by port number
        results.sort(
            key=lambda item: item["port"]
        )

        end_time = time.time()

        scan_duration = round(
            end_time - start_time,
            2
        )

        total_ports = (
            self.end_port -
            self.start_port +
            1
        )

        open_ports = len(results)

        return {
            "target": self.target,
            "ip": ip_address,
            "start_port": self.start_port,
            "end_port": self.end_port,
            "total_ports": total_ports,
            "open_ports": open_ports,
            "scan_duration": scan_duration,
            "results": results
        }