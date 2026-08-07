# taf-bakta

TAFFISH wrapper for [Bakta](https://github.com/oschwengers/bakta), a rapid and
standardized annotation tool for bacterial genomes, plasmids, and
metagenome-assembled genomes (MAGs).

This app packages Bakta `1.12.1-r1` from the exact upstream `v1.12.1` source
tag, layered on the official `oschwengers/bakta:v1.12.0` runtime with the
upstream-required DIAMOND `2.2.0` update. At packaging time, upstream had not
yet published `v1.12.1` to Docker Hub, PyPI, or Bioconda. Bakta is a
database-driven annotator: the software is packaged in the image, but the
production Bakta database is intentionally external.

## Package Identity

- name: `bakta`
- command: `taf-bakta`
- version: `1.12.1-r1`
- kind: `tool`
- image: `ghcr.io/taffish/bakta:1.12.1-r1`
- upstream: Bakta tag `v1.12.1`
- upstream commit: `2cb1a7dd38a3f25690f358a717f88ec5e84907aa`
- upstream source SHA-256:
  `3e43e4763f71c125ed992abaf7809c9e54f981fc13d52bbd16d0c818178a3b7f`
- runtime version: `bakta 1.12.1`
- required database schema: `6`
- current compatible database listed by Bakta: `6.0`
- upstream Docker base: `oschwengers/bakta:v1.12.0`
- upstream Docker digest:
  `sha256:4cb7c3f8327483d661013b5bcbb33f0dc71119d661c4c887ec1dce6d81542c60`
- DIAMOND package: `diamond-2.2.0-he361c42_0.conda`
- DIAMOND package SHA-256:
  `c5ff249ab7655a6b79c1de0fdeeba8ebfa640b81a9f6a9a6588a15508abe34a9`
- build-only wheels: `setuptools 80.9.0`, `wheel 0.45.1`; both are
  checksum-verified and removed after installing Bakta
- default command: `bakta`
- native platform: `linux/amd64`
- app license: Apache-2.0
- upstream software license: GPL-3.0

## Install

```sh
taf install bakta
```

Install the exact release:

```sh
taf install bakta 1.12.1-r1
```

For local testing before this app is published to the public index:

```sh
taf install --from .
```

## Database Boundary

Bakta requires a compatible Bakta database for real genome or protein
annotation. This TAFFISH image does not bundle the production database because
the database is large, versioned scientific data and should live in a
persistent project or site data directory.

Bakta `1.12.1` requires database schema `6`. Upstream currently documents
database `6.0` from Zenodo record `14916843` as compatible. `bakta_db list`,
`download`, and `update` consult online database metadata and therefore need
network access. Upstream documents two database types:

- `light`: smaller and faster; upstream documents about 1.3 GB compressed and
  3.9 GB uncompressed for DB `6.0`
- `full`: best annotation coverage; upstream documents about 30 GB compressed
  and 84 GB uncompressed for DB `6.0`

Download a database into a persistent host directory:

```sh
mkdir -p bakta-db
taf-bakta bakta_db download --output "$PWD/bakta-db" --type light
```

For the full database:

```sh
taf-bakta bakta_db download --output "$PWD/bakta-db" --type full
```

Use an installed database either by parameter or environment variable:

```sh
taf-bakta --db "$PWD/bakta-db/db-light" genome.fna

BAKTA_DB="$PWD/bakta-db/db-light" taf-bakta genome.fna
```

Runtime database downloads require network access. Offline and flow-oriented
runs should pre-populate a database directory and pass `--db` or `BAKTA_DB`.
If the database was installed manually, AMRFinderPlus may need its internal DB
prepared once inside the Bakta database directory:

```sh
taf-bakta amrfinder_update --force_update --database "$PWD/bakta-db/db-light/amrfinderplus-db"
```

`bakta_db download` handles this setup automatically and is the recommended
route.

## Basic Usage

Show TAFFISH wrapper help and version:

```sh
taf-bakta --help
taf-bakta --version
taf-bakta --compile
```

Show upstream Bakta help and version:

```sh
taf-bakta bakta --help
taf-bakta bakta --version
taf-bakta -- --help
taf-bakta -- --version
```

Annotate a bacterial genome:

```sh
taf-bakta \
  --db "$PWD/bakta-db/db-light" \
  --output bakta-out \
  --prefix sample1 \
  --threads 8 \
  genome.fna
```

Annotate with organism metadata and INSDC-compliant output settings:

```sh
taf-bakta \
  --db "$PWD/bakta-db/db-full" \
  --output bakta-compliant \
  --prefix ecoli123 \
  --genus Escherichia \
  --species coli \
  --strain K12 \
  --locus-tag ECO123 \
  --compliant \
  --threads 8 \
  genome.fna
```

Run protein bulk annotation:

```sh
taf-bakta bakta_proteins \
  --db "$PWD/bakta-db/db-light" \
  --output protein-bakta \
  --prefix proteins1 \
  --threads 8 \
  proteins.faa
```

Generate or regenerate output files from a Bakta JSON result:

```sh
taf-bakta bakta_io --output regenerated --prefix sample1 bakta-out/sample1.json
```

Generate plots from a Bakta JSON result:

```sh
taf-bakta bakta_plot --output plots --prefix sample1 bakta-out/sample1.json
```

## Command Mode

The default upstream command is `bakta`. Normal Bakta options can be passed
directly:

```sh
taf-bakta --db "$PWD/bakta-db/db-light" genome.fna
```

Because `command_mode = true`, a first non-option argument is treated as an
executable inside the same container. Use that form for helper commands and
runtime dependency probes:

```sh
taf-bakta bakta_db list
taf-bakta bakta_db download --help
taf-bakta bakta_proteins --help
taf-bakta bakta_plot --help
taf-bakta bakta_io --help
taf-bakta diamond version
taf-bakta amrfinder --version
taf-bakta tRNAscan-SE -h
taf-bakta aragorn -h
```

Use `--` for option-leading arguments intended for the default upstream
command when they share names with TAFFISH wrapper options:

```sh
taf-bakta -- --help
taf-bakta -- --version
```

## Inputs And Outputs

Bakta accepts bacterial genomes and plasmids in FASTA format, including
compressed FASTA. It is designed for bacterial isolates, plasmids, and MAGs,
not eukaryotic genome annotation. Optional inputs include replicon metadata,
user-provided feature regions, trusted proteins, and trusted HMMs.

Typical genome annotation outputs include:

- `<prefix>.tsv`
- `<prefix>.gff3`
- `<prefix>.gbff`
- `<prefix>.embl`
- `<prefix>.fna`
- `<prefix>.ffn`
- `<prefix>.faa`
- `<prefix>.inference.tsv`
- `<prefix>.hypotheticals.tsv`
- `<prefix>.hypotheticals.faa`
- `<prefix>.txt`
- `<prefix>.png`
- `<prefix>.svg`
- `<prefix>.json`

Set `--output DIR` and `--prefix NAME` to keep outputs predictable. The wrapper
does not create a TAFFISH-specific output layout.

## Runtime Contents

The image preserves the official Bakta `v1.12.0` dependency runtime, replaces
the Bakta Python package with the checksum-verified `v1.12.1` source, updates
DIAMOND to the exact `2.2.0` package required by upstream, and resets the
container entrypoint/PATH so TAFFISH can expose the upstream CLI and helper
commands directly. The source archive, source commit, base image digest, and
DIAMOND package checksum are recorded in `/opt/taffish/bakta/source.txt`.

Bundled runtime commands include:

- `bakta`, `bakta_db`, `bakta_proteins`, `bakta_plot`, `bakta_io`
- `amrfinder` and `amrfinder_update`
- Python 3 with Bakta modules
- DIAMOND `2.2.0`
- NCBI BLAST+ `2.17.0`
- AMRFinderPlus `4.2.7`
- tRNAscan-SE `2.0.12`
- Aragorn `1.2.41`
- Infernal `1.1.5`
- PILER-CR `1.06`
- Pyrodigal, PyHMMER, Biopython, xopen, requests, PyYAML, alive-progress, and
  pyCirclize from the upstream conda environment

The production Bakta database, AMRFinderPlus database content, project genomes,
submission templates, and downstream comparative-genomics reports are not
included.

The image does contain the upstream `v1.12.1` reduced test DB and tiny plasmid
fixture under `/opt/taffish/bakta/testdata` solely for deterministic offline
smoke. It is incomplete and must not be used for scientific annotation.

## Platform

The official upstream Docker base used by this release is published as a
single `linux/amd64` image. This TAFFISH app declares native support for
`linux/amd64` only and requests `--platform linux/amd64` for Docker and Podman
runs from `src/main.taf`.

On Apple Silicon or other arm64 hosts, Docker/Podman may run the image through
amd64 emulation. That is not native arm64 support. Apptainer behavior depends
on host and site configuration.

## Smoke Coverage

The smoke checks validate:

- Bakta `1.12.1` version/help output
- helper CLIs: `bakta_db`, `bakta_proteins`, `bakta_plot`, `bakta_io`
- Python module version and required database schema `6`
- the upstream 1.12.1 short-sequence GC and GC-skew regression using a 1 bp
  sequence
- source commit/archive and DIAMOND package provenance markers
- `bakta_db --version` and the built-in required DB schema `6`
- representative runtime dependencies are available
- a positive offline annotation using the bundled reduced upstream test DB
  produces JSON, GFF3, PNG, and SVG outputs
- a tiny FASTA call fails cleanly when `--db` points to a missing database and
  does not create annotation outputs

The smoke is intentionally offline-safe. It does not call `bakta_db list` or
download a production Bakta database. The bundled test DB validates mechanics,
not scientific completeness. Biological annotation must still be validated
with a chosen production `light` or `full` Bakta DB and a project-appropriate
bacterial or plasmid input.

## Boundaries

This is a tool app, not a TAFFISH flow. It does not batch samples, choose
organism metadata, validate assembly quality, manage database provenance for a
project, submit genomes to INSDC, download inputs, or aggregate cohort-level
reports.

Runtime network access is not required for normal annotation after the database
has been prepared. Commands that explicitly download or update databases need
network access and a writable persistent host directory.

## Upstream

- Project: <https://github.com/oschwengers/bakta>
- Documentation: <https://bakta.readthedocs.io/>
- Release: <https://github.com/oschwengers/bakta/releases/tag/v1.12.1>
- Database DOI: <https://doi.org/10.5281/zenodo.14916843>
- Citation: Schwengers et al. 2021, DOI `10.1099/mgen.0.000685`

TAFFISH packaging files are Apache-2.0. Upstream Bakta and its runtime
dependencies remain under their own licenses; Bakta records GPL-3.0 in its
CITATION metadata and setup metadata.
