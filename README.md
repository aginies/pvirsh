# Goal

EXPERIMENTATION FOR [ALP OS](https://documentation.suse.com/alp/all/)

Being able to execute the same **command** on an **group of Virtual Machine**.
If you want to manage more than 1 VM you need to script you action and this will
be done in a sequential way (most of the time). 
This wrapper is a **parralel virsh** command.

This tool provides:
* Launch parralel command on mulitiple VM selected by group
* Auto-completion of the **virsh** domain command
* Help on **virsh** command (display options)
* Reports of error/success per VM
* An interactive terminal or a one shot command
* Interactive mode: the prompt display which group you are currently managing and the connector
* Execution of a system command in interactive mode (exec)
* group of VM: selection, show selected group(s), possibility to use multi-group
* yaml file group: default is groups.yaml, option to change to any other file
* Displaying the list of VM selected according to the current group(s)
* Displaying the "regexp" per group to select VM

# Demo

![image](https://github.com/aginies/pvirsh/blob/5873dbd6c597cd41552a8d79607d2f4aea0daed7/demo_pvirsh.gif)

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
  -n, --noninteractive  Launch this tool in non interactive mode
  --conn=CONN           Connect to the hypervisor (local | ssh)
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
/pvirsh.py -n --conn local -c domstate -g suse,rhel


Connected; Version: 6002000
Multiple group selected
Selected group is suse: ['sle15sp3', 'sle15sp41$', 'sle15sp4-2$']
Selected group is rhel: ['rhe', 'fedora', 'plop']
virsh domstate sle15sp31  shut off Done
virsh domstate sle15sp41  shut off Done
virsh domstate sle15sp4-2  shut off Done
virsh domstate sle15sp32  shut off Done
virsh domstate sle15sp33  shut off Done
virsh domstate sle15sp34  shut off Done
virsh domstate rhel8  shut off Done
```

Setting hard-limit memory to 1.024GB for all VM in **suse** group:

```bash
./pvirsh.py -n --conn local -c "memtune --hard-limit 1000000" -g suse


Connected; Version: 6002000
Selected group is suse: ['sle15sp3', 'sle15sp41$', 'sle15sp4-2$']
virsh memtune sle15sp34 --hard-limit 1000000  Done
virsh memtune sle15sp41 --hard-limit 1000000  Done
virsh memtune sle15sp31 --hard-limit 1000000  Done
virsh memtune sle15sp33 --hard-limit 1000000  Done
virsh memtune sle15sp32 --hard-limit 1000000  Done
virsh memtune sle15sp4-2 --hard-limit 1000000  Done
```

Adding an RNG device to all VM in **suse** group:
```bash
cat rng.xml 
<rng model="virtio">
  <backend model="random">/dev/urandom</backend>
  <address type="pci" domain="0x0000" bus="0x0a" slot="0x00" function="0x0"/>
</rng>

./pvirsh.py -n --conn local -g suse,rhel -c "attach-device --current --file rng.xml"

Connected; Version: 6002000
Multiple group selected
Selected group is suse: ['sle15sp3', 'sle15sp41$', 'sle15sp4-2$']
Selected group is rhel: ['rhe', 'fedora', 'plop']
virsh attach-device sle15sp41 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp31 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp4-2 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp33 --current --file rng.xml Device attached successfully Done
virsh attach-device rhel8 --current --file rng.xml Device attached successfully Done
virsh attach-device sle15sp32 --current --file rng.xml Device attached successfully Done
Command was:virsh attach-device sle15sp34 --current --file rng.xml
ERROR: sle15sp34: b'error: Failed to attach device from rng.xml\nerror: unsupported configuration: a device with the same address already exists \n'
```
