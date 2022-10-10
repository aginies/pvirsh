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
import argparse
from cmd import Cmd
import sys
import libvirt
import yaml

VERSION = "0.6"

class LibVirtConnect:
    """Connection method to libvirt"""

    def __init__(self, connector, dst):
        self.connector = connector
        self.dst = dst
        print(connector +" "+ dst)

    def local():
        conn = None
        try:
            conn = libvirt.open("qemu:///system")
            ver = conn.getVersion()
            print('Connected; Version: '+str(ver))
            return conn
        except libvirt.libvirtError as verror:
            print(repr(verror), file=sys.stderr)
            return 666

    def remote(connector, dst):
        dst_conn = None
        print(connector+'://'+dst+'/system')
        try:
            dst_conn = libvirt.open(connector+'://'+dst+'/system')
            ver = dst_conn.getVersion()
            print('Connected; Version: '+str(ver))
            return dst_conn
        except libvirt.libvirtError as verror:
            print(repr(verror), file=sys.stderr)
            return 666

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
    """Launch a system command"""

    #print(cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'utf-8')
    return out, errs

def find_matching_vm(groupfile, group, conn):
    """Return the list of VM matching the group"""

    with open(groupfile) as file:
        groups = yaml.full_load(file)
        vms = ""
        for item, value in groups.items():
            # only match vm of the correct group
            if item == group:
                print('Selected group is ' +item + ': ' + str(value))
                # get the list of domain from the host
                domains = conn.listAllDomains(0)
                # check if there is a domain
                if len(domains) != 0:
                    # parse VM list on the host
                    for domain in domains:
                        # parse all VM which should be matched in the group.yaml file (virtum)
                        for virtum in value:
                            vmdomain = domain.name()
                            # check the regex contains $ at the end
                            if virtum.endswith('$'):
                                # spliting the check
                                check = virtum.split('$')
                                # if same start and ending with $ this is an exact match
                                if vmdomain.startswith(check[0]):
                                    #print('exact matching ' +vmdomain +' ' +virtum)
                                    vms = vmdomain + ' ' +vms
                                else:
                                    #print('not exact matching ' +vmdomain +' ' +virtum)
                                    pass
                            # case of regex does not finish with $
                            else:
                                # we can compare directly the vmdomain with the virtum start string
                                if vmdomain.startswith(virtum):
                                    #print('matching ' +vmdomain +' ' +virtum)
                                    vms = vmdomain + ' ' +vms
                                else:
                                    #print('doesnt match anything....')
                                    pass
                else:
                    print(esc('31;1;4')+'No domain to manage on this host!'+esc(0))
# OLD CODE BASE on virsh list
# more simple for matching...
#                for virtum in value:
                    # matching vm in virsh list, must start exactly with the name
                    # if no $ at the end it will wilcard anything
#                    cmd = 'virsh list --all --name| grep "^' +str(virtum) +'"'
#                    out, errs = system_command(cmd)
#                    if errs:
#                        print(errs)
#                    if not out:
#                        print(esc('31;1;1') +virtum +' Virtual Machine Not found' +esc(0))
#                    else:
#                        vms = out + vms
#            else:
#                # not correct group
#                pass
#
        return vms

def do_virsh_cmd(virtum, cmd, cmdoptions):
    """Execute the command on all the VM defined"""

    cmdtolaunch = cmd + ' ' + virtum + ' ' + cmdoptions
    out, errs = system_command(cmdtolaunch)
    out = out.strip("\n")
    if errs:
        print('Command was:' +str(cmdtolaunch))
        print(esc('31;1;1') + 'ERROR: ' +str(virtum)+ ': ' +str(errs)+ esc(0) + '\n')
    else:
        print(cmdtolaunch, end=" ")
        print(out + " " + esc('32;1;4') + 'Done' + esc(0))

def vm_selected(file, group, conn):
    vms = ''
    if ',' in group:
        print('Multiple group selected')
        mgroup = group.split(",")
        for allgroup in mgroup:
            morevms = find_matching_vm(file, allgroup, conn)
            vms = vms +morevms
    else:
        vms = find_matching_vm(file, group, conn)
    return vms

def para_cmd(file, group, cmd, conn):
    """Start pool of command"""

    results = []
    vms = vm_selected(file, group, conn)

    cmdoptions = ''
    # subsystem: splitlines because of \n
    #vms = str(vms).splitlines()
    # list separate by a space " "
    vms = str(vms).split(" ")
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
    for virtm in vms:
        # check virtm is not empty...
        if virtm:
            pool.apply_async(do_virsh_cmd, args=(virtm, cmd, cmdoptions))
    pool.close()
    pool.join()
    print(results) #[:10])

