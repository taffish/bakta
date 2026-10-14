# 固定 Node digest 和官方 Web tag/commit；并非永久归档。失效时先查网络、官方身份与架构，
# 原样恢复只能接受匹配 SHA256 的可信副本；新材料需新身份及完整构建/离线/GUI 验证。
FROM node:22.22.2-bookworm-slim@sha256:9f6d5975c7dca860947d3915877f85607946403fc55349f39b4bc3688448bb6e AS web
ADD --checksum=sha256:e232136d9c76fd49b7e1f2d3e5a14d030cd32a49eceded5d86613df71ac56d37 https://codeload.github.com/ag-computational-bio/bakta-web-ui/tar.gz/3bb62efac08b7f0b14384336569d93f22f6b5728 /tmp/web.tar.gz
WORKDIR /web
RUN tar -xzf /tmp/web.tar.gz --strip-components=1 && rm /tmp/web.tar.gz
COPY docker/web/main.ts src/main.ts
COPY docker/web/Offline.vue src/Offline.vue
COPY docker/web/patch-local.mjs /tmp/patch-local.mjs
COPY docker/web/collect-licenses.mjs /tmp/collect-licenses.mjs
RUN node /tmp/patch-local.mjs
# npm ci 使用官方 package-lock 的固定版本/integrity；registry 内容可下架，生命周期脚本须审计。
# 失败不能跳过 integrity/盲重生 lock 或追 latest。Node/npm 不进入最终镜像。
RUN npm ci --no-audit --no-fund && node /tmp/collect-licenses.mjs && npm run build-only

# 官方基础镜像固定 digest，只声明其 linux/amd64；不能把 ARM 主机模拟说成 native ARM。
# digest 不能保证 registry 永久可得；当前无新增活动 APK/APT 解析，后续增加时应另审漂移。
FROM --platform=linux/amd64 docker.io/oschwengers/bakta:v1.12.0@sha256:4cb7c3f8327483d661013b5bcbb33f0dc71119d661c4c887ec1dce6d81542c60 AS runtime


# 以下版本 URL 不等于永久可得；源码、build wheels 和 DIAMOND 包分别由 SHA256 校验。
# 区分网络/TLS、404、截断及真实内容变化；恢复旧材料须匹配原哈希，采用新材料须重验后继。
ARG BAKTA_VERSION=1.12.2
ARG BAKTA_COMMIT=18be6c2b75d6ef708da4a1edf1dd37dbdd899b12
ARG BAKTA_SOURCE_URL=https://codeload.github.com/oschwengers/bakta/tar.gz/refs/tags/v1.12.2
ARG BAKTA_SOURCE_SHA256=828afd3b4f7dcb0ebb51e12c8daecfe9258262b52d3c01db8ea23413c4bf1e05
ARG SETUPTOOLS_WHEEL=setuptools-80.9.0-py3-none-any.whl
ARG SETUPTOOLS_WHEEL_URL=https://files.pythonhosted.org/packages/a3/dc/17031897dae0efacfea57dfd3a82fdd2a2aeb58e0ff71b77b87e44edc772/setuptools-80.9.0-py3-none-any.whl
ARG SETUPTOOLS_WHEEL_SHA256=062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922
ARG WHEEL_WHEEL=wheel-0.45.1-py3-none-any.whl
ARG WHEEL_WHEEL_URL=https://files.pythonhosted.org/packages/0b/2c/87f3254fd8ffd29e4c02732eee68a83a1d3c346ae39bc6822dcbcb697f2b/wheel-0.45.1-py3-none-any.whl
ARG WHEEL_WHEEL_SHA256=708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248
ARG DIAMOND_PACKAGE=diamond-2.2.0-he361c42_0.conda
ARG DIAMOND_PACKAGE_URL=https://conda.anaconda.org/bioconda/linux-64/diamond-2.2.0-he361c42_0.conda
ARG DIAMOND_PACKAGE_SHA256=c5ff249ab7655a6b79c1de0fdeeba8ebfa640b81a9f6a9a6588a15508abe34a9

LABEL maintainer="taffish@163.com"

USER root

ENV PATH=/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV LANG=C
ENV LC_ALL=C

ENTRYPOINT []
CMD []
SHELL ["/bin/sh", "-c"]

