# Goal

Being able to execute the same command on an group of Virtual Machine.
If you want to destroy more than 5 VM this is really annoying with current tool.
What about adding/removing the same device to 10 VM?

# TODO

A lot... this is experimental:
* use libvirt api directly instead of virsh
* detect VM state before doing anything
* collect error in a better way
* validate the yaml file before using it
* etc....

# Define Virtual Machine group

This should be done in a **yaml** file like:

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

By default the script will use **groups.yaml** in the same path.
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

Get the state of all virtual Machine in **suse** group:

```bash
./pvirsh.py -g suse -c domstate

Selected group is suse: ['sle15sp31$', 'sle15sp4']
Will launch: "virsh domstate VirtualMachineName "

virsh domstate sle15sp4  shut off Done
virsh domstate sle15sp4-2  shut off Done
virsh domstate sle15sp41  shut off Done
virsh domstate sle15sp42  shut off Done
virsh domstate sle15sp43  shut off Done
virsh domstate sle15sp44  shut off Done
virsh domstate sle15sp31  shut off Done
```

Setting hard-limit memory to 1.024GB for all VM:

```bash
./pvirsh.py -g suse -c memtune -o "--hard-limit 1000000"

Selected group is suse: ['sle15sp31$', 'sle15sp4']
Will launch: "virsh memtune VirtualMachineName --hard-limit 1000000"

virsh memtune sle15sp4 --hard-limit 1000000  Done
virsh memtune sle15sp4-2 --hard-limit 1000000  Done
virsh memtune sle15sp41 --hard-limit 1000000  Done
virsh memtune sle15sp42 --hard-limit 1000000  Done
virsh memtune sle15sp43 --hard-limit 1000000  Done
virsh memtune sle15sp44 --hard-limit 1000000  Done
virsh memtune sle15sp31 --hard-limit 1000000  Done
```
