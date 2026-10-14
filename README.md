# taf-bakta

Bakta for reproducible bacterial, plasmid and MAG annotation, with an optional
local-only browser viewer. The default command remains the upstream CLI.

## Package Identity

- name / command / kind: `bakta` / `taf-bakta` / `tool`
- package: `1.12.2-r1`; image: `ghcr.io/taffish/bakta:1.12.2-r1`
- wrapper license: Apache-2.0; Bakta and Bakta Web UI: GPL-3.0
- native platform: **linux/amd64 only**; no GPU required
- upstream: [Bakta v1.12.2](https://github.com/oschwengers/bakta/releases/tag/v1.12.2)
- fixed commit: `18be6c2b75d6ef708da4a1edf1dd37dbdd899b12`
- codeload SHA256: `828afd3b4f7dcb0ebb51e12c8daecfe9258262b52d3c01db8ea23413c4bf1e05`
- fixed Web UI: `v1.4.0`, commit `3bb62efac08b7f0b14384336569d93f22f6b5728`
- database contract: Bakta DB 6.0, explicitly selected full/light, plus AMRFinder 2026-08-07.1

## What This App Packages

The exact upstream Bakta source is installed without scientific-code patches,
on the official 1.12.0 runtime pinned by digest
`sha256:4cb7c3f8327483d661013b5bcbb33f0dc71119d661c4c887ec1dce6d81542c60`.
DIAMOND is the upstream-required 2.2.0 linux-64 package, pinned by SHA256.
The Dockerfile also pins the temporary setuptools/wheel inputs; no resolver
silently upgrades the base runtime's Python dependencies.

Bakta 1.12.2 restores circular plots for `--meta`. The packaging adds a
transactional fixed-resource installer and a local-only entry to the official
Bakta Web viewing components. It does not add a cloud submission service.

## Scope

Supported surfaces: CLI genome/protein annotation; `bakta_io` conversions;
`bakta_plot` PNG/SVG; local JSON statistics, searchable annotation table,
genome browser and circular-plot SVG export. The viewer uses upstream result
parsing and coordinate conversion, not a replacement scientific implementation.

Not included: production databases in the image; cloud jobs, Kubernetes,
accounts/admin APIs, Baktfold workflows, a native ARM build, or a claim of
complete scientific validation of arbitrary genomes. The bundled reduced
upstream test database and AMR test snapshot are **smoke fixtures only**.

## Container Contents

- `bakta`, `bakta_db`, `bakta_proteins`, `bakta_io`, `bakta_plot`
- Python/Biopython, Pyrodigal, PyHMMER, pyCirclize/Matplotlib
- DIAMOND 2.2.0, BLAST+ 2.17.0, AMRFinderPlus 4.2.7 (including updater/indexer),
  tRNAscan-SE 2.0.12, Aragorn 1.2.41, Infernal 1.1.5, PILER-CR 1.06
- `bakta-download-db-6.0`: fixed, explicit, atomic database setup/verification
- `bakta-viewer`: local static HTTP service, lifecycle and security adapter
- `bakta-smoke`: independent offline installation probes; not a production workflow
- upstream licenses and Web dependency notices under `/usr/local/share/licenses/`

No Node runtime or npm cache is needed at runtime. The final stage removes
Conda package caches, headers and development manuals while preserving runtime
libraries, scientific data and licenses.

## Installation and Usage

```sh
taf install bakta 1.12.2-r1
taf-bakta --help
taf-bakta bakta --help
taf-bakta -- --version
taf-bakta --db /bakta-db --output results --prefix sample --threads 4 genome.fna
taf-bakta bakta_proteins --db /bakta-db --output proteins-out proteins.faa
taf-bakta bakta_plot --output plots results/sample.json
taf-bakta bakta_io --output converted results/sample.json
```

Before publication use `taf build` and `target/taf-bakta-v1.12.2-r1`;
`taf install --from .` is another local-install route. The examples assume a
prepared database exposed at `/bakta-db` as described below.

## Command Mode

`--help`, `--version` and `--compile` are wrapper options. Use an explicit
executable for upstream help/subcommands, e.g. `taf-bakta bakta_db list`.
Option-leading arguments go to default `bakta`; `--` also passes upstream
options. A filename-leading invocation must be `taf-bakta bakta INPUT.fna`,
because the wrapper otherwise interprets the first word as a command.

With the current core, retain literal quotes around values/paths containing
spaces (ordinary shell quotes alone do not survive command compilation):

```sh
taf-bakta --db /bakta-db --strain '"Lab strain"' --output '"result folder"' genome.fna
```

## Inputs and Output Notes

Inputs are bacterial/plasmid/MAG FASTA (also compressed), compatible databases,
optional trusted proteins/HMMs, replicon metadata and user regions. These
project-specific inputs are not globally downloaded for the user.

Outputs include JSON, GFF3, GenBank, EMBL, nucleotide/protein FASTA, annotation
and inference tables, TXT statistics and PNG/SVG plots. Bakta refuses an
existing output directory unless `--force` is explicitly supplied.
The CLI `--force` policy is separate from the immutable database installer.

## Resources, Databases, and Platform

### Fixed resources and licensing

Bakta requires DB schema 6. The [DB 6.0 Zenodo record](https://zenodo.org/records/14916843)
declares **CC-BY-4.0**, open access, by Oliver Schwengers (2025). Preserve its
attribution, DOI and constituent-database notices in downstream work; the
software GPL does not substitute for database terms. No login or per-user
acceptance is required by this published record.

| Selection | Exact file | Compressed bytes | Official MD5 | Approximate unpacked |
| --- | --- | ---: | --- | --- |
| light | db-light.tar.xz | 1,344,199,496 | 4a6e059ded39e9c5537ef4137d2f5648 | 3.9 GB |
| full | db.tar.xz | 31,921,769,288 | 4c1115e40abfa2b464ae5dd988bdd88e | 84 GB |

The helper also installs the explicit **AMRFinder 4.2 / 2026-08-07.1**
snapshot from NCBI HTTPS. Every input has a pinned SHA256 and byte count in
`docker/amr-inputs.json`; local BLAST/HMM indexes are then built. NCBI's
[public-domain notice](https://github.com/ncbi/amr/blob/amrfinder_v4.2.7/amrfinder_update.cpp)
covers that software/database. Its directory is called `amrfinderplus-db/latest`
because Bakta requires that path; it is a fixed physical directory here, not
a moving online selector. It is a separate identity from the AMR version used
to curate the original Bakta DB annotations.
The verified DB archive's legacy AMR subtree (including its relative
`latest -> 2024-12-18.1` link) is deliberately replaced by this explicitly
fixed expert snapshot and freshly generated indexes. Other DB members retain
their original bytes; no archive symlink is followed or installed.

The upstream `bakta_db` downloader remains available, but consults mutable
catalog metadata and invokes the latest AMR updater. It does not supply this
helper's fixed snapshot, lock, staging or atomic-install contract. Do not run
upstream updates against a prepared TAFFISH shared root.

### Personal installation

Choose one type explicitly; there is no default full download:

```sh
mkdir -p "$HOME/.local/share/taffish/databases/bakta"
TAFFISH_BAKTA_DB_AUTO_MOUNT=0 taf-bakta bakta-download-db-6.0 \
  --type light --db-root "$HOME/.local/share/taffish/databases/bakta/6.0-amr2026-08-07.1" --dry-run
# Inspect the plan, then repeat without --dry-run.
```

Allow about 9 GiB free for light, or 132 GiB for full using the conservative
preflight budget (compressed cache, extraction, AMR indexes and at least 1 GiB
reserve). Real free space is checked on the destination filesystem; a small
tmpfs is not suitable. Download caches and installation locks are siblings of
the destination. Setup needs network and a writable **actual host bind**;
normal annotation does not download anything and can run offline.

### Administrator once, ordinary users thereafter

An administrator can create
`/usr/local/share/taffish/databases/bakta` (or the analogous `/opt` path), then
run the same helper with the standard versioned root. The installer process
must actually have permission to that host directory. For paths outside the
wrapper's normal home/current-directory binds, explicitly bind the **parent**:

```sh
# Run as the authorized site administrator; parent must already exist.
TAFFISH_BAKTA_DB_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=docker \
  TAFFISH_DOCKER_RUN_ARGS="-v /usr/local/share/taffish/databases/bakta:/install" \
  taf-bakta bakta-download-db-6.0 --type light --db-root /install/6.0-amr2026-08-07.1
# Podman: same mount with TAFFISH_PODMAN_RUN_ARGS (rootless cannot gain host root).
# Apptainer: TAFFISH_APPTAINER_RUN_ARGS="--bind /usr/local/share/taffish/databases/bakta:/install"
```

Completed directories are 0755 and files 0644; installer ownership is retained.
An actual administrator-owned root is read-only to ordinary users, who need no
sudo or network for reuse. A personally owned 0644 database remains writable
by its owner: permissions alone do not make it administrator-owned.

### Discovery, override, integrity and fallback

Mount priority: `TAFFISH_BAKTA_DB_PATH`, then
`~/.local/share/taffish/databases/bakta/6.0-amr2026-08-07.1`,
`/usr/local/share/taffish/databases/bakta/6.0-amr2026-08-07.1`, then
`/opt/taffish/databases/bakta/6.0-amr2026-08-07.1`.
A root symlink resolves to its physical directory. Invalid explicit or
higher-priority roots fail closed, without silently falling back or downloading.
Use a different root plus DB_PATH to keep full and light simultaneously.

The wrapper checks READY against manifest/inventory hashes, rejects internal
symlinks and checks each member's size, then binds the chosen root read-only at
`/bakta-db`. This fast startup check is **not** a complete data-byte hash audit.
Run `taf-bakta bakta-download-db-6.0 --db-root /bakta-db --verify` for that audit.
Neither discovery nor mounting chooses scientific data for the command: still
pass `--db /bakta-db`. Explicit upstream `--db` remains supported independently.

`TAFFISH_BAKTA_DB_AUTO_MOUNT=0` disables both discovery and override. The
automatic bind interface rejects whitespace/reserved path characters; use a
safe physical path or a manually quoted backend bind for such paths.

| Backend | Shared read-only database | Local viewer |
| --- | --- | --- |
| Docker | automatic mount; manual `-v HOST:/db:ro` | publish host loopback port, helper binds container 0.0.0.0 |
| Podman | automatic mount; manual `-v HOST:/db:ro` | same, rootless host permissions still apply |
| Apptainer | automatic mount; manual `--bind HOST:/db:ro` | host network; helper binds 127.0.0.1 |

The help manual contains full minimal commands for all three backends.
Docker/Podman request `--platform linux/amd64` intrinsically. ARM host execution
would be emulation, not native ARM support. ARM-native Apptainer cannot execute
this x86-64 SIF; use an x86-64 Linux host. No backend exception is implied.

### Interrupted downloads, corrupt inputs and repair

Installation uses a private 0700 cache, a nonblocking advisory lock, HTTPS
Range resume with bounded retries, size/checksum checks, safe tar extraction,
same-filesystem staging and an atomic final rename. A directory alone never
counts as installed. Successful reinstallation validates the entire inventory
before returning an idempotent success.

A handled failure removes its own staging and leaves cache partials for retry.
A killed process releases its lock automatically; an orphan `.NAME.stage-*`
may remain but is never selected as ready. Inspect exact ownership/path and
confirm no installer is running before deleting such a stage or corrupt
`.NAME.cache/HASH[.part]`; do not clear unrelated caches. Verified inputs can
also be supplied with `--source-dir`, using the original filenames.

If an origin refuses a particular host (for example HTTP 403), obtain the
same fixed inputs on a permitted machine and transfer them without renaming.
Place the selected DB archive and **all** files listed in
`docker/amr-inputs.json` together in `inputs/`. The installer still checks the
original byte counts and checksums; a network error is not permission to use
different data or relax verification. With an existing physical
`bakta-install/` parent that is not writable by group/others, choose one backend:

```sh
TAFFISH_BAKTA_DB_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=docker \
  TAFFISH_DOCKER_RUN_ARGS="--network none --user $(id -u):$(id -g) -v $PWD/inputs:/inputs:ro -v $PWD/bakta-install:/install:rw" \
  taf-bakta bakta-download-db-6.0 --type light --db-root /install/6.0-amr2026-08-07.1 --source-dir /inputs
TAFFISH_BAKTA_DB_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=podman \
  TAFFISH_PODMAN_RUN_ARGS="--network none --userns keep-id -v $PWD/inputs:/inputs:ro -v $PWD/bakta-install:/install:rw" \
  taf-bakta bakta-download-db-6.0 --type light --db-root /install/6.0-amr2026-08-07.1 --source-dir /inputs
TAFFISH_BAKTA_DB_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=apptainer \
  TAFFISH_APPTAINER_RUN_ARGS="--net --network none --bind $PWD/inputs:/inputs:ro --bind $PWD/bakta-install:/install:rw" \
  taf-bakta bakta-download-db-6.0 --type light --db-root /install/6.0-amr2026-08-07.1 --source-dir /inputs
```

Use paths without spaces/reserved bind characters for these short examples.
If a previous failed import left a corrupt `.part`, first inspect that exact
file and confirm the installer has stopped, remove only that partial, then
repeat with the correct inputs. A second successful installation verifies
and reuses the completed root; it does not overwrite it.

There is deliberately no destructive database `--force`. If an existing root
is corrupt or has a different selection, installation refuses to overwrite it.
Install to a new physical root, verify it, switch DB_PATH, and retain the old
root until consumers have migrated. This also avoids losing a usable database
during an interrupted update.

## Local Browser Viewer

```sh
TAFFISH_CONTAINER_BACKEND=docker \
  TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8080:8080" \
  taf-bakta bakta-viewer --bind 0.0.0.0
```

Open the printed URL and choose a Bakta JSON. Podman uses the corresponding
backend/RUN_ARGS variables. Apptainer uses `taf-bakta bakta-viewer` with the
backend selected; it shares host networking, so retain loopback binding.
For remote xjp use `ssh -N -L 8080:127.0.0.1:8080 xjp`. If host/container
ports differ, pass the actual `--host-port`; the printed tunnel uses that port.

The helper prints starting/URL/SSH/stop/log information before serving, and
prints ready separately. Ctrl-C exits 130, TERM exits 143, and closes the
endpoint. Temporary logs are private and removed on exit; `--log-dir` accepts
an existing owned private directory on a writable host bind to retain logs.
No authentication is provided: never expose this service on a public interface.

Use an interactive terminal and Ctrl-C. TERM was validated by signaling the
Docker/Podman client launched by the real wrapper (outer wrapper returns 143),
and the Apptainer session. Killing only the wrapper shell, or terminating a
whole Podman terminal process group at once, is not a service-manager contract:
terminal hangup can interrupt the engine's signal forwarding. No daemon mode
or PID-only supervisor integration is claimed.

The current TAFFISH 0.11.0 `taf run` buffers service startup output until exit
and returns 1 on Ctrl-C in the tested Linux client. Do not use it for this
long-running viewer. For a source checkout use the tested built wrapper:

```sh
taf build
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8080:8080" \
  target/taf-bakta-v1.12.2-r1 bakta-viewer --bind 0.0.0.0
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:8080:8080" \
  target/taf-bakta-v1.12.2-r1 bakta-viewer --bind 0.0.0.0
TAFFISH_CONTAINER_BACKEND=apptainer target/taf-bakta-v1.12.2-r1 bakta-viewer
```

The official viewing components are retained. A separate local entry excludes
the cloud router/API/admin initialization. Small presentation/security changes
label upstream dummy job timestamps as viewer-session time and escape DbXref
text/URLs; annotation data and algorithms are not changed. The CSP restricts
background requests to local resources. Input changes clear the old result so
an invalid replacement cannot leave stale statistics visible. Local-shell CSS
wraps tabs and permits scrolling wide plots/tables on narrow screens. DbXref
links are explicit external
navigation. Example JSON is bundled. Exported circular SVG is a viewer
visualization, not a new annotation result. No noVNC/X11 desktop is involved.

## Source, Build and Reproducibility Boundary

Build from the app root, matching the unchanged canonical Action:

```sh
docker build --platform linux/amd64 -f docker/Dockerfile .
```

Action is copied byte-for-byte from fresh `taf new`. It is not hand-edited.
The Web builder uses a digest-pinned Node image and upstream npm lock/integrity;
only assets/licenses reach the runtime image. Dockerfile comments identify
actual source-availability risks, including helper downloads. A fixed URL,
digest or checksum does not guarantee upstream perpetual retention. A trusted
recovery copy must match the original checksum; adopting new materials needs a
new identity and complete verification, not skipped TLS/checksums or a blind
lockfile refresh. Provenance receipts are not a substitute for an input lock.

## Tests and Smoke Test

Independent manifest probes check all commands, version/provenance, dependency
versions, a real three-CDS annotation, `--meta` plots, JSON conversion,
negative database handling, resource plans and local HTTP lifecycle.
Every probe owns private scratch under /tmp; none downloads a production DB.
The 120 MB upstream AMR fixture is retained because it enables a genuine
offline CDS/expert path rather than an all-features-skipped empty result.

The native amd64 candidate passed 140 independent fresh/offline probes:
28 exact manifest commands on each Docker/Podman normal/read-only root and
the same-image read-only Apptainer SIF. Real wrappers passed 36 CLI/plot/IO
checks, 39 production-light resource checks and 9 service lifecycle checks
across the three backends. The complete light DB was downloaded, indexed,
verified and used for annotation; a separate container UID can verify it but
cannot write through the read-only bind. Eighteen tiny installer tests cover
resume, integrity, locking, failure recovery and safe extraction; their
synthetic indexer is not presented as a production installation.

An additional 30 real-wrapper checks closed the writable-install gate on
Docker, Podman and Apptainer: each installed the complete fixed light + AMR
inputs through an actual writable host bind, then verified byte/mtime/owner/
permission-preserving idempotence, failed-import partial retention and retry,
corrupt-root refusal, read-only reuse and a real three-CDS annotation.
Host-side inventory checks covered 194 files (about 4.13 GB) per installation,
0755 directories and 0644 files, without a half-ready final root or leftover
staging. Recovery of the failed import included inspecting and removing its
exact corrupt partial; this is not automatic repair of an immutable root.
All installation/annotation calls were forced offline. The official archive
was retrieved on another host with the same fixed checksum because the test
server received HTTP 403; the `--source-dir` path was used, not a changed URL
or relaxed checksum. A newly converted same-OCI SIF also passed all 28 exact
probes again. Earlier unchanged-image CLI/GUI evidence was rechecked, not rerun.

Standard site-path precedence was checked in 16 private-namespace cases,
without modifying real system paths or claiming an actual root deployment.
Full DB installation, arbitrary production genomes and ARM-host emulation
were not separately validated. The optional full selection shares the tested
installer, but its 32 GB archive was not downloaded in this QA run.

The local viewer was checked in a real browser with a generated three-CDS
result, example data, invalid-input clearing, table filtering, genome tracks,
circular SVG download and narrow-screen scrolling. This is engineering visual
QA, not a claim of user acceptance or complete scientific validation.
Developer-mode `taf run` service limitations are documented above.

Final runtime size is recorded in the release notes. Source audit confirmed
all 37 upstream Bakta Python files byte-for-byte and 496 retained dependency
notice files. Source/image identities and raw verification receipts are kept
in the maintainer evidence archive. Local validation and publish dry-run do
not mean that an image, tag, Release or Index record has been published.

## References

- [Bakta manual](https://bakta.readthedocs.io/)
- [Bakta](https://doi.org/10.1099/mgen.0.000685)
- [Bakta Web](https://doi.org/10.1093/nar/gkaf335)
- [Official Web source](https://github.com/ag-computational-bio/bakta-web-ui/tree/3bb62efac08b7f0b14384336569d93f22f6b5728)
