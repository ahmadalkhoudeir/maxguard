# MaxGuard engine image: Zeek 9.0.0 + Suricata + the maxguard Python package.
#
# Build from the repository root (the "." at the end is the build context):
#   docker build -f docker/Dockerfile -t maxguard:2.0.0a0 .
# Build the test image that CI uses (adds pytest and the tests folder):
#   docker build -f docker/Dockerfile --target test -t maxguard:test .
#
# Stages: "engine" holds everything both images share, "test" adds the tests,
# and "runtime" (the last stage, so the default) is the image users run.
# Everything is installed at build time: the running container never needs
# the internet.

FROM zeek/zeek:9.0.0 AS engine

# The Zeek image is Debian 13 with Python 3.13, but it has no Python venv
# support (python3-venv) and no Suricata. ca-certificates lets pip check
# PyPI's TLS certificate during the build. The apt lists are deleted because
# nothing in the image runs apt again.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-venv suricata ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Debian refuses "pip install" into its own Python (PEP 668), so MaxGuard gets
# a virtual environment. Putting it first on PATH makes "python", "pip",
# "uvicorn" and "maxguard" mean the venv versions.
RUN python3 -m venv /opt/venv
# The Zeek image sets PYTHONPATH to "/usr/local/zeek/lib/zeek/python:". The
# empty entry after the ":" means "the current folder", so a .py file in the
# current folder could replace a real module. Keep only Zeek's folder.
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/usr/local/zeek/lib/zeek/python" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/maxguard
COPY pyproject.toml ./
COPY cli ./cli
COPY maxguard ./maxguard
COPY mappings ./mappings
RUN pip install --no-cache-dir .

# MaxGuard never needs root: Zeek and Suricata only read capture files here.
# A fixed uid keeps the owner of files in the /data volume the same after a
# rebuild. /data holds the databases, event files and custody keys.
RUN useradd --uid 10001 --user-group --create-home --shell /usr/sbin/nologin maxguard \
    && mkdir /data \
    && chown maxguard:maxguard /data
# The mapping files stay a plain folder (Amory edits them on github.com); the
# pipeline finds them through this variable.
ENV MAXGUARD_DATA_DIR=/data \
    MAXGUARD_MAPPINGS_DIR=/opt/maxguard/mappings


FROM engine AS test

COPY tests ./tests
RUN pip install --no-cache-dir ".[dev]"
USER maxguard
# /opt/maxguard belongs to root, so pytest must not try to write its cache there.
ENV PYTEST_ADDOPTS="-p no:cacheprovider"
CMD ["pytest", "-m", "integration", "-q"]


FROM engine AS runtime

USER maxguard
VOLUME ["/data"]
EXPOSE 8000
# Inside the container the server must listen on 0.0.0.0 or the published
# port cannot reach it; compose publishes that port on the host's 127.0.0.1 only.
CMD ["uvicorn", "maxguard.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