RUN set -eux; \
    wget -q -O /tmp/bakta.tar.gz "${BAKTA_SOURCE_URL}"; \
    echo "${BAKTA_SOURCE_SHA256}  /tmp/bakta.tar.gz" | sha256sum -c -; \
    wget -q -O "/tmp/${SETUPTOOLS_WHEEL}" "${SETUPTOOLS_WHEEL_URL}"; \
    echo "${SETUPTOOLS_WHEEL_SHA256}  /tmp/${SETUPTOOLS_WHEEL}" | sha256sum -c -; \
    wget -q -O "/tmp/${WHEEL_WHEEL}" "${WHEEL_WHEEL_URL}"; \
    echo "${WHEEL_WHEEL_SHA256}  /tmp/${WHEEL_WHEEL}" | sha256sum -c -; \
    wget -q -O "/tmp/${DIAMOND_PACKAGE}" "${DIAMOND_PACKAGE_URL}"; \
    echo "${DIAMOND_PACKAGE_SHA256}  /tmp/${DIAMOND_PACKAGE}" | sha256sum -c -; \
    mkdir -p /tmp/bakta-src /opt/taffish/bakta/testdata /usr/local/share/licenses/bakta; \
    tar -xzf /tmp/bakta.tar.gz -C /tmp/bakta-src --strip-components=1; \
    micromamba install -y -n base --offline "/tmp/${DIAMOND_PACKAGE}"; \
    python3 -m pip install --no-cache-dir --no-deps "/tmp/${SETUPTOOLS_WHEEL}" "/tmp/${WHEEL_WHEEL}"; \
    python3 -m pip install --no-cache-dir --no-build-isolation --no-deps --force-reinstall /tmp/bakta-src; \
    python3 -m pip uninstall -y setuptools wheel; \
    cp /tmp/bakta-src/LICENSE /usr/local/share/licenses/bakta/LICENSE; \
    cp -R /tmp/bakta-src/test/db-light /opt/taffish/bakta/testdata/db-light; \
    rm -f /opt/taffish/bakta/testdata/db-light/amrfinderplus-db; \
    cp -R /tmp/bakta-src/test/db/amrfinderplus-db /opt/taffish/bakta/testdata/db-light/amrfinderplus-db; \
    cp /tmp/bakta-src/test/data/NC_002127.1.fna /opt/taffish/bakta/testdata/input.fna; \
    cp /tmp/bakta-src/test/data/user-proteins.faa /opt/taffish/bakta/testdata/user-proteins.faa; \
    printf '%s\n' \
      'Bundled upstream v1.12.2 fixture for offline TAFFISH smoke only.' \
      'This reduced test database is not a production Bakta database.' \
      > /opt/taffish/bakta/testdata/README.txt; \
    printf '%s\n' \
      "version=${BAKTA_VERSION}" \
      "commit=${BAKTA_COMMIT}" \
      "source_url=${BAKTA_SOURCE_URL}" \
      "source_sha256=${BAKTA_SOURCE_SHA256}" \
      "setuptools_wheel_sha256=${SETUPTOOLS_WHEEL_SHA256}" \
      "wheel_wheel_sha256=${WHEEL_WHEEL_SHA256}" \
      "base_image=docker.io/oschwengers/bakta:v1.12.0@sha256:4cb7c3f8327483d661013b5bcbb33f0dc71119d661c4c887ec1dce6d81542c60" \
      "diamond_package=${DIAMOND_PACKAGE}" \
      "diamond_package_url=${DIAMOND_PACKAGE_URL}" \
      "diamond_package_sha256=${DIAMOND_PACKAGE_SHA256}" \
      > /opt/taffish/bakta/source.txt; \
    rm -rf /tmp/bakta.tar.gz /tmp/bakta-src "/tmp/${SETUPTOOLS_WHEEL}" "/tmp/${WHEEL_WHEEL}" "/tmp/${DIAMOND_PACKAGE}" /root/.cache/pip; \
    bakta --version 2>&1 | grep -Fx "bakta 1.12.2" >/dev/null; \
    bakta --help 2>&1 | grep -F "usage: bakta" >/dev/null; \
    bakta_db --help 2>&1 | grep -F "{list,download,install,update}" >/dev/null; \
    bakta_db --version 2>&1 | grep -Fx "bakta_db 1.12.2" >/dev/null; \
    bakta_proteins --help 2>&1 | grep -F "usage: bakta_proteins" >/dev/null; \
    bakta_plot --help 2>&1 | grep -F "usage: bakta_plot" >/dev/null; \
    bakta_io --help 2>&1 | grep -F "usage: bakta_io" >/dev/null; \
    python3 -c 'import bakta; from bakta import plot; assert bakta.__version__ == "1.12.2"; assert bakta.__db_schema_version__ == 6; assert len(plot.calc_gc_content("G")[0]) > 0; assert len(plot.calc_gc_skew("G")[0]) > 0'; \
    python3 -m pip check; \
    grep -Fx "commit=${BAKTA_COMMIT}" /opt/taffish/bakta/source.txt >/dev/null; \
    grep -Fx "source_sha256=${BAKTA_SOURCE_SHA256}" /opt/taffish/bakta/source.txt >/dev/null; \
    grep -Fx "diamond_package_sha256=${DIAMOND_PACKAGE_SHA256}" /opt/taffish/bakta/source.txt >/dev/null; \
    test -s /opt/taffish/bakta/testdata/db-light/version.json; \
    test -s /opt/taffish/bakta/testdata/input.fna; \
    test -s /opt/taffish/bakta/testdata/user-proteins.faa; \
    diamond version 2>&1 | grep -F "diamond version 2.2.0" >/dev/null; \
    blastn -version 2>&1 | grep -F "blastn: 2.17.0" >/dev/null; \
    makeblastdb -version 2>&1 | grep -F "makeblastdb: 2.17.0" >/dev/null; \
    amrfinder --version 2>&1 | grep -Fx "4.2.7" >/dev/null; \
    amrfinder_update --version 2>&1 | grep -Fx "4.2.7" >/dev/null; \
    tRNAscan-SE -h 2>&1 | grep -F "tRNAscan-SE 2.0.12" >/dev/null; \
    aragorn -h 2>&1 | grep -F "ARAGORN v1.2.41" >/dev/null; \
    cmscan -h 2>&1 | grep -F "INFERNAL 1.1.5" >/dev/null; \
    pilercr -version 2>&1 | grep -F "pilercr v1.06" >/dev/null

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

