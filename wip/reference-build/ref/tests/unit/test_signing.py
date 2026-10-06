"""Tests for maxguard.custody.signing (Ed25519 chain-of-custody signatures)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from maxguard.custody import signing

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = b'{"schema": "maxguard.report/2", "findings": []}'


@pytest.fixture
def keys(tmp_path: Path) -> tuple[Path, Path]:
    return signing.generate_keypair(tmp_path / "keys")


def test_generate_keypair_writes_two_pem_files(keys):
    private_path, public_path = keys
    assert private_path.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----")
    assert public_path.read_bytes().startswith(b"-----BEGIN PUBLIC KEY-----")


@pytest.mark.skipif(os.name != "posix", reason="file modes are a POSIX feature")
def test_private_key_is_readable_by_owner_only(keys):
    private_path, _ = keys
    assert stat.S_IMODE(private_path.stat().st_mode) == 0o600


def test_generate_keypair_refuses_to_replace_existing_key(keys, tmp_path):
    with pytest.raises(FileExistsError):
        signing.generate_keypair(tmp_path / "keys")


def test_signature_verifies(keys):
    private_path, public_path = keys
    signature = signing.sign(REPORT, private_path)
    assert len(signature) == 64
    assert signing.verify(REPORT, signature, public_path) is True


def test_signature_is_deterministic(keys):
    private_path, _ = keys
    assert signing.sign(REPORT, private_path) == signing.sign(REPORT, private_path)


def test_changed_data_fails_verification(keys):
    private_path, public_path = keys
    signature = signing.sign(REPORT, private_path)
    changed = REPORT.replace(b"[]", b"[1]")
    assert signing.verify(changed, signature, public_path) is False


def test_signature_from_another_key_fails(keys, tmp_path):
    private_path, _ = keys
    _, other_public_path = signing.generate_keypair(tmp_path / "other")
    signature = signing.sign(REPORT, private_path)
    assert signing.verify(REPORT, signature, other_public_path) is False


@pytest.mark.parametrize("bad_signature", [b"", b"short", bytes(64), bytes(65)])
def test_malformed_signature_fails(keys, bad_signature):
    _, public_path = keys
    assert signing.verify(REPORT, bad_signature, public_path) is False


def test_sign_rejects_a_non_ed25519_key(tmp_path):
    ec_key = ec.generate_private_key(ec.SECP256R1())
    pem = ec_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_path = tmp_path / "ec.pem"
    key_path.write_bytes(pem)
    with pytest.raises(TypeError):
        signing.sign(REPORT, key_path)


def test_key_dir_is_inside_the_data_dir():
    assert signing.key_dir_for(Path("/data")) == Path("/data/keys")


@pytest.mark.skipif(
    not (REPO_ROOT / ".gitignore").exists(), reason="not a git checkout (e.g. the Docker image)"
)
def test_data_dir_is_git_ignored():
    # Keys live under data/ on a laptop; this keeps them out of every commit.
    ignored = (REPO_ROOT / ".gitignore").read_text().splitlines()
    assert "data/" in ignored
