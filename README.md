# toiletwater
You might be able to drink it in an emergency, but you might still die

This repo is an Ansible collection containing some of my own Ansible plugins that died in the PR phase, and have instead been moved to this festering repository.

## Plugins

### Filter

* `to_ini` - Convert hash/map/dict to INI format
* `from_ini` - Convert INI to hash/map/dict
* `to_toml` - Convert hash/map/dict to TOML format
* `from_toml` - Convert TOML to hash/map/dict

### Modules

#### net_tools

* `speedtest` - Tests internet bandwidth using speedtest.net

#### Packaging

* `go` - Manage Golang packages
