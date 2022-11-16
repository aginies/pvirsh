#!/usr/bin/env python3
# Authors: Antoine Ginies <aginies@suse.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing as mp
import subprocess
from pathlib import Path
import yaml

def esc(code):
    """
    Better layout with some color
    """
    # foreground: 31:red 32:green 34:blue 36:cyan
    # background: 41:red 44:blue 107:white
    # 0:reset
    return f'\033[{code}m'

def print_error(text):
    """
    Print error in red
    """
    formated_text = esc('31;1;1') +text +esc(0)
    print(formated_text)

def print_ok(text):
    """
    Print ok in green
    """
    formated_text = esc('32;1;1') +text +esc(0)
    print(formated_text)

def validate_file(file):
    """
    validate the yaml file
    """

    with open(file, 'r') as stream:
        try:
            yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
            print_error(' Please fix the Yaml file... exiting')
            exit(1)

def show_file_example():
    """
    Show an example of a groups.yaml file
    """

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
    print('Example of a groups.yaml file:')
    print(example)


def find_all_vm(conn):
    """
    Find all VM from the current Hypervisor
    """
    allvm_list = []
    # Store all VM from the hypervisor
    domains = conn.listAllDomains(0)
    for domain in domains:
        if domain.name():
            vmdomain = domain.name()
            allvm_list.append(vmdomain)
    return allvm_list

def check_file_exist(groupfile):
    """
    Check the gile exist
    """
    my_file = Path(groupfile)
    if my_file.is_file():
        validate_file(my_file)
    else:
        print_error('File '+groupfile +' Doesnt exist!\n')
        show_file_example()


def check_group(groupfile, group):
    """
    check that the group exist in the yaml file
    """
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
            print_error(group +' Group Not found!')
            return 666
    return 0

def show_group(groupfile):
    """
    show all group and machines
    """
    check_file_exist(groupfile)
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        print('Available groups are:')
        for item, value in groups.items():
            print('Group '+esc('36;1;1')+str(item)+esc(0)+': '+str(value))
        print('\n')

def system_command(cmd):
    """
    Launch a system command
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'utf-8')
    return out, errs

def do_virsh_cmd(virtum, cmd, cmdoptions):
    """
    Execute the command on all the VM defined
    """
    cmdtolaunch = cmd + ' ' + virtum + ' ' + cmdoptions
    out, errs = system_command(cmdtolaunch)
    out = out.strip("\n")
    if errs:
        print('Command was:' +str(cmdtolaunch))
        print_error('ERROR: ' +str(virtum)+ ': ' +str(errs)+'\n')
    else:
        print(cmdtolaunch, end=" ")
        print(out + " " + esc('32;1;4') + 'Done' + esc(0))

def para_cmd(file, group, cmd, conn, show, VMS):
    """
    Start pool of command
    """
    results = ''
    vms = vm_selected(file, group, conn, VMS)

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
            if show == 'on':
                print(str(cmd) +' ' +virtm +' ' +str(cmdoptions))
            pool.apply_async(do_virsh_cmd, args=(virtm, cmd, cmdoptions))
    pool.close()
    pool.join()
    print(results) #[:10])

def vm_selected(file, group, conn, VMS=''):
    """
    return the vm selected matching on the hypervisor
    """
    vms = ''
    # manual selection of VM
    if group == "SELECTED_VMS":
        if ',' in VMS:
            print('Multiple VM selected')
            VMS = VMS.split(",")
            for allvms in VMS:
                vms = vms +' '+allvms
        else:
            vms = VMS

    # selection by group
    elif ',' in group:
        print('Multiple group selected')
        mgroup = group.split(",")
        for allgroup in mgroup:
            morevms = find_matching_vm(file, allgroup, conn)
            vms = vms +morevms
    else:
        vms = find_matching_vm(file, group, conn)
    return vms


def find_matching_vm(groupfile, group, conn):
    """
    Return the list of VM matching the group
    """
    with open(groupfile) as file:
        groups = yaml.full_load(file)
        vms = ""
        for item, value in groups.items():
            # only match vm of the correct group
            if item == group:
                print('Selected group is ' +esc('36;1;4')+item+esc(0)+ ': ' + str(value))
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
                    print_error('No domain to manage on this host!')
        return vms
