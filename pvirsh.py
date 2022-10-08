#!/usr/bin/env python3
# aginies@suse.com
#
# EXPERIMENTAL
# draft of a scalable VM management tool for a group of VM
# Interactive or non interactive mode
#
# Goal at the end is being able to on this group of VM
# - execute command
# - add / remov devices
# - plenty of other stuff :)

import multiprocessing as mp
import subprocess
from pathlib import Path
import optparse
from cmd import Cmd
import yaml

VERSION = "0.1"

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
            return 666
    return 0

def check_file_exist(groupfile):
    my_file = Path(groupfile)
    if my_file.is_file():
        pass
    else:
        print('File ' +groupfile + ' Doesnt exist!\n')
        show_file_example()
        exit(1)

def show_group(groupfile):
    """show all group and machines"""

    check_file_exist(groupfile)
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        print('Available groups are:')
        for item, value in groups.items():
            print('Group ' +str(item) + ': '  +str(value))
        print('\n')

def list_group(groupfile):
    """show all group and machines"""

    check_file_exist(groupfile)
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        l_group = []
        for item, value in groups.items():
            #print(item)
            l_group.append(item)
        return l_group

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
    #tolaunch = 'virsh ' +str(cmd) + ' VirtualMachineName ' +str(cmdoptions)
    #print('Will launch: ' +tolaunch +'\n')
    cmd = 'virsh ' +cmd
    pool = mp.Pool(mp.cpu_count())
    for virtum in vms:
        pool.apply_async(do_virsh_cmd, args=(virtum, cmd, cmdoptions))
    pool.close()
    pool.join()
    print(results) #[:10])

# list of domain command available with virsh
# remove some: create console domrename define managedsave-define managedsave-edit domid
list_domain_cmd = ['attach-device', 'attach-disk', 'attach-interface',
                   'autostart', 'blkdeviotune', 'blkiotune', 'blockcommit',
                   'blockcopy', 'blockjob', 'blockpull', 'blockresize',
                   'change-media', 'cpu-stats', 'desc', 'destroy', 'detach-device',
                   'detach-device-alias', 'detach-disk', 'detach-interface',
                   'domdisplay', 'domfsfreeze', 'domfsthaw', 'domfsinfo',
                   'domfstrim', 'domhostname', 'domid', 'domif-setlink',
                   'domiftune', 'domjobabort', 'domjobinfo', 'domlaunchsecinfo',
                   'domsetlaunchsecstate', 'domname', 'dompmsuspend', 'domstate',
                   'dompmwakeup', 'domuuid', 'domxml-from-native', 'domxml-to-native',
                   'dump', 'dumpxml', 'edit', 'event', 'get-user-sshkeys', 'inject-nmi',
                   'iothreadinfo', 'iothreadpin', 'iothreadadd', 'iothreadset',
                   'iothreaddel', 'send-key', 'send-process-signal', 'managedsave',
                   'managedsave-remove', 'managedsave-dumpxml', 'memtune', 'perf',
                   'metadata', 'migrate', 'migrate-setmaxdowntime',
                   'migrate-getmaxdowntime', 'migrate-compcache', 'migrate-setspeed',
                   'migrate-getspeed', 'migrate-postcopy', 'numatune', 'qemu-attach',
                   'qemu-monitor-command', 'qemu-monitor-event', 'qemu-agent-command',
                   'guest-agent-timeout', 'reboot', 'reset', 'restore', 'resume', 'save',
                   'save-image-define', 'save-image-dumpxml', 'save-image-edit',
                   'schedinfo', 'screenshot', 'set-lifecycle-action', 'set-user-sshkeys',
                   'set-user-password', 'setmaxmem', 'setmem', 'setvcpus', 'shutdown',
                   'start', 'suspend', 'ttyconsole', 'undefine', 'update-device',
                   'update-memory-device', 'vcpucount', 'vcpuinfo', 'vcpupin',
                   'emulatorpin', 'vncdisplay', 'guestvcpus', 'setvcpu', 'domblkthreshold',
                   'guestinfo', 'domdirtyrate-calc']

list_domain_monitoring = ['domblkerror', 'domblkinfo', 'domblklist', 'domblkstat',
                          'domcontrol', 'domif-getlink', 'domifaddr', 'domiflist',
                          'domifstat', 'dominfo', 'dommemstat', 'domstate',
                          'domstats', 'domtimedomain', 'list']

list_domain_all_cmd = list_domain_cmd + list_domain_monitoring

