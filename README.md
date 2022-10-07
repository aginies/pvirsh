# Goal

Being able to execute the same command on a pool of guest.
If you want to destroy more than 5 VM this is really annoying with current tool.
What about adding/removing the same device to 10 VM?

# TODO

A lot... this is experimental:
* use libvirt api directly instead of virsh
* detect VM state before doing anything
* collect error in a better way
* etc....

# Define Virtual Machine group

This should be done in a yaml file like:

```yaml
suse:
  - sle15sp31$
  - sle15sp4

rhel:
  - rhe
  - fedora

windows:
  - win7
  - win10
```

By default the script will use '''groups.yaml''' in the same path.
* sle15sp31$ : will match exactly this machine name
* sle15sp4 : will match all VM, including sle15sp4*

# Usage

```bash
Usage: pvirsh.py -h 

Options:
  -h, --help            show this help message and exit
  -g GROUP, --group=GROUP
                        Group of VM to use
  -f FILE, --file=FILE  Group file to use as yaml file (default will be
                        groups.yaml)
  -c CMD, --cmd=CMD     Command to execute on a group of VM
  -o CMDOPTIONS, --options=CMDOPTIONS
                        Option to the command to execute
  -s, --showgroup       Show group of VM file content
  -v, --virsh           Show all virsh domain commands available
  -d CMDDOC, --cmddoc=CMDDOC
                        Show the virsh CMD documentation
```

# Example

Get the state of all virtual Machine in '''suse''' group:

```bash
./pvirsh.py -g suse -c domstate

Selected group is suse: ['sle15sp31$', 'sle15sp4']
Number of processors:  12
Will launch: "virsh domstate VM "

virsh domstate sle15sp4 
sle15sp4: shut off

virsh domstate sle15sp4-2 
sle15sp4-2: shut off

virsh domstate sle15sp41 
sle15sp41: shut off

virsh domstate sle15sp42 
sle15sp42: shut off

virsh domstate sle15sp43 
sle15sp43: shut off

virsh domstate sle15sp44 
sle15sp44: shut off

virsh domstate sle15sp31 
sle15sp31: shut off
```
