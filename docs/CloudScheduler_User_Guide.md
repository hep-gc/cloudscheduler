# Cloud Scheduler User Documentation

## 1. Overview

Cloud Scheduler is a cloud resource orchestration and management tool for scheduling and managing compute resources, users, groups, jobs, and metadata. The project is distributed as a Python-based command-line application and includes support for cloud backends, data collection agents, and a web frontend.

The current repository is the Python 3 rewrite of the original Cloud Scheduler application, with CLI commands built around the `cloudscheduler` executable and a documentation set generated with Sphinx.

## 2. What is included in the project

The repository includes:

- CLI tooling under `cli/bin/`
- Command documentation under `cli/man/`
- Sphinx documentation under `docs/source/`
- User and group management logic
- Cloud metadata and VM management commands
- Job management and scheduling metadata
- Data collector services for Condor/OpenStack reporting
- Integration points for a web frontend and API-oriented backend

## 3. System requirements

The README indicates the CLI expects Python 3. On CentOS 7, the following installation pattern is recommended:

```bash
sudo yum install python36 python36-devel
ln -sf /bin/python36 /bin/python3
python36 -m pip install PyYAML
python36 -m pip install requests
```

For modern Python 3 environments, the package should work with the default Python 3 toolchain and `pip`.

## 4. Installation and setup

1. Clone the repository into a suitable location, such as `/opt/cloudscheduler`.
2. Ensure Python 3 and required dependencies are installed.
3. Make the CLI command available in your shell environment.
4. Configure the server endpoint and authentication details with the Cloud Scheduler CLI.

Example defaults configuration:

```bash
cloudscheduler defaults set
```

The project documentation notes that tests can be configured with dedicated `unit-test` and `unit-test-un` server defaults.

## 5. Configuration

Cloud Scheduler uses a layered configuration model:

- Global defaults
- Server configuration
- Cloud configuration
- Group defaults
- Metadata definitions

Common CLI configuration commands include:

```bash
cloudscheduler server config
cloudscheduler defaults list
cloudscheduler defaults set
cloudscheduler my settings
```

The project also includes command reference pages for server, cloud, user, group, metadata, and VM operations.

## 6. Basic CLI usage

The main command is:

```bash
cloudscheduler
```

The CLI exposes subcommands such as:

- `cloud`
- `user`
- `group`
- `vm`
- `job`
- `metadata`
- `defaults`
- `my`
- `server`
- `helpers`

Common examples:

```bash
cloudscheduler cloud list
cloudscheduler user list
cloudscheduler group list
cloudscheduler vm list
cloudscheduler job list
```

Use the built-in help system to discover detailed options for each command:

```bash
cloudscheduler --help
cloudscheduler cloud --help
cloudscheduler user add --help
```

## 7. Cloud and VM management

Cloud Scheduler can manage cloud resources and virtual machines. Typical tasks include:

- adding a cloud definition
- querying cloud status
- listing available VM images
- listing VM instances
- updating metadata and defaults

Example commands:

```bash
cloudscheduler cloud add
cloudscheduler cloud list
cloudscheduler cloud status
cloudscheduler vm list
cloudscheduler vm update
```

Metadata entities can be attached and updated as part of cloud and group definitions, supporting richer resource descriptions and group-level defaults.

## 8. Users, groups, and permissions

The platform supports role-oriented user and group management. Typical flows include:

```bash
cloudscheduler user add
cloudscheduler user list
cloudscheduler user update
cloudscheduler user delete

cloudscheduler group add
cloudscheduler group list
cloudscheduler group update
cloudscheduler group delete
```

These commands help administrators manage access, resource ownership, and default settings across a Cloud Scheduler environment.

## 9. Jobs and metadata

Cloud Scheduler also includes job-oriented commands and metadata handling. These allow administrators to:

- inspect active jobs
- list job status
- update job fields
- attach or modify metadata values

```bash
cloudscheduler job list
cloudscheduler metadata list
cloudscheduler metadata load
cloudscheduler metadata update
```

This is useful for keeping job definitions, cloud metadata, and group defaults aligned with operational requirements.

## 10. Data collectors and service deployment

The repository contains directories for data collection services, including Condor and OpenStack pollers. These services collect job and machine data and ship it to a central Redis server.

The `data_collectors/README.md` documents the expected deployment model:

- create a dedicated `cloudscheduler` system user
- install the relevant service units under `/etc/systemd/system/`
- place YAML configuration files in `/etc/`
- create log files under `/var/log/cloudscheduler`
- reload and start the services with `systemctl`

Example service startup:

```bash
sudo systemctl daemon-reload
sudo systemctl start csjobs
sudo systemctl start cscollector
sudo systemctl start csmetadata
```

## 11. Running tests

The repository contains a dedicated test framework under `unit_tests/`.

Typical usage:

```bash
cd unit_tests
./run_tests
./run_tests user
./run_tests db
```

The test README describes how to initialize a test environment, set default test servers, and execute targeted validation checks.

## 12. Documentation structure

The project includes a Sphinx-based documentation tree under `docs/source/` and a generated user guide layout with the following main sections:

- Getting Started
- User Guide
- Utilities
- Architecture

The command-specific reference pages in `docs/source/_user_guide/_cli/` cover every CLI command in detail and are the most comprehensive source of operational guidance.

## 13. Troubleshooting and support

If a problem occurs:

- confirm Python 3 is installed correctly
- verify CLI defaults and server configuration
- ensure the necessary services are running
- check Redis, systemd, and Condor/OpenStack collector logs
- consult the `cli/man` references for exact command syntax and valid parameters

Useful log locations include:

- `/var/log/cloudscheduler/`
- service-specific systemd journal output
- the repository's doc sources under `docs/source/`

## 14. Summary

Cloud Scheduler is a flexible cloud resource manager built around a Python 3 CLI. It supports cloud, VM, group, user, and job operations, with additional data collectors for machine and job telemetry. The best starting points for new users are the README, the Sphinx documentation, and the CLI reference pages in `docs/source/_user_guide/_cli/`.

This documentation is intended as a practical overview for day-to-day administration and operations.
