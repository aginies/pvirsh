#!/usr/bin/env python3
# Authors: Antoine Ginies <aginies@suse.com>
#

from pathlib import Path
import argparse
from cmd import Cmd
import os
import sys
import yaml
import pvirsh.connection as connection
import pvirsh.util as util

def list_group(groupfile):
    """show all group and machines"""

    util.check_file_exist(groupfile)
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        l_group = []
        for item, value in groups.items():
            #print(item)
            l_group.append(item)
        return l_group

def find_yaml_file():
    """ Show all yaml file in current path"""
    yaml_list = []
    for files in os.listdir('.'):
        if files.endswith(".yaml"):
            yaml_list.append(files)
    return yaml_list

def find_xml_file(xmldir):
    """ Show all xml files in xml dir"""
    xml_list = []
    if os.path.isdir(xmldir):
        for files in os.listdir(xmldir):
            if files.endswith(".xml"):
                xml_list.append(files)
        return xml_list
    else:
        util.print_error('No' +xmldir +' directory found...')

# list of domain command available with virsh
# removed: create console domrename define managedsave-define managedsave-edit domid edit event
LIST_DOMAIN_CMD = ['attach-device', 'attach-disk', 'attach-interface',
                   'autostart', 'blkdeviotune', 'blkiotune', 'blockcommit',
                   'blockcopy', 'blockjob', 'blockpull', 'blockresize',
                   'change-media', 'cpu-stats', 'desc', 'destroy', 'detach-device',
                   'detach-device-alias', 'detach-disk', 'detach-interface',
                   'domdisplay', 'domfsfreeze', 'domfsthaw', 'domfsinfo',
                   'domfstrim', 'domhostname', 'domid', 'domif-setlink',
                   'domiftune', 'domjobabort', 'domjobinfo', 'domlaunchsecinfo',
                   'domsetlaunchsecstate', 'domname', 'dompmsuspend',
                   'dompmwakeup', 'domuuid', 'domxml-from-native', 'domxml-to-native',
                   'dump', 'dumpxml', 'get-user-sshkeys', 'inject-nmi',
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

    usage = """Interactive or Non Interactive command tool to manage multiple VM at the same Time

        Non interactive:
        pvirsh -n -f GROUP.yaml --conn CONNECTOR -g VM_GROUP,VM_GROUP2 -c 'CMD CMD_OPTION'

        Example:
        pvirsh -n --conn local -g suse -c 'domstate --reason'
        """

    show = 'off'
    parser = argparse.ArgumentParser(usage)

    group_help = parser.add_argument_group('help')
    group_help.add_argument('-s', '--showgroup', dest='show', action='store_true',
                            help='Show group from the yaml group file')

    group_config = parser.add_argument_group('config')
    group_config.add_argument('--conn', dest='conn', action='store',
                              help='Connect to the hypervisor (local | ssh)')
    group_config.add_argument('-g', '--group', dest='group', action='store',
                              help='Group of VM to use (could be a list separated by ,)')
    group_config.add_argument('-f', '--file', dest='file', action='store',
                              help='Group file to use as yaml file')

    group_exec = parser.add_argument_group('exec')
    group_exec.add_argument('-n', '--noninter', dest='noninter', action='store_true',
                            help='Launch this tool in non interactive mode')
    group_exec.add_argument('-c', '--cmd', dest='cmd', help='Command to execute on a group of VM')

    print('\n')
    args = parser.parse_args()

    if args.noninter is False:
        MyPrompt().cmdloop()
    else:
        # yaml group file
        if args.file is None:
            parser.error('Yaml File of group of VM not given')

        if args.show is False:
            pass
        else:
            print(args.file)
            util.check_file_exist(args.file)
            util.show_group(args.file)
            return 0

        # connector
        if args.conn is None:
            parser.error('No connector selected!: local | ssh ')
        elif args.conn == 'local':
            conn = connection.LibVirtConnect.local()
        elif args.conn == 'ssh':
            remoteip = str(input("(qemu) Remote IP address? "))
            conn = connection.LibVirtConnect.remote('qemu+ssh', remoteip)

        if args.group is None:
            parser.error('Group of VM to use not given')
            print(usage)

        if args.cmd is None:
            util.print_error('Nothing todo, no COMMAND to execute...')
            print('-c COMMAND')
            util.print_ok('Available are:')
            print(list_domain_all_cmd)
        else:
            if ',' in args.group:
                mgroup = args.group.split(",")
                for allgroup in mgroup:
                    code = util.check_group(args.file, allgroup)
            else:
                code = util.check_group(args.file, args.group)
            # for now launch a virsh commande line
            if code != 666:
                util.para_cmd(args.file, args.group, args.cmd, conn, show)
            else:
                util.print_error('Unknow group!')
        return 0

LIST_CONNECTORS = ['local', 'qemu+ssh', 'xen+ssh']
LIST_SHOW = ['on', 'off']
DEV_OPTIONS_LIST = ['--config', '--persistent', '--live', '--current']

class MyPrompt(Cmd):
    prompt = '> '
    introl = {}
    introl[0] = " Welcome to "+util.esc('32;1;1') +"pvirsh "+util.esc(0)+ "Interactive Terminal!\n"
    introl[1] = util.esc('32;1;1')+" Parallel virsh"+util.esc(0)
    introl[2] = " command to manage selected group of Virtual Machine (async mode)"
    introl[3] = " Version: \n\n" #+pvirsh.__version__+",\n\n"
    introl[4] = " Type: "+util.esc('36;1;1')+'help'+util.esc(0)+" for help with commands\n"
    introl[5] = "       "+util.esc('36;1;1')+'quit'+util.esc(0)+" to quit\n\n"
    introl[6] = "1) Connect to an Hypervisor\n"
    introl[7] = util.esc('36;1;1')+"    conn [TAB]"+util.esc(0)+"\n"
    introl[8] = "2) Select the group yaml file (default will be groups.yaml if in path)\n"
    introl[9] = util.esc('36;1;1')+"    file PATH_TO_FILE/FILE.YAML"+util.esc(0)+" | "+util.esc('36;1;1')+"file [TAB]\n"+util.esc(0)
    introl[10] = "3) Select a group of VM to manage\n"
    introl[11] = util.esc('36;1;1')+"    select_group [TAB]\n"+util.esc(0)
    introl[12] = "4) Run command on selected VM\n"
    introl[13] = util.esc('36;1;1')+"    cmd [TAB]\n"+util.esc(0)
    intro = ''
    for line in range(14):
        intro += introl[line]
    Cmd.vm_group = ''
    # define a default file to load
    Cmd.file = '/etc/pvirsh/groups.yaml'
    # libvirt connection
    Cmd.conn = ''
    # adjust prompt with yaml group file if present
    my_file = Path(Cmd.file)
    if my_file.is_file():
        util.validate_file(Cmd.file)
        # Cmd.promptfile is used for the prompt file
        Cmd.promptfile = 'Group File: '+util.esc('32;1;1')+str(Cmd.file)+util.esc(0)
    else:
        Cmd.promptfile = util.esc('31;1;1')+'No Group file selected'+util.esc(0)
        Cmd.file = ''
    # by default there is no connection to any hypervisor
    Cmd.promptcon = util.esc('31;1;1')+'Not Connected'+util.esc(0)+'\n'
    promptline = '_________________________________________\n'
    # xml directory from system
    #cwdir = os.getcwd()
    Cmd.xmldir = '/var/lib/pvirsh/xml'
    # show the command on all VM or not
    Cmd.show = False
    prompt = promptline +Cmd.promptfile+' | '+Cmd.promptcon+Cmd.vm_group +'> '

    def do_quit(self, args):
        """Exit the application"""
        if Cmd.conn != '':
            print('Disconnecting ...')
            Cmd.conn.close()
        # French Flag :)
        print(util.esc('44')+'Bye'+util.esc('107')+'Bye'+util.esc('41')+'Bye'+util.esc(0))
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
            conn = connection.LibVirtConnect.local()
            Cmd.conn = conn
            if conn != 666:
                Cmd.promptcon = 'Connector: ' +util.esc('32;1;1') +'qemu:///system'+util.esc(0)+'\n'
                self.prompt = self.promptline+Cmd.promptfile+' | '+Cmd.promptcon+self.vm_group +'> '
        elif conn == 'qemu+ssh':
            remoteip = str(input("Remote IP address? "))
            conn = connection.LibVirtConnect.remote('qemu+ssh', remoteip)
            Cmd.conn = conn
            if conn != 666:
                Cmd.promptcon = 'Connector: ' +util.esc('32;1;1') +'qemu+ssh://' +remoteip + '/system'+util.esc(0)+'\n'
                self.prompt = self.promptline+Cmd.promptfile+' | '+Cmd.promptcon+self.vm_group +'> '
        elif conn == 'xen+ssh':
            remoteip = str(input("Remote IP address? "))
            conn = connection.LibVirtConnect.remote('xen+ssh', remoteip)
            Cmd.conn = conn
            if conn != 666:
                Cmd.promptcon = 'Connector: ' +util.esc('32;1;1') +'xen+ssh://' +remoteip +util.esc(0)+'\n'
                self.prompt = self.promptline+Cmd.promptfile+' | '+Cmd.promptcon+self.vm_group +'> '
        else:
            util.print_error('Unknow Connector...')

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
        if self.file == '':
            print('Please select a group yaml file: help file')
        else:
            vm_group = args
            if ',' in vm_group:
                mgroup = vm_group.split(",")
                for allgroup in mgroup:
                    code = util.check_group(self.file, allgroup)
            else:
                code = util.check_group(self.file, vm_group)

            if code != 666:
                #print("Selected group is '{}'".format(args))
                self.prompt = self.promptline+Cmd.promptfile+' | '+Cmd.promptcon+vm_group + '> '
                Cmd.vm_group = vm_group
                self.do_show_vm(args)
            else:
                util.print_error('Unknow group!')
                util.show_group(self.file)

    def complete_select_group(self, text, line, begidx, endidx):
        """ auto completion selection of the VM group"""
        l_group = list_group(self.file)
        if not text:
            completions = l_group[:]
        else:
            completions = [f for f in l_group if f.startswith(text)]
        return completions

    def help_select_group(self):
        print("Select the group of VM to Manage")

    def do_show_group(self, args):
        """Show group from VM file content"""
        if self.file == '':
            print('Please select a group yaml file: help file')
        else:
            util.show_group(self.file)

    def help_show_group(self):
        print('Show group from VM file content')

    def complete_file(self, text, line, begidx, endidx):
        """ auto completion to find yaml file in current path"""
        all_files = find_yaml_file()
        if not text:
            completions = all_files[:]
        else:
            completions = [f for f in all_files if f.startswith(text)]
        return completions

    def do_file(self, args):
        """select the group yaml file"""
        file = args
        my_file = Path(file)
        if my_file.is_file():
            print("Selected group yaml file is '{}'".format(file))
            Cmd.file = file
            util.validate_file(Cmd.file)
            Cmd.vm_group = ''
            Cmd.promptfile = 'Group File: '+util.esc('32;1;1')+str(Cmd.file)+util.esc(0)
            self.prompt = self.promptline+Cmd.promptfile+' | '+Cmd.promptcon+self.vm_group +'> '
        else:
            util.print_error("File " +file +" Doesnt exist!")
            util.show_file_example()

    def help_file(self):
        print('Select the group yaml file')

    def do_show_file(self, args):
        """Show the Group yaml file used"""
        print("Group yaml file used is: "+util.esc('36;1;1')+self.file+util.esc(0))

    def help_show_file(self):
        print("Show the Group yaml file used")

    def do_shell(self, args):
        """Execute a system command"""
        out, errs = util.system_command(args)
        if errs:
            print(errs)
        if not out:
            util.print_error(' No output... seems weird...')
        print(out)

    def help_shell(self):
        print("Execute a system command")

    def do_show_vm(self, args):
        """ Show all VM matching the selected group(s)"""
        group = Cmd.vm_group
        conn = Cmd.conn
        if conn == '':
            print('Connect to an hypervisor to show selected VM: help conn')
        elif self.file == '':
            print('Please select a group yaml file: help file')
        else:
            if group == '':
                print('Please select a group of VM: select_group GROUP_VM')
            else:
                vms = util.vm_selected(self.file, group, conn)
                print('Vm selected by ' +group +' group(s) on this Hypervisor are:')
                print(util.esc('36;1;1')+str(vms)+util.esc(0))
                #print(vms)

    def do_show_all_vm(self,args):
        """Show all VM from the current hypervisor"""
        conn = Cmd.conn
        if conn == '':
            print('Connect to an hypervisor to show selected VM: help conn')
        else:
            allvms = util.find_all_vm(conn)
            print(util.esc('36;1;1')+str(allvms)+util.esc(0))

    def help_show_all_vm(self):
        print("Show all VM from the current hypervisor")

    def help_show_vm(self):
        print('Show all VM matching the selected group(s)')

    def do_show(self, args):
        show = args
        if show == 'on':
            Cmd.show = 'on'
        else:
            Cmd.show = 'off'

    def help_show(self):
        print('Show command executed on VM (on|off)')

    def complete_show(self, text, line, begidx, endidx):
        """ auto completion show option"""
        if not text:
            completions = LIST_SHOW[:]
        else:
            completions = [f for f in LIST_SHOW if f.startswith(text)]
        return completions

    def do_cmd(self, cmd):
        """ Command to execute on a group of VM (virsh)"""
        if Cmd.conn == '':
            print('Connect to an hypervisor: help conn')
        elif self.file == '':
            print('Please select a group yaml file: help file')
        else:
            group = Cmd.vm_group
            if group == '':
                print('Please select a group of VM: select_group GROUP_VM')
            else:
                testcmd = cmd.split(" ")
                if testcmd[0] in list_domain_all_cmd:
                    util.para_cmd(self.file, group, cmd, self.conn, Cmd.show)
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
            out, errs = util.system_command(fcmd)
            print(str(out) +str(errs))
        else:
            print(list_domain_all_cmd)

    def help_hcmd(self):
        print("Show the option of a virsh command")

    def do_add_dev(self, args):
        """Add a device using an xml file"""
        if args != '':
            if os.path.isfile(Cmd.xmldir+'/'+args):
                option = str(input("Wich option?\n"+str(DEV_OPTIONS_LIST)+"\n"))
                finalcmd = "attach-device --file " + Cmd.xmldir+'/'+args+' '+option
                self.do_cmd(finalcmd)
            else:
                util.print_error('Please select an XML file')
        else:
            self.help_add_dev()

    def complete_add_dev(self, text, line, begidx, endidx):
        """ auto completion add_dev help command"""
        xml_list = find_xml_file(Cmd.xmldir)
        if not text:
            completions = xml_list[:]
        else:
            completions = [f for f in xml_list if f.startswith(text)]
        return completions

    def help_add_dev(self):
        print('Add a device using an xml file')

    def do_remove_dev(self, args):
        """Remove a device using an xml file"""
        if args != '':
            if os.path.isfile(Cmd.xmldir+'/'+args):
                option = str(input("Wich option?\n"+str(DEV_OPTIONS_LIST)+"\n"))
                finalcmd = "detach-device --file " + Cmd.xmldir+'/'+args+' '+option
                self.do_cmd(finalcmd)
            else:
                util.print_error('Please select an XML file')
        else:
            self.help_remove_dev()

    def help_remove_dev(self):
        print('Remove a device using an xml file')

    def complete_remove_dev(self, text, line, begidx, endidx):
        """ auto completion remove_dev help command"""
        xml_list = find_xml_file(Cmd.xmldir)
        if not text:
            completions = xml_list[:]
        else:
            completions = [f for f in xml_list if f.startswith(text)]
        return completions

    do_EOF = do_quit
    help_EOF = help_quit


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled by user.')
        exit(1)