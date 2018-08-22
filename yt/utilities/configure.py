# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2016, yt Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import os
import shutil
import sys
import argparse
from yt.config import CURRENT_CONFIG_FILE, _OLD_CONFIG_FILE, _OLD_INI_CONFIG_FILE, YTConfig

CONFIG = YTConfig()
CONFIG.read(CURRENT_CONFIG_FILE)


def get_config(section, option):
    try:
        return CONFIG[section, option]
    except KeyError:
        print('Option "%s %s" does not exist in the configuration' % (section, option))
        sys.exit(1)


def _cast_helper(v):
    types = (int, float, bool_caster)
    for t in types:
        try:
            return t(v)
        except ValueError:
            pass
    return v

def bool_caster(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    raise ValueError

def set_config(section, option, value):
    if section not in CONFIG:
        CONFIG[section] = {}
    # Try to cast value to one int float or bool
    value = _cast_helper(value)
    print('Setting %s %s to %s' % (section, option, value))
    CONFIG[section, option] = value
    write_config()


def write_config(fd=None):
    if fd is None:
        with open(CURRENT_CONFIG_FILE, 'w') as fd:
            CONFIG.write(fd)
    else:
        CONFIG.write(fd)

def migrate_config_to_ini():
    if not os.path.exists(_OLD_CONFIG_FILE):
        print('Old config not found.')
        return
    CONFIG.read(_OLD_CONFIG_FILE)
    print('Writing a new config file to: {}'.format(CURRENT_CONFIG_FILE))
    write_config()
    print('Backing up the old config file: {}.bak'.format(_OLD_CONFIG_FILE))
    os.rename(_OLD_CONFIG_FILE, _OLD_CONFIG_FILE + '.bak')

    old_config_dir = os.path.dirname(_OLD_CONFIG_FILE)
    plugin_file = CONFIG.get('yt', 'pluginfilename')
    if plugin_file and \
            os.path.exists(os.path.join(old_config_dir, plugin_file)):
        print('Migrating plugin file {} to new location'.format(plugin_file))
        shutil.copyfile(
            os.path.join(old_config_dir, plugin_file),
            os.path.join(os.path.dirname(CURRENT_CONFIG_FILE), plugin_file))
        print('Backing up the old plugin file: {}.bak'.format(_OLD_CONFIG_FILE))
        plugin_file = os.path.join(old_config_dir, plugin_file)
        os.rename(plugin_file, plugin_file + '.bak')

def migrate_config_to_toml():
    if not os.path.exists(_OLD_INI_CONFIG_FILE)    :
        print('Old init config file not found.')
        return
    from six.moves import configparser
    cp = configparser.ConfigParser()
    cp.read(_OLD_INI_CONFIG_FILE)
    new_cp = YTConfig()
    # Read toml configuration file (if any)
    new_cp.read(CURRENT_CONFIG_FILE)
    for section in cp.sections():
        if section not in new_cp:
            new_cp[section] = {}

        for option in cp.options(section):
            value = _cast_helper(cp.get(section, option))
            print('Setting %s %s to %s' % (section, option, value))
            new_cp[section, option] = value
    print('Writing a new config file to: {}'.format(CURRENT_CONFIG_FILE))
    new_cp.write(CURRENT_CONFIG_FILE)
    print('Backing up the old ini config file: {}.bak'.format(_OLD_INI_CONFIG_FILE))
    os.rename(_OLD_INI_CONFIG_FILE, _OLD_INI_CONFIG_FILE + '.bak')

def migrate_config():
    migrate_config_to_ini()
    migrate_config_to_toml()

def rm_config(section, option):
    del CONFIG[section][option]
    write_config()


def main():
    parser = argparse.ArgumentParser(
        description='Get and set configuration values for yt')
    subparsers = parser.add_subparsers(help='sub-command help', dest='cmd')

    get_parser = subparsers.add_parser('get', help='get a config value')
    set_parser = subparsers.add_parser('set', help='set a config value')
    rm_parser = subparsers.add_parser('rm', help='remove a config option')
    subparsers.add_parser('migrate', help='migrate old config file')
    subparsers.add_parser('list', help='show all config values')

    get_parser.add_argument(
        'section', help='The section containing the option.')
    get_parser.add_argument('option', help='The option to retrieve.')

    set_parser.add_argument(
        'section', help='The section containing the option.')
    set_parser.add_argument('option', help='The option to set.')
    set_parser.add_argument('value', help='The value to set the option to.')

    rm_parser.add_argument(
        'section', help='The section containing the option to remove.')
    rm_parser.add_argument('option', help='The option to remove.')

    args = parser.parse_args()

    if args.cmd == 'get':
        print(get_config(args.section, args.option))
    elif args.cmd == 'set':
        set_config(args.section, args.option, args.value)
    elif args.cmd == 'list':
        write_config(sys.stdout)
    elif args.cmd == 'migrate':
        migrate_config()
    elif args.cmd == 'rm':
        rm_config(args.section, args.option)

if __name__ == '__main__':
    main()  # pragma: no cover
