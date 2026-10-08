# Install MaxGuard without the internet

This folder is the MaxGuard **offline bundle**. It holds everything MaxGuard
needs, including its local AI model, so you can install it on a computer that
has no internet connection. (Jonattan, JON-05)

| File | What it is |
|---|---|
| `images.tar.part-aa`, `images.tar.part-ab`, ... | The MaxGuard and Ollama Docker images, split into parts under 2 GiB |
| `models.tar.gz.part-aa`, ... (or `models.tar.gz`) | The AI model (the files of the `maxguard-ollama-models` volume) |
| `compose.yaml` | Tells Docker how to run MaxGuard |
| `install.sh` | Checks every file, loads the images and the model, starts MaxGuard |
| `uninstall.sh` | Stops MaxGuard and, only if you confirm, deletes its data |
| `sample-telnet.pcap`, `sample-clean-tls13.pcap`, `sample-telnet-zeek-logs.tar.gz` | Small test data recorded on the team's own lab network, to try MaxGuard: the Telnet capture gives one alert, the TLS 1.3 capture gives none |
| `SHA256SUMS` | The SHA-256 checksum of every file above |
| `OFFLINE-INSTALL.md` | This file |

The bundle is built for one kind of processor (`linux/amd64`, that is Intel or
AMD, unless the release says otherwise). Check the release notes before you
copy it to an Apple Silicon Mac or a Raspberry Pi.

## What you need

- Linux, macOS, or Windows with WSL 2 (run every command in the Ubuntu terminal).
- Docker Engine or Docker Desktop with the `docker compose` plugin, already
  installed and running. Check: `docker compose version` prints a version.
- About three times the bundle's size in free disk space (the parts, the loaded
  images, and the model).
- 8 GB of memory or more for the AI model.

## Steps

1. Copy **every** bundle file into one empty folder, for example `~/maxguard-bundle`.
   Keep the part names exactly as they are.

2. Open a terminal in that folder and check the files yourself:

   ```bash
   cd ~/maxguard-bundle
   sha256sum -c SHA256SUMS          # Linux and WSL
   shasum -a 256 -c SHA256SUMS      # macOS
   ```

   Every line must end in `OK`. If one says `FAILED`, copy or download that
   file again. **Why:** a damaged or swapped file must never be loaded.
   `SHA256SUMS` itself is not signed yet. If someone handed you the bundle on
   a USB stick, compare its `SHA256SUMS` with the copy on the GitHub Release
   page: a swapped file only shows up if `SHA256SUMS` is the real one.

3. (Optional) Unplug the network cable or switch Wi-Fi off. MaxGuard installs
   and runs without it.

4. Install:

   ```bash
   bash install.sh
   ```

   `install.sh` checks every checksum again **before** it loads anything, and
   stops if any file fails or a line of `SHA256SUMS` is badly formatted. It
   also refuses a part that `SHA256SUMS` does not list. Then it loads the
   images, puts the AI model into the
   `maxguard-ollama-models` volume, and starts MaxGuard with
   `docker compose up -d --pull never` (`--pull never` means Docker may not
   download anything). The last line is:

   ```text
   MaxGuard is running. Open the dashboard: http://127.0.0.1:8000
   ```

5. Open http://127.0.0.1:8000 in your browser. Only this computer can open it.

6. Try it: on the **Upload** page choose `sample-telnet.pcap`. After a few
   seconds the queue shows a high alert, "Telnet session in cleartext", with an explanation
   from the local AI.

If a checksum is wrong, `install.sh` prints
`ERROR: a file is damaged or was changed. Nothing was installed.` and stops
before `docker load`: nothing has changed on your computer.

## Stop, start, and remove MaxGuard

```bash
docker compose -f compose.yaml down      # stop (your data is kept)
docker compose -f compose.yaml up -d     # start again
bash uninstall.sh                        # stop and remove; asks before deleting data
```

`uninstall.sh` deletes the volumes `maxguard-data` (alerts, reports, audit log)
and `maxguard-ollama-models` (the AI model) only after you type `yes`. Anything
else, even pressing Enter, keeps them. The images stay on the computer; the
script prints the command that removes them.

## Troubleshooting

| Message | What to do |
|---|---|
| `ERROR: docker is not installed` / `Docker is not running` | Install or start Docker Desktop / Docker Engine, then run `bash install.sh` again. |
| `ERROR: SHA256SUMS is missing` or `... is missing from this folder` | Copy every bundle file into the folder. |
| `<file>: FAILED` | That file is damaged. Copy or download it again. |
| `... is not listed in SHA256SUMS` | A file in the folder does not belong to the bundle. Start again with an empty folder. |
| A warning that the volume `maxguard-ollama-models` "already exists but was not created by Docker Compose" | Expected: `install.sh` creates that volume before the first start so the model is in place. |
