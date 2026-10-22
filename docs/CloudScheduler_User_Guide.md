# Cloud Scheduler User Guide

This guide reflects the behavior implemented in the actual source code, not the repository README summaries. It documents how the project is used in practice from the command-line client and the Django-based web frontend.

## 1. What Cloud Scheduler is in this repository

The repository contains a server-backed cloud orchestration system with two primary user interfaces:

- a CLI client at `cli/bin/cloudscheduler`
- a Django web front-end under `web_frontend/cloudscheduler/`

The CLI is the main control path for administrators and users. Most real operations are performed by sending REST-style requests to a Cloud Scheduler server. The browser UI mirrors the same underlying functionality through Django views.

At the implementation level, Cloud Scheduler is not a local-only script. It is a client-server system where the code in this repository:

- defines and dispatches commands
- stores local defaults and credentials
- authenticates to a target server
- sends requests to server-side endpoints
- renders results as terminal tables or HTML pages

## 2. Command-line interface: actual syntax

The real entrypoint is `cli/bin/cloudscheduler`.

Actual CLI syntax:

```bash
cloudscheduler <object> <action> [options]
```

Examples:

```bash
cloudscheduler cloud list
cloudscheduler group list
cloudscheduler user list
cloudscheduler vm list
cloudscheduler job list
cloudscheduler server config
cloudscheduler my settings
cloudscheduler defaults set -s prod
```

The CLI parses arguments into a global command map, then looks up the handler for the requested object and action.

## 3. Actual object and action map

The command table in the CLI is defined in `cli/bin/cloudscheduler`. The implemented top-level objects are:

- `accounting`
- `alias`
- `cloud`
- `defaults`
- `ec2`
- `group`
- `helpers`
- `job`
- `metadata`
- `my`
- `server`
- `user`
- `vm`
- `image`

The current implemented actions are:

### `defaults`

- `list`
- `set`
- `delete`

This is the local profile manager for named Cloud Scheduler servers.

### `my`

- `settings`

This updates a user's settings and defaults on the server, and may modify the local saved defaults if the current user is changing their own password.

### `server`

- `config`

This retrieves and updates server configuration values.

### `user`

- `add`
- `delete`
- `list`
- `update`

These are the user management actions used by privileged users.

### `group`

- `add`
- `defaults`
- `delete`
- `list`
- `update`
- `metadata-add`
- `metadata-delete`
- `metadata-fetch`
- `metadata-list`
- `metadata-new`
- `metadata-query`
- `metadata-update`

This is the main group object for permissions, group metadata, and defaults.

### `cloud`

- `add`
- `delete`
- `list`
- `status`
- `update`
- `metadata-add`
- `metadata-collation`
- `metadata-delete`
- `metadata-fetch`
- `metadata-list`
- `metadata-new`
- `metadata-query`
- `metadata-update`

This is the main object for defining and managing clouds.

### `vm`

- `list`
- `update`
- additional VM detail and settings pages exist in the web frontend

### `job`

- `list`

Job support is present in the CLI but currently limited to listing jobs.

### `metadata`

- `backup`
- `delete`
- `edit`
- `group-defaults`
- `list`
- `load`
- `restore`
- `update`

This is the metadata-management object used for both user and group configuration.

### `alias`

- `add`
- `list`
- `update`
- `delete`

### `ec2`

- `images`
- `instance-types`

### `helpers`

- `check_documentation`
- `generate_bash_completion_script`
- `print_json_syntax_tree`

### `image`

- `transfer`
- `upload`
- `delete`
- `list`

### `accounting`

- `apel`

## 4. How the CLI stores local configuration

The CLI stores local state under:

```bash
~/.csv2/
```

This directory contains:

- `default_server`
- `/<server>/settings.yaml`

Example structure:

```bash
~/.csv2/
├── default_server
├── prod/
│   └── settings.yaml
├── dev/
│   └── settings.yaml
```

The code loads saved settings from `~/.csv2/<server>/settings.yaml`, overlays command-line arguments, and then sends the request to the server.

The local server defaults include things like:

- server URL
- server username
- server password
- preferred group
- authentication flags

## 5. Authentication model

The CLI supports two ways to authenticate to the server:

1. username and password
2. x509 certificate-based proxy authentication

Relevant CLI options:

```bash
-su, --server-user
-spw, --server-password
-sa, --server-address
-x509, --use-x509-authentication
```

The request code in `cli/bin/csv2_common.py` checks for both. If no credentials are configured, it triggers an interactive prompt to collect a server URL and credentials, and optionally saves them as a named profile.

This is the actual behavior implemented in the code. The CLI is designed around a server endpoint and credentials, not a standalone local-only mode.

## 6. How requests are sent

The shared helper `requests()` in `cli/bin/csv2_common.py` does the actual communication.

It:

- prepares a CSRF token if needed
- chooses the proper HTTP method (`GET` or `POST`)
- adds the current group context
- appends `csrfmiddlewaretoken` to state-changing requests
- sends the request to the configured server URL
- parses the JSON response
- exits on `response_code != 0`

The general pattern is:

```python
response = requests(gvar, '/some/server/path/', form_data)
```

All server interactions use the same pattern. This is why the CLI behaves like a thin client to the server.

## 7. Typical CLI usage

### 1. Set up a named server default

```bash
cloudscheduler defaults set -s prod
```

Then provide the actual connection values:

```bash
cloudscheduler defaults set -s prod -sa https://server.example -su myuser -spw mypassword
```

### 2. Make the server the default

