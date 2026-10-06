"""Create the lab's test certificates. All are fake and only valid in the lab.

A lab CA signs every certificate except "selfsigned", so each TLS scenario
triggers exactly one certificate rule. The SHA-1 certificate is made with the
openssl command because the cryptography library refuses to sign with SHA-1
(it is insecure, which is exactly why the lab needs one).
"""
import datetime as dt
import subprocess

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def name(cn):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def save(prefix, key, cert):
    with open(f"{prefix}.key", "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM,
                                  serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption()))
    with open(f"{prefix}.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def build(subject, issuer, public_key, signing_key, start, end, ca=False):
    return (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
            .public_key(public_key).serial_number(x509.random_serial_number())
            .not_valid_before(start).not_valid_after(end)
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
            .sign(signing_key, hashes.SHA256()))


VALID = (dt.datetime(2026, 1, 1), dt.datetime(2036, 1, 1))
EXPIRED = (dt.datetime(2020, 1, 1), dt.datetime(2020, 12, 31))

ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ca_name = name("MaxGuard Lab CA")
save("ca", ca_key, build(ca_name, ca_name, ca_key.public_key(), ca_key, *VALID, ca=True))

for prefix, key_size, dates in (("good", 2048, VALID), ("expired", 2048, EXPIRED),
                                ("weak", 1024, VALID)):
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    save(prefix, key, build(name(f"{prefix}.lab.invalid"), ca_name, key.public_key(),
                            ca_key, *dates))

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cn = name("selfsigned.lab.invalid")
save("selfsigned", key, build(cn, cn, key.public_key(), key, *VALID))

subprocess.run(["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
                "-keyout", "sha1.key", "-out", "sha1.csr", "-subj", "/CN=sha1.lab.invalid"],
               check=True, capture_output=True)
subprocess.run(["openssl", "x509", "-req", "-in", "sha1.csr", "-CA", "ca.crt",
                "-CAkey", "ca.key", "-CAcreateserial", "-sha1", "-days", "3650",
                "-out", "sha1.crt"], check=True, capture_output=True)
print("certificates written")
