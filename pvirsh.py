#!/usr/bin/env python3
# aginies@suse.com
#
# EXPERIMENTAL
# draft of a scalable VM management tool for a group of VM
#
# Goal at the end is being able to
# - execute command
# - add / remov devices
# - ???

import yaml
import subprocess
import multiprocessing as mp
from pathlib import Path
import optparse

# TODO: validate the yaml file
def validate_file():
    print('todo')

def esc(code):
    """ Better layout with some color"""

    return f'\033[{code}m'

def show_file_example():
    """ Show an example of a groups.yaml file"""

    example = """
--------------------
suse:
  - sle15sp31$
  - sle15sp4
rhel:
  - rhe
  - fedora
--------------------

Information/tips:
- use NAME$ to match exact NAME (add $ at the end)
- NAME will match everything starting with NAME* 
  ie: NAMEguibo,NAME,NAME15SP4"""
    print('Example of a group yaml file:')
    print(example)

def check_group(groupfile,group):
    """check that the group exist in the yaml file"""

    with open(groupfile) as file:
        groups = yaml.full_load(file)
        keys = list(groups.keys())
        found = False
        # going through the list to find the group
        for key in keys:
            if (key == group):
                found = True

        if found:
            pass
        else:
            print(group+ 'Not found!')
            exit(1)

def show_group(groupfile):
    """show all group and machines"""

    my_file = Path(groupfile)
    if my_file.is_file():
        print('File: ' +groupfile)
    else:
        print('File ' +groupfile + ' Doesnt exist!\n')
        show_file_example()
        exit(1)
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        keys = list(groups.keys())
        print('Available groups are:')
        for item, value in groups.items():
            print('Group ' +str(item) + ': '  +str(value))
        print('\n')

def system_command(cmd):
    """ Launch a system command  """

    #print(cmd)
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rc = proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'utf-8')
    return out, errs

def find_matching_vm(groupfile,group):
    """return the list of VM matching the group"""

    with open(groupfile) as file:
        groups = yaml.full_load(file)
        # all group store in keys
        keys = list(groups.keys())
        vms = ""
        for item, value in groups.items():
            # only match vm of the correct group
            if (item == group):
                print ('Selected group is ' +item + ': ' + str(value))
                for vm in value:
                    # matching vm in virsh list, must start exactly with the name
                    # if no $ at the end it will wilcard anything
                    cmd = 'virsh list --all --name| grep "^' +str(vm) +'"'
                    out, errs = system_command(cmd)
                    if errs:
                        print(errs)
                    vms = out + vms
            else:
                # not correct group
                pass

        return vms


def do_virsh_cmd(vm,cmd,cmdoptions):
    """execute the command on all the VM defined"""

    cmdtolaunch = cmd + ' ' + vm + ' ' + cmdoptions
    out, errs = system_command(cmdtolaunch)
    out = out.strip("\n")
    if errs:
        print('Command was:' +str(cmdtolaunch))
        print(esc('31;1;4') + 'ERROR: ' +str(vm)+ ': ' +str(errs)+ esc(0) + '\n')
    else:
        print(cmdtolaunch, end= " ")
        print(out + " " + esc('32;1;4') + 'Done' + esc(0))

def para_cmd(file,group,cmd):
    """Start pool of command"""

    results = []
    vms = find_matching_vm(file,group)
    # splitlines because of \n
    vms = str(vms).splitlines()
    #print("Number of processors: ", mp.cpu_count())
    # check if there is an option
    if ' ' in cmd:
        cmd, cmdoptions = cmd.split(" ", 1)
    else:
        cmdoptions = ''
    #tolaunch = 'virsh ' +str(precmd) + ' VirtualMachineName ' +str(cmdoptions)
    #print('Will launch: ' +tolaunch +'\n')
    cmd = 'virsh ' +cmd
    pool = mp.Pool(mp.cpu_count())
    for vm in vms:
        pool.apply_async(do_virsh_cmd, args = (vm, cmd, cmdoptions))
    pool.close()
    pool.join()
    print(results) #[:10])

