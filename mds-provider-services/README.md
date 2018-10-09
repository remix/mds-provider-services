# mds-provider-services

Base Docker image for MDS Provider services.

## Running

The container makes available a Jupyter Notebook server to the host at http://localhost:$NB_HOST_PORT.

This directory is the root of the Notebook server filesystem.

First, ensure the image is up to date locally:

```console
$ docker-compose build --no-cache python-base
```

Then start the notebook server with:

```bash
$ docker-compose up python-base
```

### Configuration

Configure the notebook environment using the following environment variables:

```bash
NB_USER=joyvan
NB_UID=1000
NB_GID=100
NB_HOST_PORT=8888
```