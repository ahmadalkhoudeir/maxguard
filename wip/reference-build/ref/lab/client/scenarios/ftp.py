import ftplib

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
ftp = ftplib.FTP(SERVER, timeout=10)
ftp.login("labuser", "labpass")
ftp.nlst()
ftp.quit()
finish()
