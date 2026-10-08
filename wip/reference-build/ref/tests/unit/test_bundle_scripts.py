"""Tests for the offline bundle scripts (Jonattan, JON-05).

These are unit tests, so they never call the real Docker: each test puts a
fake "docker" program first on PATH. The fake writes every call to a log file
and keeps what the scripts stream into it ("docker load", "tar -x"), so a
test can check what happened, and in which order, in well under a second.
The same scripts were also run against the real Docker with small stand-in
images (see the JON-05 guide).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD = REPO_ROOT / "scripts" / "build-offline-bundle.sh"
INSTALL = REPO_ROOT / "scripts" / "install.sh"
UNINSTALL = REPO_ROOT / "scripts" / "uninstall.sh"

# Small sizes so that splitting is exercised with tiny files.
PART_BYTES = 1000
FAKE_IMAGES = b"fake docker save output " * 100  # 2400 bytes -> 3 parts
FAKE_MODELS = b"fake model archive " * 30  # 570 bytes -> not split

# The fake docker. It answers just enough for the three scripts:
#   save -o FILE ...       writes FAKE_IMAGES to FILE
#   run ... -czf - ...     prints FAKE_MODELS (the model volume as tar.gz)
#   run ... (with stdin)   keeps stdin in restored-models.bin (tar -x)
#   load                   keeps stdin in loaded-images.bin
#   anything else          succeeds and prints nothing
FAKE_DOCKER = """#!/usr/bin/env bash
echo "$*" >>"$FAKE_DIR/docker.log"
case "$1" in
    save)
        while [ "$#" -gt 0 ]; do
            if [ "$1" = "-o" ]; then printf '%s' "$FAKE_IMAGES" >"$2"; fi
            shift
        done
        ;;
    load)
        cat >"$FAKE_DIR/loaded-images.bin"
        ;;
    version)
        echo "linux/amd64"
        ;;
    run)
        case "$*" in
            *"-czf -"*) printf '%s' "$FAKE_MODELS" ;;
            *" -i "*) cat >"$FAKE_DIR/restored-models.bin" ;;
        esac
        ;;
esac
exit 0
"""


def make_fake_docker(tmp_path: Path) -> dict[str, str]:
    """Write the fake docker into tmp_path/bin and return an env that uses it."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(FAKE_DOCKER)
    docker.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["FAKE_DIR"] = str(tmp_path)
    env["FAKE_IMAGES"] = FAKE_IMAGES.decode()
    env["FAKE_MODELS"] = FAKE_MODELS.decode()
    return env


def docker_calls(tmp_path: Path) -> list[str]:
    log = tmp_path / "docker.log"
    return log.read_text().splitlines() if log.exists() else []


def run_script(
    script: Path, env: dict[str, str], *args: str, cwd: Path, stdin: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(script), *args],
        cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=30,
    )


def build_bundle(tmp_path: Path, env: dict[str, str]) -> Path:
    """Run build-offline-bundle.sh with the fake docker; return the dist folder."""
    model_dir = tmp_path / "fake-model"
    (model_dir / "blobs").mkdir(parents=True)
    (model_dir / "blobs" / "sha256-fake").write_bytes(b"not a real model")
    offline_doc = tmp_path / "OFFLINE-INSTALL.md"
    offline_doc.write_text("# Install MaxGuard without the internet\n")
    dist = tmp_path / "dist"
    build_env = dict(env)
    build_env.update(
        MG_IMAGE="alpine:3.20",
        OLLAMA_IMAGE="hello-world:latest",
        MODEL_SOURCE_DIR=str(model_dir),
        MODEL_VOLUME="test-models",
        OFFLINE_DOC=str(offline_doc),
        DIST_DIR=str(dist),
        PART_BYTES=str(PART_BYTES),
    )
    result = run_script(BUILD, build_env, cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    return dist


@pytest.fixture
def bundle(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """A freshly built bundle (fake images) and the env with the fake docker."""
    if shutil.which("bash") is None:
        pytest.skip("bash is not installed")
    env = make_fake_docker(tmp_path)
    dist = build_bundle(tmp_path, env)
    (tmp_path / "docker.log").unlink()  # tests check only the install's calls
    env["MAXGUARD_SKIP_START"] = "1"
    return dist, env


def sha256_lines(folder: Path) -> dict[str, str]:
    """SHA256SUMS as {file name: hex digest}."""
    lines = (folder / "SHA256SUMS").read_text().splitlines()
    return {line[66:]: line[:64] for line in lines}


def test_build_splits_big_files_and_lists_every_file(bundle):
    dist, _ = bundle
    names = sorted(p.name for p in dist.iterdir())
    assert names == [
        "OFFLINE-INSTALL.md", "SHA256SUMS", "compose.yaml",
        "images.tar.part-aa", "images.tar.part-ab", "images.tar.part-ac",
        "install.sh", "models.tar.gz", "sample-clean-tls13.pcap",
        "sample-telnet-zeek-logs.tar.gz", "sample-telnet.pcap", "uninstall.sh",
    ]
    sums = sha256_lines(dist)
    assert sorted(sums) == [n for n in names if n != "SHA256SUMS"]
    for name, digest in sums.items():
        assert hashlib.sha256((dist / name).read_bytes()).hexdigest() == digest
    parts = sorted(dist.glob("images.tar.part-*"))
    assert b"".join(p.read_bytes() for p in parts) == FAKE_IMAGES


def test_build_refuses_a_dist_folder_that_is_not_empty(tmp_path):
    env = make_fake_docker(tmp_path)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "images.tar.part-zz").write_text("left over from an old build")
    offline_doc = tmp_path / "OFFLINE-INSTALL.md"
    offline_doc.write_text("# Install MaxGuard without the internet\n")
    env.update(DIST_DIR=str(dist), OFFLINE_DOC=str(offline_doc))
    result = run_script(BUILD, env, cwd=REPO_ROOT)
    assert result.returncode != 0
    assert "is not empty" in result.stderr
    assert "save" not in "\n".join(docker_calls(tmp_path))


def test_install_loads_the_joined_parts_and_restores_the_model(bundle, tmp_path):
    dist, env = bundle
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "loaded-images.bin").read_bytes() == FAKE_IMAGES
    assert (tmp_path / "restored-models.bin").read_bytes() == FAKE_MODELS
    calls = docker_calls(tmp_path)
    assert any(call.startswith("load") for call in calls)
    assert not any(call.startswith("compose -f") for call in calls)  # start skipped


