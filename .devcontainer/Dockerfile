FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

# Keep image lean but include common build tooling for Python packages.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