# list of domain command available with virsh
# remove some: create console domrename define managedsave-define managedsave-edit domid
LIST_DOMAIN_CMD = ['attach-device', 'attach-disk', 'attach-interface',
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

LIST_DOMAIN_MONITORING = ['domblkerror', 'domblkinfo', 'domblklist', 'domblkstat',
                          'domcontrol', 'domif-getlink', 'domifaddr', 'domiflist',
                          'domifstat', 'dominfo', 'dommemstat', 'domstate',
                          'domstats', 'domtimedomain', 'list']

list_domain_all_cmd = LIST_DOMAIN_CMD + LIST_DOMAIN_MONITORING

def main():
    """ main function"""

    usage = """
        Interactive or Non Interactive command tool to manage multiple VM at the same Time

        Non interactive:
        pvirsh -n -f GROUP.yaml --conn CONNECTOR -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        Example:
        pvirsh -n --conn local -g suse -c 'domstate --reason'
        """

    parser = argparse.ArgumentParser(usage)

    group_help = parser.add_argument_group('help')
    group_help.add_argument('-v', '--virsh', dest='virsh', action='store_true',
                            help='Show all virsh domain commands available')
    group_help.add_argument('-d', '--cmddoc', dest='cmddoc', action='store_true',
                            help='Show the virsh CMD documentation')
    group_help.add_argument('-s', '--showgroup', dest='show', action='store_true',
                            help='Show group from VM file content')

    group_config = parser.add_argument_group('config')
    group_config.add_argument('-p', '--conn', dest='conn', action='store',
                              help='Connect to the hypervisor (local | ssh)')
    group_config.add_argument('-g', '--group', dest='group',
                              help='Group of VM to use (could be a list separated by ,)')
    group_config.add_argument('-f', '--file', dest='file', action='store', default='groups.yaml',
                              help='Group file to use as yaml file (default will be groups.yaml)')

    group_exec = parser.add_argument_group('exec')
    group_exec.add_argument('-n', '--noninter', dest='noninter', action='store_true',
                            help='Launch this tool in non interactive mode')
    group_exec.add_argument('-c', '--cmd', dest='cmd', help='Command to execute on a group of VM')

    print('\n')
    args = parser.parse_args()

    if args.noninter is False:
        MyPrompt().cmdloop()
    else:
        if args.conn is None:
            parser.error(esc('31;1;1') +'No connector selected!: local | ssh ' +esc(0))
        elif args.conn == 'local':
            conn = LibVirtConnect.local()
        elif args.conn == 'ssh':
            remoteip = str(input("Remote IP address? "))
            conn = LibVirtConnect.remote('qemu+ssh', remoteip)

        if args.file is None:
            parser.error(esc('31;1;1') +'Yaml File of group of VM not given' +esc(0))
        if args.show is False:
            pass
        else:
            show_group(args.file)
            return 0
        if args.virsh is False:
            pass
        else:
            cmd = "virsh help domain"
            out, errs = system_command(cmd)
            print(out)
            if errs:
                print(errs)
            return 0
        if args.cmddoc is False:
            pass
        else:
            cmd = "virsh help " +args.cmddoc
            out, errs = system_command(cmd)
            print(out)
            if errs:
                print(errs)
            return 0

        if args.group is None:
            parser.error(esc('31;1;1') +'Group of VM to use not given' +esc(0))
            print(usage)

        if args.cmd is None:
            print(esc('31;1;1') +'Nothing todo, no COMMAND to execute...' +esc(0))
            print('-c COMMAND')
            print(esc('32;1;4') +'Available are:' +esc(0))
            print(list_domain_all_cmd)
        else:
            if ',' in args.group:
                mgroup = args.group.split(",")
                for allgroup in mgroup:
                    code = check_group(args.file, allgroup)
            else:
                code = check_group(args.file, args.group)
            # for now launch a virsh commande line
            if code != 666:
                para_cmd(args.file, args.group, args.cmd, conn)
            else:
                print(esc('31;1;1') +'Unknow group!' +esc(0))
            return 0
        return 0

LIST_CONNECTORS = ['local', 'qemu+ssh']

class MyPrompt(Cmd):
    prompt = '> '
    intro = " Welcome to pvirsh interactive terminal!\n Version: " +VERSION + """

Type:  'help' for help with commands
       'quit' to quit

1) Connect to an Hypervisor
    conn [TAB]
2) Select the group yasml file (default will be groups.yaml)
    file PATH_TO_FILE/FILE.YAML
3) Select a group of VM:
    select group [TAB]
4) Run a command:
    cmd [TAB]
"""
    Cmd.vm_group = ''
    # define a default file
    Cmd.file = 'groups.yaml'
    Cmd.conn = ''
    Cmd.promptcon = ''
    promptline = '###########################\n'

    def do_quit(self, args):
        """Exit the application"""
        print("Bye Bye")
        if Cmd.conn != '':
            Cmd.conn.close()
        return True

    def help_quit(self):
        print('Exit the application. Shorthand: Ctrl-D.')

    # conn = LibVirtConnect.local()
    # conn = LibVirtConnect.remote('qemu+ssh', '10.0.1.73')
    # conn.close()

    def do_conn(self, args):
        """Setting up the connector to the hypervisor"""
        # conn = LibVirtConnect.local()
        conn = args
        if conn == 'local':
            conn = LibVirtConnect.local()
            Cmd.conn = conn
            if conn != 666:
                Cmd.promptcon = esc('32;1;1') +'Connector: qemu:///system\n' +esc(0)
                self.prompt = self.promptline + Cmd.promptcon +self.vm_group + '> '
        elif conn == 'qemu+ssh':
            remoteip = str(input("Remote IP address? "))
            conn = LibVirtConnect.remote('qemu+ssh', remoteip)
            Cmd.conn = conn
            if conn != 666:
                Cmd.promptcon = esc('32;1;1') +'Connector: qemu+ssh://' +remoteip + '/system' +'\n' +esc(0)
                self.prompt = self.promptline + Cmd.promptcon +self.vm_group + '> '
        else:
            print(esc('31;1;1') +'Unknow Connector...'+esc(0))

    def help_conn(self):
        print('Setting up the connector to the hypervisor: ' +str(LIST_CONNECTORS))

    def complete_conn(self, text, line, begidx, endidx):
        """auto completion list of connectors"""
        if not text:
            completions = LIST_CONNECTORS[:]
        else:
            completions = [f for f in LIST_CONNECTORS if f.startswith(text)]
        return completions

    def do_select_group(self, args):
        """Select the group of VM to Manage"""
        vm_group = args
        if ',' in vm_group:
            mgroup = vm_group.split(",")
            for allgroup in mgroup:
                code = check_group(self.file, allgroup)
        else:
            code = check_group(self.file, vm_group)

        if code != 666:
            print("Selected group is '{}'".format(args))
            self.prompt = self.promptline + Cmd.promptcon +vm_group + ' > '
            Cmd.vm_group = vm_group
        else:
            print(esc('31;1;1') +'Unknow group!' +esc(0))

    def complete_select_group(self, text, line, begidx, endidx):
        """ auto completion selection of the VM group"""
        l_group = list_group(self.file)
        if not text:
            completions = l_group[:]
        else:
            completions = [f for f in l_group if f.startswith(text)
                          ]
        return completions

    def help_select_group(self):
        print("Select the group of VM to Manage")

    def do_show_group(self, args):
        """Show group from VM file content"""
        show_group(self.file)

    def help_show_group(self):
        print('Show group from VM file content')

    def do_file(self, args):
        """select the group yaml file"""
        file = args
        my_file = Path(file)
        if my_file.is_file():
            print("Selected group yaml file is '{}'".format(file))
            Cmd.file = file
        else:
            print(esc('31;1;1') +file +" Doesnt exist!"+esc(0))

    def help_file(self):
        print('Select the group yaml file')

    def do_show_file(self, args):
        """Show the Group yaml file used"""
        print("Group yaml file used is: " +self.file)

    def help_show_file(self):
        print("Show the Group yaml file used")

    def do_exec(self, args):
        """Execute a system command"""
        out, errs = system_command(args)
        if errs:
            print(errs)
        if not out:
            print(esc('31;1;1') +' No output... seems weird...' +esc(0))
        print(out)

    def help_exec(self):
        print("Execute a system command")

    def do_show_vm(self, cmd):
        """ Show all VM matching the selected group(s)"""
        group = Cmd.vm_group
        conn = Cmd.conn
        if conn == '':
            print('Connect to an hypervisor: help conn')
        else:
            if group == '':
                print('Please seclect a group of VM: select_group GROUP_VM')
            else:
                vms = vm_selected(self.file, group, conn)
                print('Vm selected by ' +group +' are:')
                print(vms)

    def help_show_vm(self):
        print('Show all VM matching the selected group(s)')

    def do_cmd(self, cmd):
        """ Command to execute on a group of VM (virsh)"""
        if Cmd.conn == '':
            print('Connect to an hypervisor: help conn')
        else:
            group = Cmd.vm_group
            if group == '':
                print('Please seclect a group of VM: select_group GROUP_VM')
            else:
                testcmd = cmd.split(" ")
                if testcmd[0] in list_domain_all_cmd:
                    para_cmd(self.file, group, cmd, self.conn)
                else:
                    print(list_domain_all_cmd)

    def complete_cmd(self, text, line, begidx, endidx):
        """ auto completion cmd"""
        if not text:
            completions = list_domain_all_cmd[:]
        else:
            completions = [f for f in list_domain_all_cmd if f.startswith(text)]
        return completions

    def help_cmd(self):
        print("Command to execute on a group of VM (virsh)")

    # same as complete_hcmd but sadly cant not copy it as it will not work...
    def complete_hcmd(self, text, line, begidx, endidx):
        """ auto completion help command"""
        if not text:
            completions = list_domain_all_cmd[:]
        else:
            completions = [f for f in list_domain_all_cmd if f.startswith(text)]
        return completions

    def do_hcmd(self, cmd):
        """Show the option of a virsh command """
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
