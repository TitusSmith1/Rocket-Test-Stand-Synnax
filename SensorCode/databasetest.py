import synnax as sy

client = sy.Synnax(host="192.168.172.56", port=9090, username="synnax", password="seldon", secure=False)

try:
    p1 = client.channels.retrieve("pressure_1")
    print(f"Total data points stored in pressure_1: {p1.size}")
except Exception as e:
    print(f"Error checking database: {e}")
