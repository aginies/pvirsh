# Goal

EXPERIMENTATION FOR [ALP OS](https://documentation.suse.com/alp/all/)

Being able to execute the same **command** on an **group of Virtual Machine**.
If you want to manage more than 1 VM you need to script you actioni and this will
be done in a sequential way (most of the time). This wrapper is a **parralel virsh**
command.

This tool provides:
* Selection of group of VM, possibility to use multi-group (yaml file)
* Possibility to select a different group yaml file (default is groups.yaml)
* Show the list of VM per group
* Launch parralel command on mulitiple VM selected by group
* auto-completion of the **virsh** domain command
* Help on **virsh** command (display options)
* Reports error/success per VM
* Interactive terminal or one shot command
* use libvirt api to connect to host (local by default)
* In Interactive mode: the prompt display which group you are currently managing
* Can execute a system command without leaving the interactive mode (exec)
* Can display the list of VM selected

# Demo

![image](https://github.com/aginies/pvirsh/blob/d1c9d87d61b749a060ea7ea77ea7780c7bc88785/demo_pvirsh.gif)

# Python requires

* libvirt
* yaml

# TODO

Probably a lot as this is for testing purpose...
* detect VM state before (useful for some command which requires VM running)
* validate the yaml file before using it
* connect to multiple host?
* use libvirt api directly for the command? -> need some rewrite...
* ....

# Define Virtual Machine groups

By default the script will use **groups.yaml** in the same path.
The **yaml** file looks like:

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

* sle15sp31$ : will match exactly this machine name
* sle15sp4 : will match all VM, including sle15sp4*

# Usage

```bash
Usage:

        Interactive or Non Interactive command tool to manage multiple VM at the same Time

        Non interactive:
        pvirsh.py -n  -f GROUP.yaml -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        example:
        pvirsh.py -n -g suse -c 'domstate --reason'
        

Options:
  -h, --help            show this help message and exit
  -n, --noninteractive  Launch this tool in non interactive mode)
  -g GROUP, --group=GROUP
                        Group of VM to use (could be a list separated by ,)
  -f FILE, --file=FILE  Group file to use as yaml file (default will be
                        groups.yaml)
  -c CMD, --cmd=CMD     Command to execute on a group of VM
  -s, --showgroup       Show group from VM file content
  -v, --virsh           Show all virsh domain commands available
  -d CMDDOC, --cmddoc=CMDDOC
                        Show the virsh CMD documentation
```

# Examples

Get the state of all virtual Machine in **suse** group:

```bash
./pvirsh.py -n -g suse,rhel -c domstate

Multiple group selected
Selected group is suse: ['sle15sp31$', 'sle15sp4']
Selected group is rhel: ['rhe', 'fedora', 'plop']
fedora Virtual Machine Not found
plop Virtual Machine Not found
virsh domstate sle15sp42  shut off Done
virsh domstate sle15sp4  shut off Done
virsh domstate sle15sp31  shut off Done
virsh domstate sle15sp41  shut off Done
virsh domstate sle15sp4-2  shut off Done
virsh domstate rhel8  shut off Done
virsh domstate sle15sp44  shut off Done
virsh domstate sle15sp43  shut off Done
```

Setting hard-limit memory to 1.024GB for all VM in **suse** group:

```bash
./pvirsh.py -n -g suse -c "memtune --hard-limit 1000000"

Selected group is suse: ['sle15sp31$', 'sle15sp4']
virsh memtune sle15sp31 --hard-limit 1000000  Done
virsh memtune sle15sp41 --hard-limit 1000000  Done
virsh memtune sle15sp44 --hard-limit 1000000  Done
virsh memtune sle15sp4-2 --hard-limit 1000000  Done
virsh memtune sle15sp42 --hard-limit 1000000  Done
virsh memtune sle15sp4 --hard-limit 1000000  Done
virsh memtune sle15sp43 --hard-limit 1000000  Done
```

Adding an RNG device to all VM in **suse** group:
```bash
cat rng.xml 
<rng model="virtio">
  <backend model="random">/dev/urandom</backend>
  <address type="pci" domain="0x0000" bus="0x0a" slot="0x00" function="0x0"/>
</rng>

./pvirsh.py -n -g suse -c "attach-device --current --file rng.xml"

Selected group is suse: ['sle15sp31$', 'sle15sp4']
virsh attach-device sle15sp4-2 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp31 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp4 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp41 --current --file rng.xml Device attached successfully Done
Command was:virsh attach-device sle15sp44 --current --file rng.xml
ERROR: sle15sp44: b'error: Failed to attach device from rng.xml\nerror: unsupported configuration: a device with the same address already exists \n'

virsh attach-device sle15sp42 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp43 --current --file rng.xml Device attached successfully Done
```