def test_install_starts_compose_without_pulling(bundle, tmp_path):
    dist, env = bundle
    env["MAXGUARD_SKIP_START"] = "0"
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "compose -f compose.yaml up -d --pull never" in docker_calls(tmp_path)
    assert "http://127.0.0.1:8000" in result.stdout


def test_install_refuses_a_changed_byte_before_loading(bundle, tmp_path):
    dist, env = bundle
    part = dist / "images.tar.part-ab"
    data = bytearray(part.read_bytes())
    data[10] ^= 0x01  # flip one bit of one byte
    part.write_bytes(bytes(data))
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode != 0
    assert "images.tar.part-ab: FAILED" in result.stdout
    assert "Nothing was installed" in result.stderr
    calls = docker_calls(tmp_path)
    assert not any(c.startswith(("load", "run", "volume", "compose -f")) for c in calls)


def test_install_refuses_a_part_that_sha256sums_does_not_list(bundle, tmp_path):
    dist, env = bundle
    (dist / "images.tar.part-ad").write_bytes(b"an extra part")
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode != 0
    assert "images.tar.part-ad is not listed in SHA256SUMS" in result.stderr
    assert not any(c.startswith("load") for c in docker_calls(tmp_path))


def test_install_refuses_a_badly_formatted_checksum_line(bundle, tmp_path):
    # Without --strict, sha256sum skips a bad line with a warning and still
    # succeeds, and the "is it listed?" check would then accept the extra part.
    dist, env = bundle
    (dist / "images.tar.part-ad").write_bytes(b"an extra part")
    with (dist / "SHA256SUMS").open("a") as sums:
        sums.write("z" * 64 + "  images.tar.part-ad\n")
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode != 0
    assert "Nothing was installed" in result.stderr
    assert not any(c.startswith("load") for c in docker_calls(tmp_path))


def test_install_unpacks_the_model_without_network(bundle, tmp_path):
    dist, env = bundle
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    tar_runs = [c for c in docker_calls(tmp_path) if c.startswith("run") and "tar" in c]
    assert tar_runs and all("--network none" in c for c in tar_runs)


def test_install_refuses_a_missing_part(bundle, tmp_path):
    dist, env = bundle
    (dist / "images.tar.part-ac").unlink()
    result = run_script(dist / "install.sh", env, cwd=tmp_path)
    assert result.returncode != 0
    assert not any(c.startswith("load") for c in docker_calls(tmp_path))


def test_uninstall_keeps_the_volumes_unless_you_type_yes(tmp_path):
    env = make_fake_docker(tmp_path)
    result = run_script(UNINSTALL, env, cwd=tmp_path, stdin="\n")
    assert result.returncode == 0, result.stderr
    calls = docker_calls(tmp_path)
    assert "compose -p maxguard down" in calls
    assert not any(call.startswith("volume rm") for call in calls)
    assert "Kept the volumes" in result.stdout


def test_uninstall_keeps_the_volumes_without_a_keyboard(tmp_path):
    # No input at all (end of file), for example when run from cron.
    env = make_fake_docker(tmp_path)
    result = run_script(UNINSTALL, env, cwd=tmp_path, stdin="")
    assert result.returncode == 0, result.stderr
    assert not any(call.startswith("volume rm") for call in docker_calls(tmp_path))
    assert "Kept the volumes" in result.stdout


def test_uninstall_yes_flag_deletes_both_volumes(tmp_path):
    env = make_fake_docker(tmp_path)
    result = run_script(UNINSTALL, env, "--yes", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    calls = docker_calls(tmp_path)
    assert "volume rm maxguard-data" in calls
    assert "volume rm maxguard-ollama-models" in calls


def test_uninstall_typed_yes_deletes_both_volumes(tmp_path):
    env = make_fake_docker(tmp_path)
    result = run_script(UNINSTALL, env, cwd=tmp_path, stdin="yes\n")
    assert result.returncode == 0, result.stderr
    assert "volume rm maxguard-data" in docker_calls(tmp_path)


def test_uninstall_rejects_an_unknown_flag(tmp_path):
    env = make_fake_docker(tmp_path)
    result = run_script(UNINSTALL, env, "--force", cwd=tmp_path)
    assert result.returncode == 2
    assert docker_calls(tmp_path) == []
