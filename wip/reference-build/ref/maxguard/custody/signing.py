"""Ed25519 signatures for chain of custody (v2.0).

MaxGuard signs the reports and evidence files it produces so that anyone with
the public key can later check that a file was not changed after MaxGuard
wrote it. Ed25519 is used because its keys are small, signing is fast, and it
has no settings (curve, hash, padding) that a user could get wrong.

Where the keys live
-------------------
Key files are secrets and must never be inside the git repository. They go in
the MaxGuard data directory, in a "keys" folder (see key_dir_for):
- in the Docker image: /data/keys (the /data volume, outside the code)
- on a developer laptop: ./data/keys (data/ is listed in .gitignore)

The private key file is created with permissions 0600 (only its owner can read
it) and is not password protected: the file permissions are the protection.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

KEY_SUBDIR = "keys"
PRIVATE_KEY_NAME = "custody_ed25519_private.pem"
PUBLIC_KEY_NAME = "custody_ed25519_public.pem"


def key_dir_for(data_dir: Path) -> Path:
    """The folder that holds the custody keys inside a MaxGuard data directory."""
    return Path(data_dir) / KEY_SUBDIR


def generate_keypair(key_dir: Path) -> tuple[Path, Path]:
    """Create a new key pair in key_dir and return (private_key_path, public_key_path).

    Refuses to replace an existing private key: a new key would make every
    signature made with the old key impossible to check.
    """
    key_dir = Path(key_dir)
    key_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_path = key_dir / PRIVATE_KEY_NAME
    public_path = key_dir / PUBLIC_KEY_NAME
    if private_path.exists():
        raise FileExistsError(f"{private_path} already exists; refusing to replace a custody key")

    private_key = Ed25519PrivateKey.generate()
    write_private_file(private_path, private_key_pem(private_key))
    public_path.write_bytes(public_key_pem(private_key.public_key()))
    return private_path, public_path


def private_key_pem(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_pem(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def write_private_file(path: Path, data: bytes) -> None:
    """Write a secret file that only its owner can read.

    The 0o600 mode is given when the file is created, so the key is never
    readable by other users, not even for a moment. O_EXCL makes the call fail
    if the file already exists instead of overwriting it.
    """
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def load_private_key(private_key_path: Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"{private_key_path} is not an Ed25519 private key")
    return key


def load_public_key(public_key_path: Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(Path(public_key_path).read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError(f"{public_key_path} is not an Ed25519 public key")
    return key


def sign(data: bytes, private_key_path: Path) -> bytes:
    """Return the 64-byte Ed25519 signature of data.

    Ed25519 signatures are deterministic: the same key and the same data always
    give the same signature (no random numbers are involved).
    """
    return load_private_key(private_key_path).sign(data)


def verify(data: bytes, signature: bytes, public_key_path: Path) -> bool:
    """True if signature was made over exactly these bytes by the matching private key."""
    public_key = load_public_key(public_key_path)
    try:
        public_key.verify(signature, data)
    except InvalidSignature:
        return False
    return True
