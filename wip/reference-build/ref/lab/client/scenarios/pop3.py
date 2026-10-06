import poplib

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
p = poplib.POP3(SERVER, timeout=10)
p.user("labuser")
p.pass_("labpass")
p.quit()
finish()
