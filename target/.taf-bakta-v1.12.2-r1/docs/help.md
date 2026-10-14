taf-bakta 1.12.2-r1
Genome annotation with Bakta 1.12.2; local result viewer with Bakta Web UI 1.4.0.
A production database is NOT bundled. Choose light or full explicitly.

Commands:
  taf-bakta --help
  taf-bakta --version
  taf-bakta --compile
  taf-bakta bakta --help
  taf-bakta -- --version
  taf-bakta bakta_db --help
  taf-bakta bakta_proteins --help
  taf-bakta bakta_io --help
  taf-bakta bakta_plot --help

Install a fixed database (network required; light needs about 9 GiB free):
  mkdir -p "$HOME/.local/share/taffish/databases/bakta"
  TAFFISH_BAKTA_DB_AUTO_MOUNT=0 taf-bakta bakta-download-db-6.0 --type light --db-root \
    "$HOME/.local/share/taffish/databases/bakta/6.0-amr2026-08-07.1" --dry-run
  Repeat without --dry-run to install. Use --type full only with enough disk
  space (about 132 GiB conservative free-space budget). No silent overwrite.
  An administrator may install once under /usr/local/share/taffish/databases/
  bakta/6.0-amr2026-08-07.1; ordinary users then reuse it read-only.
  Interrupted transfers resume on retry; corrupt inputs fail closed.
  For repair, install into a NEW root and switch DB_PATH after verification.

Use a prepared shared database:
  export TAFFISH_BAKTA_DB_PATH=/data/bakta/6.0-amr2026-08-07.1
  TAFFISH_CONTAINER_BACKEND=docker taf-bakta --db /bakta-db \
    --output results --prefix sample --threads 4 genome.fna
  TAFFISH_CONTAINER_BACKEND=podman taf-bakta --db /bakta-db \
    --output results --prefix sample --threads 4 genome.fna
  TAFFISH_CONTAINER_BACKEND=apptainer taf-bakta --db /bakta-db \
    --output results --prefix sample --threads 4 genome.fna
  Omit DB_PATH to discover a prepared personal, /usr/local/share or /opt
  standard root, in that order. Set TAFFISH_BAKTA_DB_AUTO_MOUNT=0 to disable.
  --db is still explicit: discovery exposes a root, not a scientific choice.
  Verify all bytes: taf-bakta bakta-download-db-6.0 --db-root /bakta-db --verify

Manual read-only database bind (disable auto first):
  export TAFFISH_BAKTA_DB_AUTO_MOUNT=0
  TAFFISH_CONTAINER_BACKEND=docker \
    TAFFISH_DOCKER_RUN_ARGS="-v /data/bakta-db:/db:ro" \
    taf-bakta --db /db --output results genome.fna
  TAFFISH_CONTAINER_BACKEND=podman \
    TAFFISH_PODMAN_RUN_ARGS="-v /data/bakta-db:/db:ro" \
    taf-bakta --db /db --output results genome.fna
  TAFFISH_CONTAINER_BACKEND=apptainer \
    TAFFISH_APPTAINER_RUN_ARGS="--bind /data/bakta-db:/db:ro" \
    taf-bakta --db /db --output results genome.fna

Other tasks:
  taf-bakta bakta_proteins --db /bakta-db --output proteins-out proteins.faa
  taf-bakta bakta_plot --output plots results/sample.json
  taf-bakta bakta_io --output converted results/sample.json
  Annotation writes JSON, GFF3, GenBank/EMBL, FASTA, tables, TXT and PNG/SVG.
  Existing output directories are refused unless you explicitly use --force.
  Production annotation can run offline after database preparation.

Local JSON viewer (choose your JSON in the browser; no cloud jobs):
  TAFFISH_CONTAINER_BACKEND=docker \
    TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8080:8080" \
    taf-bakta bakta-viewer --bind 0.0.0.0
  TAFFISH_CONTAINER_BACKEND=podman \
    TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:8080:8080" \
    taf-bakta bakta-viewer --bind 0.0.0.0
  TAFFISH_CONTAINER_BACKEND=apptainer taf-bakta bakta-viewer
  Open http://127.0.0.1:8080/ ; stop with Ctrl-C.
  On xjp: ssh -N -L 8080:127.0.0.1:8080 xjp
  For a different published host port, also give --host-port PORT.
  Logs use a private temporary directory (printed at startup, removed on stop).
  Use --log-dir with an existing private writable host directory to retain logs.
  Apptainer shares host networking: keep its default loopback bind.
  DbXref links require the Internet when clicked; charts and JSON viewing do not.

Platform and troubleshooting:
  Native linux/amd64 only. ARM Docker/Podman requires amd64 emulation;
  native ARM Apptainer is unsupported; use an x86-64 Linux host.
  Missing DB: run the installer or provide --db with a visible prepared path.
  Invalid DB_PATH: fix it or explicitly disable automatic mounting.
  Paths with spaces/reserved bind characters: use backend manual binds.
  Use explicit "taf-bakta bakta INPUT.fna" for a filename-leading invocation.
  For values/paths with spaces, preserve literal quotes for the current core:
    taf-bakta --db /bakta-db --strain '"Lab strain"' --output '"result folder"' genome.fna
  More setup, licenses and validation boundaries: README.md.
  Upstream manual: https://bakta.readthedocs.io/