The first configured server can be saved as the default. The CLI also supports switching the current default via the server profile.

### 3. Set a default group for your user

```bash
cloudscheduler my settings -gn mygroup
```

### 4. List clouds

```bash
cloudscheduler cloud list
```

### 5. List groups

```bash
cloudscheduler group list
```

### 6. List users

```bash
cloudscheduler user list
```

### 7. List VMs

```bash
cloudscheduler vm list
```

### 8. List jobs

```bash
cloudscheduler job list
```

### 9. Inspect server configuration

```bash
cloudscheduler server config
```

### 10. Show available help

```bash
cloudscheduler --help
cloudscheduler cloud --help
cloudscheduler cloud list -h
cloudscheduler cloud list -H
```

The code distinguishes between:

- `-h`: short help
- `-H`: long help, using the `man` pages under `cli/man/`

## 8. Global options used by the real CLI

The CLI recognizes options such as:

- `-s`, `--server`
- `-sa`, `--server-address`
- `-su`, `--server-user`
- `-spw`, `--server-password`
- `-g`, `--group`
- `-gn`, `--group-name`
- `-v`, `--version`
- `-h`, `--help`
- `-H`, `--long-help`
- `-Y`, `--yes`
- `-x509`, `--use-x509-authentication`
- `-xA`, `--expose-API`
- `-CSV`, `--comma-separated-values`
- `-VC`, `--view-columns`

The app is designed to let users print table output, filter columns, and request verbose API tracing when needed.

## 9. Browser/web usage

The web interface is implemented as a Django project under:

```text
web_frontend/cloudscheduler/
```

The top-level Django URLs are configured in:

```text
web_frontend/cloudscheduler/cloudscheduler_web/urls.py
```

This file includes the `csv2` app routes:

```python
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('csv2.urls')),
    re_path(r'^images/', include('glintwebui.image_urls')),
    re_path(r'^keypairs/', include('glintwebui.keypair_urls')),
]
```

The actual web routes are declared in:

```text
web_frontend/cloudscheduler/csv2/urls.py
```

Those routes include pages such as:

- `/`
- `/cloud/status/`
- `/cloud/list/`
- `/cloud/add/`
- `/cloud/update/`
- `/group/list/`
- `/group/add/`
- `/group/update/`
- `/group/defaults/`
- `/vm/list/`
- `/vm/update/`
- `/vm/machines/`
- `/vm/error/`
- `/user/list/`
- `/user/add/`
- `/user/update/`
- `/user/settings/`
- `/job/list/`
- `/server/config/`
- `/settings/prepare/`
- `/settings/log-out/`

These routes are the web equivalents of the CLI objects and actions.

## 10. What the web app actually does

The browser app is not a separate backend implementation. It is a Django presentation layer over the same Cloud Scheduler concepts.

The relevant code shows that the web views:

- open a database config connection
- resolve the active user and user groups
- use the same active-group concept as the CLI
- render HTML templates for cloud, VM, user, and group data
- require CSRF for state-changing requests

The `prepare` endpoint in `settings_views.py` is especially important:

```python
response = {
    'active_user': active_user.username,
    'active_group': active_user.active_group,
    'super_user': active_user.is_superuser,
    'user_groups': active_user.user_groups,
    'version': config.get_version(),
}
```

That confirms the browser UI is built around the same identity and active-group model as the CLI.

## 11. Browser workflow

A normal browser workflow is:

1. Open the Django app in a browser.
2. Log in or authenticate to the Cloud Scheduler server through the web app.
3. The app loads the active user and group context from the server.
4. Use pages like cloud status, group list, VM list, and user settings.
5. Submit changes by posting forms to server-backed Django views.

This is a direct web face on the same server-backed state as the command-line tool.

## 12. Relationship between CLI and web usage

The CLI and browser are parallel interfaces to the same system.

The key idea is:

- CLI commands are built around `cloudscheduler <object> <action>`
- web routes are built around `/object/action/`
- both share the same underlying server metadata model
- both use active user and active group context
- both ultimately talk to the same server state and configuration

In other words, the browser UI is not a separate product; it is a Django front-end for the same scheduler functions.

## 13. Practical workflow for real use

A realistic usage flow is:

```bash
cloudscheduler defaults set -s prod -sa https://server.example -su myuser -spw mypassword
cloudscheduler my settings -gn mygroup
cloudscheduler cloud list
cloudscheduler group list
cloudscheduler vm list
cloudscheduler server config
```

Or in the browser:

```text
https://server.example/
```

Then navigate to:

- cloud status
- cloud list
- group list
- VM list
- user settings
- server config

## 14. Limitations and realities from the code

The implementation in this repository shows that the system is broad but not uniformly polished.

Notable realities:

- the CLI is the most complete, explicit, and well-structured interface
- the browser app is present and routes are clearly defined, but it is a Django app layered over the same backend
- some job operations are partially implemented or limited
- some actions are privileged and blocked by client-side authorization checks
- local settings are stored in the user home directory under `~/.csv2`

## 15. Summary

Cloud Scheduler in this repository is a server-backed cloud management system with two UIs:

- a Python CLI at `cli/bin/cloudscheduler`
- a Django web application under `web_frontend/cloudscheduler/`

Both interfaces operate on the same model:

- named servers and credentials
- active user and active group
- group-scoped cloud, VM, and job management
- metadata and configuration objects
- server-backed REST-style requests for operational actions

The CLI is the clearest interface for real use, while the web interface is the corresponding browser layer over the same underlying system.
