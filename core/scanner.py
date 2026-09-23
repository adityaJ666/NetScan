import socket
import time


class PortScanner:

    def __init__(self, target, start_port=1, end_port=1024):

        self.target = target
        self.start_port = start_port
        self.end_port = end_port

    def scan(self):

        start_time = time.time()

        # Resolve hostname/IP
        ip_address = socket.gethostbyname(
            self.target
        )

        results = []

        for port in range(
            self.start_port,
            self.end_port + 1
        ):

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            sock.settimeout(0.2)

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

                    results.append(
                        {
                            "port": port,
                            "state": "Open",
                            "service": service
                        }
                    )

            finally:

                sock.close()

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

        open_ports = len(
            results
        )

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