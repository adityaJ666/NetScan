from core.scanner import PortScanner


scanner = PortScanner(
    target="127.0.0.1",
    start_port=1,
    end_port=100
)

result = scanner.scan()

print(f"Target: {result['target']}")
print(f"IP Address: {result['ip']}")
print()

if result["results"]:
    print("Open Ports:")
    
    for item in result["results"]:
        print(
            f"Port {item['port']} | "
            f"{item['state']} | "
            f"Service: {item['service']}"
        )
else:
    print("No open ports found.")