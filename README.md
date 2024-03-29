# Goal

EXPERIMENTATION FOR [ALP OS](https://documentation.suse.com/alp/all/)

This wrapper is a **parallel virsh** command to manage a selected group of Virtual Machine.
This provides an easy way to execute the same **command** on a **selected group of Virtual Machine**.
If you want to manage more than 1 VM you need to script you action and this will
be done in a sequential way (most of the time). 

Features:
* Launch **parallel command** on mulitiple **VM** selected by group
* **auto-completion** of the **virsh** domain command
* **Reports** of **error/success** per VM
* Interactive mode with intelligent prompt (display group, yaml file and connector)
* **Interactive terminal** or a one shot command
* **colored prompt** to easily catch up trouble and syntax
* yaml file group: default is **groups.yaml**, possible to change to any other file

Interactive command:

See the **pvirsh.pod** file in **man/** directory

# Demo

![image](https://github.com/aginies/pvirsh/blob/1fe39679fbeac2e9f02a99bdfc50efa98a2ca6df/demo_pvirsh.gif)

# Python requires

* python3-libvirt-python
* python3-PyYAML
* python3-curses (to get completion)

# Install

* From source code:
```bash
git clone https://github.com/aginies/pvirsh
cd pvirsh
./setup.py install
```

* Package from [OBS](https://build.opensuse.org/package/show/home:aginies/pvirsh)

# Define Virtual Machine groups

It is possible to select VM directly on the connected hypervisir with **select_vm**,
or you can use a group yaml file which contains list of VM per group.
By default the script will use **groups.yaml**.
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

NOTE: select_vm is only available in interactive mode.

# TODO

Probably a lot as this is for testing purpose...
* detect VM state before (useful for some command which requires VM running)
* connect to multiple host?
* ....

# Usage

```bash
usage: Interactive or Non Interactive command tool to manage multiple VM at the same Time

        Non interactive:
        pvirsh -n -f GROUP.yaml --conn CONNECTOR -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        Example:
        pvirsh -n --conn local -g suse -c 'domstate --reason'
        
       [-h] [-s] [--conn CONN] [-g GROUP] [-f FILE] [-n] [-c CMD]

optional arguments:
  -h, --help            show this help message and exit

help:
  -s, --showgroup       Show group from VM file content

config:
  --conn CONN           Connect to the hypervisor (local | ssh)
  -g GROUP, --group GROUP
                        Group of VM to use (could be a list separated by ,)
  -f FILE, --file FILE  Group file to use as yaml file

exec:
  -n, --noninter        Launch this tool in non interactive mode
  -c CMD, --cmd CMD     Command to execute on a group of VM
```

# Examples

Get the state of all virtual Machine in **suse** group:

```bash
pvirsh.py -n --conn local -c domstate -g suse,rhel


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
pvirsh.py -n --conn local -c "memtune --hard-limit 1000000" -g suse


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

pvirsh.py -n --conn local -g suse,rhel -c "attach-device --current --file rng.xml"

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
