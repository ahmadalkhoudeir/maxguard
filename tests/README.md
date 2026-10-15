# Tests

| Folder | What goes here |
|---|---|
| `unit/` | Fast tests. No Docker, no network. Run in seconds. |
| `integration/` | Tests marked `@pytest.mark.integration`. They need Zeek and Suricata, so they run inside the engine image. |
| `pcaps/` | Synthetic or publicly licensed captures, each listed in `pcaps/SOURCES.md`. |
| `fixtures/` | Saved Zeek/Suricata logs and small hand-written fixtures (KAR-02). |
| `expected/` | Expected findings for each capture (KAR-03). |

## Run the unit tests

From the repository root, inside your virtual environment:

```bash
pip install pytest
pytest -m "not integration" -q
```

Expected output:

```
1 passed, 1 deselected in 0.01s
```

`echo $?` should then print `0`. If you see `no tests ran`, you are not in the
repository root or your branch is older than this folder (`git pull` on `main`).
