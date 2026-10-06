import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4431, ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1)
finish()
