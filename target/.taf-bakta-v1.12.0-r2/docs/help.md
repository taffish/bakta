taf-bakta 1.12.0-r2

TAFFISH tool app for Bakta 1.12.0. The default upstream command is bakta.

Important database note:
  Real annotation requires a compatible Bakta database. The production database
  is not bundled. Bakta 1.12.0 requires database schema 6. bakta_db list,
  download, and update need network access for online database metadata.

Usage:
  taf-bakta --help
  taf-bakta --version
  taf-bakta --compile
  taf-bakta [bakta options...] INPUT.fna
  taf-bakta bakta [bakta options...] INPUT.fna
  taf-bakta helper-command [args...]
  taf-bakta -- [option-leading bakta args...]

Wrapper options:
  --help       Show this TAFFISH help text.
  --version    Show the TAFFISH package version.
  --compile    Print generated shell instead of running it.
  --           Pass following option-leading arguments to bakta.

Show upstream help and database compatibility:
  taf-bakta bakta --help
  taf-bakta bakta --version
  taf-bakta -- --help
  taf-bakta bakta_db list

Prepare a persistent database directory:
  mkdir -p bakta-db
  taf-bakta bakta_db download --output "$PWD/bakta-db" --type light
  taf-bakta bakta_db download --output "$PWD/bakta-db" --type full

Run genome annotation:
  taf-bakta \
    --db "$PWD/bakta-db/db-light" \
    --output bakta-out \
    --prefix sample1 \
    --threads 8 \
    genome.fna

Protein bulk annotation:
  taf-bakta bakta_proteins \
    --db "$PWD/bakta-db/db-light" \
    --output protein-bakta \
    --prefix proteins1 \
    --threads 8 \
    proteins.faa

Regenerate outputs or plots from JSON:
  taf-bakta bakta_io --output regenerated --prefix sample1 sample1.json
  taf-bakta bakta_plot --output plots --prefix sample1 sample1.json

Helper and dependency commands:
  bakta_db, bakta_proteins, bakta_plot, bakta_io, diamond, blastn, makeblastdb,
  amrfinder, tRNAscan-SE, aragorn, cmscan, pilercr

Inputs:
  Bakta is designed for bacterial genomes, plasmids, and MAGs. It accepts FASTA
  input, including compressed FASTA. Optional inputs include replicon metadata,
  trusted proteins, trusted HMMs, and user-provided regions.

Typical genome outputs:
  <prefix>.tsv, <prefix>.gff3, <prefix>.gbff, <prefix>.embl, <prefix>.fna,
  <prefix>.ffn, <prefix>.faa, <prefix>.inference.tsv,
  <prefix>.hypotheticals.tsv, <prefix>.hypotheticals.faa, <prefix>.txt,
  <prefix>.png, <prefix>.svg, <prefix>.json

Boundaries:
  The Bakta database, AMRFinderPlus database content, input genomes, submission
  templates, and project reports are not included. Runtime database downloads
  require network access and a persistent writable host directory.

Platform:
  Native container platform is linux/amd64. Docker and Podman runs request
  --platform linux/amd64 from this app. On arm64 hosts this is emulation, not
  native arm64 support.

Docs:
  https://bakta.readthedocs.io/
  https://github.com/oschwengers/bakta
