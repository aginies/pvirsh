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

import multiprocessing as mp
import subprocess
from pathlib import Path
import optparse
import yaml

# TODO: validate the yaml file
def validate_file():
    """ validate the yaml file"""
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

def check_group(groupfile, group):
    """check that the group exist in the yaml file"""

    with open(groupfile) as file:
        groups = yaml.full_load(file)
        keys = list(groups.keys())
        found = False
        # going through the list to find the group
        for key in keys:
            if key == group:
                found = True

        if found:
            pass
        else:
            print(esc('31;1;1') +group +' Group Not found!' +esc(0))
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
        print('Available groups are:')
        for item, value in groups.items():
            print('Group ' +str(item) + ': '  +str(value))
        print('\n')

def system_command(cmd):
    """ Launch a system command  """

    #print(cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'utf-8')
    return out, errs

def find_matching_vm(groupfile, group):
    """return the list of VM matching the group"""

    with open(groupfile) as file:
        groups = yaml.full_load(file)
        # all group store in keys
        vms = ""
        for item, value in groups.items():
            # only match vm of the correct group
            if item == group:
                print('Selected group is ' +item + ': ' + str(value))
                for virtum in value:
                    # matching vm in virsh list, must start exactly with the name
                    # if no $ at the end it will wilcard anything
                    cmd = 'virsh list --all --name| grep "^' +str(virtum) +'"'
                    out, errs = system_command(cmd)
                    if errs:
                        print(errs)
                    if not out:
                        print(esc('31;1;1') +virtum +' Virtual Machine Not found' +esc(0))
                    else:
                        vms = out + vms
            else:
                # not correct group
                pass

        return vms


def do_virsh_cmd(virtum, cmd, cmdoptions):
    """execute the command on all the VM defined"""

    cmdtolaunch = cmd + ' ' + virtum + ' ' + cmdoptions
    out, errs = system_command(cmdtolaunch)
    out = out.strip("\n")
    if errs:
        print('Command was:' +str(cmdtolaunch))
        print(esc('31;1;1') + 'ERROR: ' +str(virtum)+ ': ' +str(errs)+ esc(0) + '\n')
    else:
        print(cmdtolaunch, end=" ")
        print(out + " " + esc('32;1;4') + 'Done' + esc(0))

def para_cmd(file, group, cmd):
    """Start pool of command"""

    results = []
    vms = ''
    if ',' in group:
        print('Multiple group selected')
        mgroup = group.split(",")
        for allgroup in mgroup:
            morevms = find_matching_vm(file, allgroup)
            vms = vms +morevms
    else:
        vms = find_matching_vm(file, group)

    cmdoptions = ''
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
    for virtum in vms:
        pool.apply_async(do_virsh_cmd, args=(virtum, cmd, cmdoptions))
    pool.close()
    pool.join()
    print(results) #[:10])

# list of domain command available with virsh
# remove some: create, console
list_domaincmd = ['attach-device', 'attach-disk', 'attach-interface', 'autostart', 'blkdeviotune', 'blkiotune', 'blockcommit', 'blockcopy', 'blockjob', 'blockpull', 'blockresize', 'change-media', 'console', 'cpu-stats', 'create', 'define', 'desc', 'destroy', 'detach-device', 'detach-device-alias', 'detach-disk', 'detach-interface', 'domdisplay', 'domfsfreeze', 'domfsthaw', 'domfsinfo', 'domfstrim', 'domhostname', 'domid', 'domif-setlink', 'domiftune', 'domjobabort', 'domjobinfo', 'domlaunchsecinfo', 'domsetlaunchsecstate', 'domname', 'domrename', 'dompmsuspend', 'dompmwakeup', 'domuuid', 'domxml-from-native', 'domxml-to-native', 'dump', 'dumpxml', 'edit', 'event', 'get-user-sshkeys', 'inject-nmi', 'iothreadinfo', 'iothreadpin', 'iothreadadd', 'iothreadset', 'iothreaddel', 'send-key', 'send-process-signal', 'lxc-enter-namespace', 'managedsave', 'managedsave-remove', 'managedsave-edit', 'managedsave-dumpxml', 'managedsave-define', 'memtune', 'perf', 'metadata', 'migrate', 'migrate-setmaxdowntime', 'migrate-getmaxdowntime', 'migrate-compcache', 'migrate-setspeed', 'migrate-getspeed', 'migrate-postcopy', 'numatune', 'qemu-attach', 'qemu-monitor-command', 'qemu-monitor-event', 'qemu-agent-command', 'guest-agent-timeout', 'reboot', 'reset', 'restore', 'resume', 'save', 'save-image-define', 'save-image-dumpxml', 'save-image-edit', 'schedinfo', 'screenshot', 'set-lifecycle-action', 'set-user-sshkeys', 'set-user-password', 'setmaxmem', 'setmem', 'setvcpus', 'shutdown', 'start', 'suspend', 'ttyconsole', 'undefine', 'update-device', 'update-memory-device', 'vcpucount', 'vcpuinfo', 'vcpupin', 'emulatorpin', 'vncdisplay', 'guestvcpus', 'setvcpu', 'domblkthreshold', 'guestinfo', 'domdirtyrate-calc']

def main():
    """ main function"""

    usage = """usage:
        %prog -f GROUP.yaml -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        example:
        %prog -g suse -c 'domstate --reason'
        """
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-g', '--group', dest='group', action='store',
                      help='Group of VM to use (could be a list separated by ,)')
    parser.add_option('-f', '--file', dest='file', action='store', default='groups.yaml',
                      help='Group file to use as yaml file (default will be groups.yaml)')
    parser.add_option('-c', '--cmd', dest='cmd', help='Command to execute on a group of VM')
    parser.add_option('-s', '--showgroup', dest='show', action='store_false',
                      help='Show group of VM file content')
    parser.add_option('-v', '--virsh', dest='virsh', action='store_false',
                      help='Show all virsh domain commands available')
    parser.add_option('-d', '--cmddoc', dest='cmddoc', action='store',
                      choices=list_domaincmd,
                      help='Show the virsh CMD documentation')

    print('\n')
    (options, args) = parser.parse_args()

    if options.file is None:
        parser.error(esc('31;1;1') + 'Yaml File of group of VM not given' +esc(0))
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
        print(out)
        if errs:
            print(errs)
        return 0
    if options.cmddoc is None:
        pass
    else:
        cmd = "virsh help " +options.cmddoc
        out, errs = system_command(cmd)
        print(out)
        if errs:
            print(errs)
        return 0

    if options.group is None:
        parser.error(esc('31;1;1') + 'Group of VM to use not given' +esc(0))
        print(usage)

    if options.cmd is None:
        print(esc('31;1;1') + 'Nothing todo, no COMMAND to execute...' +esc(0))
        print('-c COMMAND')
        print(esc('32;1;4') + 'Available are:' +esc(0))
        print(list_domaincmd)
    else:
        if ',' in options.group:
            mgroup = options.group.split(",")
            for allgroup in mgroup:
                check_group(options.file, allgroup)
        else:
            check_group(options.file, options.group)
        # for now launch a virsh commande line
        para_cmd(options.file, options.group, options.cmd)
        return 0
    return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled by user.')
        exit(1)