# list of domain command available with virsh
# remove some: create, console
listdomaincmd = [ 'attach-device','attach-disk','attach-interface',
                   'autostart','blkdeviotune','blkiotune','blockcommit',
                   'blockcopy','blockjob','blockpull','blockresize',
                   'change-media','cpu-stats','define','domstate',
                   'desc','destroy','detach-device','detach-device-alias',
                   'detach-disk','detach-interface','domdisplay','domfsfreeze',
                   'domfsthaw','domfsinfo','domfstrim','domhostname','domid',
                   'domif-setlink','domiftune','domjobabort','domjobinfo',
                   'domlaunchsecinfo','domsetlaunchsecstate','domname',
                   'domrename','dompmsuspend','dompmwakeup','domuuid',
                   'domxml-from-native','domxml-to-native','dump','dumpxml',
                   'event','get-user-sshkeys','inject-nmi','iothreadinfo',
                   'iothreadpin','iothreadadd','iothreadset','iothreaddel',
                   'send-key','send-process-signal','lxc-enter-namespace',
                   'managedsave','managedsave-remove','managedsave-edit',
                   'managedsave-dumpxml','managedsave-define','memtune',
                   'perf','metadata','migrate','migrate-setmaxdowntime',
                   'migrate-getmaxdowntime','migrate-compcache',
                   'migrate-setspeed','migrate-getspeed','migrate-postcopy',
                   'numatune','qemu-attach','qemu-monitor-command',
                   'qemu-monitor-event','qemu-agent-command',
                   'guest-agent-timeout','reboot','reset','restore',
                   'resume','save','save-image-define','save-image-dumpxml',
                   'save-image-edit','schedinfo','screenshot',
                   'set-lifecycle-action','set-user-sshkeys','set-user-password',
                   'setmaxmem','setmem','setvcpus','shutdown','start','suspend',
                   'undefine','update-device','update-memory-device','vcpucount',
                   'vcpuinfo','vcpupin','emulatorpin','vncdisplay','guestvcpus',
                   'setvcpu','domblkthreshold','guestinfo','domdirtyrate-calc' ]

def main():
    """ main function"""

    usage = """usage: 
        %prog -f GROUP.yaml -g VM_GROUP -c 'command command_option' 
        """
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-g', '--group',
        dest = 'group',
        action = 'store',
        help = 'Group of VM to use')
    parser.add_option('-f', '--file',
        dest = 'file',
        action = 'store',
        default = 'groups.yaml',
        help = 'Group file to use as yaml file (default will be groups.yaml)')
    parser.add_option('-c', '--cmd',
        dest = 'cmd',
        #choices = listdomaincmd,
        help = 'Command to execute on a group of VM')
    parser.add_option('-s', '--showgroup',
        dest = 'show',
        action = 'store_false',
        help = 'Show group of VM file content')
    parser.add_option('-v', '--virsh',
        dest = 'virsh',
        action = 'store_false',
        help = 'Show all virsh domain commands available')
    parser.add_option('-d', '--cmddoc',
        dest = 'cmddoc',
        action = 'store',
        choices = listdomaincmd,
        help = 'Show the virsh CMD documentation')

    print('\n')
    (options, args) = parser.parse_args()

    if options.file is None:
        parser.error('Yaml File of group of VM not given')
    if options.show is None:
        pass
    else:
        show_group(options.file)
        return 0
    if options.virsh is None:
        pass
    else:
        cmd = "virsh help domain"
        out, errs = system_command(cmd)
        out = str(out, 'utf-8')
        print(out)
        if errs:
            print(errs)
        return 0
    if options.cmddoc is None:
        pass
    else:
        cmd = "virsh help " +options.cmddoc
        out, errs = system_command(cmd)
        #out = str(out, 'utf-8')
        print(out)
        if errs:
            print(errs)
        return 0

    if options.group is None:
        parser.error('Group of VM to use not given')
        print(usage)

    if options.cmd is None:
        print('Nothing todo, no command to execute... Available are:')
        print(listdomaincmd)
    else:
        check_group(options.file,options.group)
        # for now launch a virsh commande line
        para_cmd(options.file,options.group,options.cmd)
        return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled by user.')
        exit(1)
