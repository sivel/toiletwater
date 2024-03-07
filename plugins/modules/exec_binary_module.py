# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
  module: exec_binary_module
  short_description: A proxy action, to execute binary modules
  description:
      - This action is used to execute binary modules by a root name
        with auto discovery of the system type and architecture
  options:
    module:
      required: false
      type: str
      description:
        - The module to execute, this is only required when calling
          this module by it's name of M(sivel.toiletwater.exec_binary_module)
    arch:
      required: false
      type: str
      default: auto
      description:
        - Explicitly set an architecture to use when calling a binary module
    system:
      required: false
      type: str
      default: auto
      description:
        - Explicitly set a system to use when calling a binary module
  requirements: []
  notes:
    - This module will not generally be called directly, but will be
      configured in a collection as the C(action_plugin) for a specific
      module name, see the C(README.md) for more details.
    - Any argument accepted by the actual module being called is proxied
      by this action can be specified in addition to the documented options
      of this module.
    - The binary modules that this action proxies to must be named like
      C({root}_{system}_{arch}). An example would look like
      C(helloworld_linux_amd64).
    - The general implementation of arch follows that of C(GOOS) defined
      in Golang.
  author: 'Matt Martz (@sivel)'
'''

EXAMPLES = r'''
  # Usually you aren't calling this module directly
  - name: Call the helloworld module
    sivel.toiletwater.helloworld:
      name: sivel

  # Just some examples of calling this directly
  - name: Simple call
    sivel.toiletwater.exec_binary_module:
      module: sivel.toiletwater.helloworld
      name: sivel

  - name: Explicit system and arch
    sivel.toiletwater.exec_binary_module:
      module: sivel.toiletwater.helloworld
      system: linux
      arch: amd64
      name: sivel
'''

RETURN = r'''
  _architecture:
    type: str
    description: The discovered or explicitly passed architecture
    returned: always
  _system:
    type: str
    description: The discovered or explicitly passed system
    returned: always
  _module:
    type: str
    description: The formatted module name including the root, system, and
                 architecture
    returned: always
'''