COPY --from=web /web/dist /opt/taffish/bakta/web
COPY --from=web /web/LICENSE /usr/local/share/licenses/bakta-web-ui/LICENSE
COPY --from=web /web/THIRD_PARTY_NOTICES.txt /usr/local/share/licenses/bakta-web-ui/THIRD_PARTY_NOTICES.txt
COPY --from=web /web/package-lock.json /opt/taffish/bakta/web-package-lock.json
COPY docker/bakta-resources.py /usr/local/bin/bakta-download-db-6.0
COPY docker/amr-inputs.json /opt/taffish/bakta/amr-inputs.json
COPY docker/bakta-viewer /usr/local/bin/bakta-viewer
COPY docker/bakta-smoke /usr/local/bin/bakta-smoke
COPY docker/collect-runtime-licenses.py /tmp/collect-runtime-licenses.py
# helper 的外部 DB 另固定 Zenodo record/MD5 和 NCBI snapshot/SHA256，不在分析时获取 latest。
# source.txt/安装 manifest 是 provenance；不是新的输入 lock，也不承诺永久离线重建。
RUN set -eu; \
    chmod 0755 /usr/local/bin/bakta-download-db-6.0 /usr/local/bin/bakta-viewer /usr/local/bin/bakta-smoke; \
    python3 /tmp/collect-runtime-licenses.py; \
    rm /tmp/collect-runtime-licenses.py; \
    rm -rf /opt/conda/pkgs /opt/conda/include /opt/conda/man /root/.cache; \
    mkdir -p /bakta-db; \
    bakta-download-db-6.0 --help >/dev/null; \
    bakta-viewer --help >/dev/null

# final stage 才移除基础镜像的旧缓存层；保留运行库、数据、许可证和上游科学实现。
FROM scratch
COPY --from=runtime / /
ENV PATH=/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV LANG=C
ENV LC_ALL=C
WORKDIR /tmp

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=bakta
