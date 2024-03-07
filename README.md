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
* `passlib_hash` - Hash passwords using `passlib`

### Modules

#### utilities

* `exec_binary_module` - A proxy action, to execute binary modules

#### net_tools

* `speedtest` - Tests internet bandwidth using speedtest.net

#### system

* `cert_locations` - Report CA cert locations used by Ansible

#### files

* `substring` - Search for substring in file

### Callback

* `dump_stats` - Callback to dump to stats from `set_stat` to a JSON file
* `cprofile` - Uses `cProfile` to profile the python execution of ansible

### Inventory

* `cprofile` - Noop inventory plugin used to enable cProfile as early as possible

## exec_binary_module

Generally speaking, most users should not even know they are interacting with `exec_binary_module`, but instead should be using the name of an underlying binary module implementation.

To achieve this, requires a small addition to a collections `meta/runtime.yml`:

```yaml
  plugin_routing:
    modules:
      helloworld:
        action_plugin: sivel.toiletwater.exec_binary_module
      another_module:
        action_plugin: sivel.toiletwater.exec_binary_module
```

At which point, with modules named something like `helloworld_linux_amd64` a user would only have to do the following:

```yaml
- namespace.name.helloworld:
    name: sivel

- namespace.name.another_module:
    some_argument: true
```
