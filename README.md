# DayZ Server Manager (DZSM)

A basic utility for managing one or more DayZ servers, including managment of startup, restart, and configurations.

## Quick Start

### Prerequisites
- Python 3.10 or higher

Install the utility by downloading the wheel (.whl) file from the Github releases section. Once downloaded, run the command:

`# pip install <path_to_wheel_file>`

The server manager can then be started by running `dzsm`

## Configuration Format

The primary configuration for DZSM defaults to a file called `config.yaml`. This file has 3 primary sections:
- `app_config` - This section is used for configuring the behavior of the server manager itself, for example controlling how often it does health-checks on servers.
- `shared` - This section defines default values for server configuration that are shared across all servers. Individual server settings will take precedence over shared settings.
- `servers` - This section defines configuration values for each server instance that is being managed.

### `app_config`

| Setting | Default | Description |
|---------|---------|-------------|
| `startup_delay` | 60 | Defines the backoff time between server startup actions (in seconds). If servers start too quickly, it can cause problems with the Steam API|
| `update_interval` | 30 | Defines the time between health-check cycles (in seconds) |

### `shared` / `servers`

| Setting | Default | Required | Description |
|---------|---------|----------|-------------|
| `server_name` | None | Yes | The internal name for this server instance. Used in logging and system menus|
| `name` | None | Yes | The name that should be shown for this server instance in the server browser |
| `port` | None | Yes | Port to be used for this server instance |
| `base_path` | None | Yes | Full path to the DayZ Server data folder |
| `config_file` | None | Yes | Relative or full path to the server configuration file |
| `executable` | None | Yes | Relative or full path to the DayZ server executable |
| `restart_time` | None | Yes | Time interval (in minutes) for automatic server restarts |
| `profiles` | None | Yes | Relative or full path to the mission directory |
| `extra_args` | None | No | Additional command line arguments to pass to the server executable |
| `mods` | None | No | List of mods to load for the server. Mod names should not include the starting @ or ; at end |
| `server_mods` | None | No | List of server-side mods to load. Mod names should not include the starting @ or ; at end |
| `cpu` | 2 | No | Number of CPU cores to allocate to the server |
