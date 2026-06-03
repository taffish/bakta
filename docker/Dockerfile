ARG BAKTA_BASE_PLATFORM=linux/amd64
FROM --platform=${BAKTA_BASE_PLATFORM} docker.io/oschwengers/bakta:v1.12.0@sha256:4cb7c3f8327483d661013b5bcbb33f0dc71119d661c4c887ec1dce6d81542c60

LABEL maintainer="taffish@163.com"

USER root

ENV PATH=/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C
ENV LC_ALL=C

ENTRYPOINT []
CMD []
SHELL ["/bin/sh", "-c"]

RUN set -eux; \
    bakta --version 2>&1 | grep -F "bakta 1.12.0" >/dev/null; \
    bakta --help 2>&1 | grep -F "usage: bakta" >/dev/null; \
    bakta_db --help 2>&1 | grep -F "{list,download,install,update}" >/dev/null; \
    bakta_db --version 2>&1 | grep -F "bakta_db 1.12.0" >/dev/null; \
    bakta_proteins --help 2>&1 | grep -F "usage: bakta_proteins" >/dev/null; \
    bakta_plot --help 2>&1 | grep -F "usage: bakta_plot" >/dev/null; \
    bakta_io --help 2>&1 | grep -F "usage: bakta_io" >/dev/null; \
    python3 -c 'import bakta; assert bakta.__version__ == "1.12.0"; assert bakta.__db_schema_version__ == 6'; \
    diamond version 2>&1 | grep -F "diamond version 2.1.21" >/dev/null; \
    blastn -version 2>&1 | grep -F "blastn: 2.17.0" >/dev/null; \
    makeblastdb -version 2>&1 | grep -F "makeblastdb: 2.17.0" >/dev/null; \
    amrfinder --version 2>&1 | grep -Fx "4.2.7" >/dev/null; \
    tRNAscan-SE -h 2>&1 | grep -F "tRNAscan-SE 2.0.12" >/dev/null; \
    aragorn -h 2>&1 | grep -F "ARAGORN v1.2.41" >/dev/null; \
    cmscan -h 2>&1 | grep -F "INFERNAL 1.1.5" >/dev/null; \
    pilercr -h 2>&1 | grep -F "pilercr v1.06" >/dev/null

RUN set -eux; \
    tmp=/tmp/taf-bakta-db-boundary; \
    rm -rf "${tmp}"; \
    mkdir -p "${tmp}"; \
    printf '>tiny\nATGAAATAA\n' > "${tmp}/tiny.fa"; \
    if bakta --db "${tmp}/no-db" --output "${tmp}/out" --prefix tiny "${tmp}/tiny.fa" > "${tmp}/run.log" 2>&1; then \
      cat "${tmp}/run.log" >&2; \
      exit 1; \
    fi; \
    grep -Ei "database|db" "${tmp}/run.log" >/dev/null; \
    test ! -e "${tmp}/out/tiny.gff3"; \
    rm -rf "${tmp}"

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=bakta