def main():
    """ main function"""

    usage = """usage:

        Interactive or Non Interactive command tool to manage multiple VM at the same Time

        Non interactive:
        %prog -n  -f GROUP.yaml -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        example:
        %prog -n -g suse -c 'domstate --reason'
        """
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-n', '--noninteractive', dest='noninteractive', action='store_false',
                      help='Launch this tool in non interactive mode')
    parser.add_option('-g', '--group', dest='group', action='store',
                      help='Group of VM to use (could be a list separated by ,)')
    parser.add_option('-f', '--file', dest='file', action='store', default='groups.yaml',
                      help='Group file to use as yaml file (default will be groups.yaml)')
    parser.add_option('-c', '--cmd', dest='cmd', help='Command to execute on a group of VM')
    parser.add_option('-s', '--showgroup', dest='show', action='store_false',
                      help='Show group from VM file content')
    parser.add_option('-v', '--virsh', dest='virsh', action='store_false',
                      help='Show all virsh domain commands available')
    parser.add_option('-d', '--cmddoc', dest='cmddoc', action='store',
                      choices=list_domain_all_cmd,
                      help='Show the virsh CMD documentation')

    print('\n')
    (options, args) = parser.parse_args()

    if options.noninteractive is None:
        MyPrompt().cmdloop()
    else:
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
            print(list_domain_all_cmd)
        else:
            if ',' in options.group:
                mgroup = options.group.split(",")
                for allgroup in mgroup:
                    code = check_group(options.file, allgroup)
            else:
                code = check_group(options.file, options.group)
            # for now launch a virsh commande line
            if code != 666:
                para_cmd(options.file, options.group, options.cmd)
            else:
                print('Unknow group!')
            return 0
        return 0

class MyPrompt(Cmd):
    prompt = '> '
    intro = " Welcome to pvirsh interactive terminal!\n Version: " +VERSION + """

Type:  'help' for help with commands
       'quit' to quit

1) Select the group yasml file (default will be groups.yaml)
    file PATH_TO_FILE/FILE.YAML
2) Select a group of VM:
    select group [TAB]
3) Run a command:
    cmd [TAB]
"""
    Cmd.vm_group = None
    # define a default file
    Cmd.file = 'groups.yaml'

    def do_quit(self, args):
        print("Bye Bye")
        return True

    def help_quit(self):
        print('Exit the application. Shorthand: Ctrl-D.')

    def do_select_group(self, args):
        vm_group = args
        if ',' in vm_group:
            mgroup = vm_group.split(",")
            for allgroup in mgroup:
                code = check_group(self.file, allgroup)
        else:
            code = check_group(self.file, vm_group)

        if code != 666:
            print("Selected group is '{}'".format(args))
            self.prompt = vm_group + ' > '
            Cmd.vm_group = vm_group
        else:
            print('Unknow group!')

    def complete_select_group(self, text, line, begidx, endidx):
        l_group = list_group(self.file)
        if not text:
            completions = l_group[:]
        else:
            completions = [f
                           for f in l_group
                           if f.startswith(text)
                          ]
        return completions

    def help_select_group(self):
        print("Select the group of VM to Manage")

    def do_show_group(self, args):
        show_group(self.file)

    def help_show_group(self):
        print('Show group from VM file content')

    def do_file(self, args):
        file = args
        my_file = Path(file)
        if my_file.is_file():
            print("Selected group yaml file is '{}'".format(file))
            Cmd.file = file
        else:
            print(file +" Doesnt exist!")

    def help_file(self):
        print('Show slected group yaml file')

    def do_show_file(self, args):
        print("Group yaml file used is: " +self.file)

    def help_show_file(self):
        print("Show the Group yaml file used")

    def do_cmd(self, cmd):
        group = Cmd.vm_group
        if group is None:
            print('Please seclect a group of VM: select_group GROUP_VM')
        else:
            testcmd = cmd.split(" ")
            if testcmd[0] in list_domain_all_cmd:
                para_cmd(self.file, group, cmd)
            else:
                print(list_domain_all_cmd)

    def complete_cmd(self, text, line, begidx, endidx):
        if not text:
            completions = list_domain_all_cmd[:]
        else:
            completions = [f for f in list_domain_all_cmd if f.startswith(text)]
        return completions

    def help_cmd(self):
        print("Command to execute on a group of VM")

    # same as complete_hcmd but sadly cant not copy it as it will not work...
    def complete_hcmd(self, text, line, begidx, endidx):
        if not text:
            completions = list_domain_all_cmd[:]
        else:
            completions = [f for f in list_domain_all_cmd if f.startswith(text)]
        return completions

    def do_hcmd(self, cmd):
        if cmd in list_domain_all_cmd:
            fcmd = 'virsh help ' +cmd
            out, errs = system_command(fcmd)
            print(str(out) +str(errs))
        else:
            print(list_domain_all_cmd)

    def help_hcmd(self):
        print("Show the option of a virsh command")

    do_EOF = do_quit
    help_EOF = help_quit


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled by user.')
        exit(1)
