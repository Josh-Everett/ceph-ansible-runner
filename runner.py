#!/usr/bin/python

import ansible_runner
import argparse
import os

#global parser var
parser = argparse.ArgumentParser(description='gluster-ansible-runner')

def setup_args():
    parser.add_argument('-p', '--playbook', required=True, help='Specify the playbook you want ansible to use')
    #--playbook brick_setup.yml

    parser.add_argument('-i', '--inventory', required=True, help='Specify the inventory you want ansible to use. Check code for format examples')
    #inventory input examples
    #--inventory [vdos:192.168.122.158,192.168.122.159,192.168.122.160],[other:192.168.122.158,192.168.122.159],[more:192.168.122.158]
    #--inventory [vdos:192.168.122.158,192.168.122.158,192.168.122.158],[other:192.168.122.158]
    #--inventory [vdos:192.168.122.158,192.168.122.158,192.168.122.158]
    #--inventory [vdos:172.28.128.10,172.28.128.11,172.28.128.12,172.28.128.13]

def parse_args():
    active_args = {}
    args = parser.parse_args()

    # convert parsed-Namespace into a key value pairing
    arg_vars = vars(args)

    # toggled settings are placed into dictionary of active arguments
    for foo in arg_vars:
        if arg_vars[foo]:
            active_args[foo] = arg_vars[foo]

    # remove redundant inventory and playbook keys from dictionary
    active_args.pop('inventory')
    active_args.pop('playbook')

    return active_args


# unpack flat string into flat list
def string_to_list(foo):
    # remove brackets and delimt by CSVs
    temp_string = foo[1:-1]
    temp_string = temp_string.split(",")
    new = []
    # remove extra spaces and add to list or return values
    for x in temp_string:
        x = x.replace(' ', '')
        new.append(x)
    return new


# unpack nested lists from input string into valid list format
def unpack_list(foo):
    for key, value in foo.iteritems():
        if value[0] == '[':
            foo[key] = string_to_list(value)
    return foo


def get_inventory():
    #Get inventory
    args = parser.parse_args()

    #create inventroy
    inventory = {}
    #break up groups
    groups = args.inventory.split('],[')
    #go thru groups
    for group in groups:
        #remove extra '[' & ']'
        group = group.replace('[', '')
        group = group.replace(']', '')
        #split group name from ips
        split = group.split(':')
        #creat inner dicts
        hosts = {}
        ips = {}
        #split ips
        ip_list = split[1].split(',')
        #fill ip dict with ips
        for ip in ip_list:
            ips[ip] = ''
        #put ip dict in host dict
        hosts['hosts'] = ips
        #put host in group in inventory dict
        inventory[split[0]] = hosts

    return inventory


# remove generated files
def clean_up():
    files = ['./ansible/env/extravars', './ansible/env/settings', './ansible/inventory/hosts.json']
    for filename in files:
        try:
            os.remove(filename)
        except OSError:
            pass


def main():
    #setup command line args
    setup_args()

    #get args back and reformat them to work with ansible
    arg_vars = unpack_list(parse_args())

    #get inventory
    inventory = get_inventory()

    #playbook
    args = parser.parse_args()
    playbook = args.playbook

    #no output
    settings = {"suppress_ansible_output": False}

    #get private data dir
    directory = os.getcwd() + "/ansible"

    #run playbook wiht inventory
    r = ansible_runner.run(private_data_dir = directory,
                           playbook = playbook,
                           inventory = inventory,
                           extravars = arg_vars,
                           verbosity = 0,
                           settings = settings)
    #clean_up()

if __name__ == "__main__":
    main()
