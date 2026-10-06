import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4435, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2)
finish()
