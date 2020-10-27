# sivel.toiletwater

You might be able to drink it in an emergency, but you might still die.

<p align="center"><img width="297" height="380" src="https://i.imgur.com/LCYeNRx.png"></p>

This repo is an Ansible collection containing some of my own Ansible plugins that died in the PR phase, and have instead been moved to this festering repository.

## Plugins

### Filter

* `to_ini` - Convert hash/map/dict to INI format
* `from_ini` - Convert INI to hash/map/dict
* `to_toml` - Convert hash/map/dict to TOML format
* `from_toml` - Convert TOML to hash/map/dict
* `jq` - Parse JSON using `jq`

### Modules

#### net_tools

* `speedtest` - Tests internet bandwidth using speedtest.net

#### packaging

* `go` - Manage Golang packages

#### system

* `cert_locations` - Report CA cert locations used by Ansible

### Callback

* `dump_stats` - Callback to dump to stats from `set_stat` to a JSON file
* `cprofile` - Uses `cProfile` to profile the python execution of ansible
