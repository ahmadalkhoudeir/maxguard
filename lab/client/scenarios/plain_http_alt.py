import urllib.request

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
urllib.request.urlopen(f"http://{SERVER}:8080/", timeout=10).read()
finish()
