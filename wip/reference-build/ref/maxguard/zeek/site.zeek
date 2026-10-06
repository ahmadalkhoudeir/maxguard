##! MaxGuard's Zeek site policy (Jakub, JAK-01). MaxGuard loads this file
##! instead of Zeek's own "local" policy, on capture files and on the live sensor.
##!
##! It is Zeek 9.0.0's share/zeek/site/local.zeek without the three scripts that
##! send network traffic of their own. MaxGuard never contacts anything
##! (CLAUDE.md rule 1) and a sensor only listens (rule 5):
##!
##! - frameworks/files/detect-MHR asks Team Cymru's Malware Hash Registry, with a
##!   DNS query, about the SHA-1 of every executable, PDF, video ... seen on the
##!   network. That also tells an outside service what people downloaded.
##! - protocols/ssh/interesting-hostnames makes a reverse DNS lookup of both ends
##!   of every successful SSH login.
##! - frameworks/notice/extend-email/hostnames makes reverse DNS lookups for
##!   notice e-mails.
##!
##! Zeek runs as its own program, so the Python offline guard (maxguard/offline.py)
##! cannot stop it: leaving these scripts out is the fix. Everything else is the
##! same as local.zeek, so the logs MaxGuard reads do not change.

# Kept as in local.zeek: it only salts file IDs (fuid), and a different value
# would change every file ID in the test fixtures.
redef digest_salt = "Please change this value.";

@load misc/loaded-scripts
@load misc/capture-loss
@load misc/stats

@load frameworks/software/vulnerable
@load frameworks/software/version-changes
@load-sigs frameworks/signatures/detect-windows-shells

@load protocols/ftp/software
@load protocols/smtp/software
@load protocols/ssh/software
@load protocols/http/software

@load protocols/dns/detect-external-names
@load protocols/ftp/detect

@load protocols/conn/known-hosts
@load protocols/conn/known-services
@load protocols/ssl/known-certs

@load protocols/ssl/validate-certs
@load protocols/ssl/log-hostcerts-only

@load protocols/ssh/geo-data
@load protocols/ssh/detect-bruteforcing

@load protocols/http/detect-sql-injection

@load frameworks/files/hash-all-files
