# 1. Install poetry dependencies to /site-packages
# 2. Start with a clean python image (no poetry)
# 3. Copy /site-packages from poetry image to python image
# 4. Copy the rest of the project files
ARG PY_VER=3.11

FROM python:${PY_VER} AS poetry
WORKDIR /app
COPY poetry.lock pyproject.toml ./
# build dependencies for matplotlib and pandas
RUN pip install poetry poetry-plugin-export wheel && \
    poetry export | pip install --target=/site-packages -r /dev/stdin

FROM python:${PY_VER}
ARG PY_VER
WORKDIR /app
COPY --from=poetry /site-packages /usr/local/lib/python${PY_VER}/site-packages
COPY ./kiltisbot ./kiltisbot/
ENTRYPOINT [ "python", "-m", "kiltisbot.bot" ]
