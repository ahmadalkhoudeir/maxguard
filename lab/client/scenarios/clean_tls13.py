import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4436, ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3, None)
finish()
