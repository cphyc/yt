"""
This module is very simple.  It imports the configuration
we have written for yt.
Everything will be returned in a global config dictionary ``ytcfg``

"""

from __future__ import print_function

#-----------------------------------------------------------------------------
# Copyright (c) 2013, yt Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import os
import re
import warnings
from collections import defaultdict, Mapping
# from six.moves.configparser import NoOptionError
from yt.extern.six.moves import configparser
import pytoml as toml
from yt.utilities.exceptions import \
    YTFieldNotFound

SECTION_RE = re.compile('^config\.(?P<ftype>\w+)\.(?P<fname>\w+)$')

ytcfg_defaults = dict(
    serialize = False,
    onlydeserialize = False,
    timefunctions = False,
    logfile = False,
    coloredlogs = False,
    suppressStreamLogging = False,
    stdoutStreamLogging = False,
    loglevel = 20,
    inline = False,
    numthreads = -1,
    __withintesting = False,
    __parallel = False,
    __global_parallel_rank = 0,
    __global_parallel_size = 1,
    __topcomm_parallel_rank = 0,
    __topcomm_parallel_size = 1,
    __command_line = False,
    StoreParameterFiles = False,
    parameterfilestore = 'parameter_files.csv',
    maximumstoreddatasets = 500,
    skip_dataset_cache = True,
    loadfieldplugins = True,
    pluginfilename = 'my_plugins.py',
    parallel_traceback = False,
    pasteboard_repo = '',
    reconstruct_index = True,
    test_storage_dir = '/does/not/exist',
    test_data_dir = '/does/not/exist',
    requires_ds_strict = False,
    enzo_db = '',
    hub_url = 'https://girder.hub.yt/api/v1',
    hub_api_key = '',
    hub_sandbox = '/collection/yt_sandbox/data',
    notebook_password = '',
    answer_testing_tolerance = 3,
    answer_testing_bitwise = False,
    gold_standard_filename = 'gold311',
    local_standard_filename = 'local001',
    answer_tests_url = 'http://answers.yt-project.org/{1}_{2}',
    sketchfab_api_key = None,
    imagebin_api_key = 'e1977d9195fe39e',
    imagebin_upload_url = 'https://api.imgur.com/3/upload',
    imagebin_delete_url = 'https://api.imgur.com/3/image/{delete_hash}',
    curldrop_upload_url = 'http://use.yt/upload',
    thread_field_detection = False,
    ignore_invalid_unit_operation_errors = False,
    chunk_size = 1000,
    xray_data_dir = '/does/not/exist',
    supp_data_dir = '/does/not/exist',
    default_colormap = 'arbre',
    ray_tracing_engine = 'embree',
    )

CONFIG_DIR = os.environ.get(
    'XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config', 'yt'))
if not os.path.exists(CONFIG_DIR):
    try: 
        os.makedirs(CONFIG_DIR)
    except OSError:
        warnings.warn("unable to create yt config directory")

CURRENT_CONFIG_FILE = os.path.join(CONFIG_DIR, 'yt.toml')
_OLD_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.yt', 'config')

# Here is the upgrade.  We're actually going to parse the file in its entirety
# here.  Then, if it has any of the Forbidden Sections, it will be rewritten
# without them.

if os.path.exists(_OLD_CONFIG_FILE):
    f = open(_OLD_CONFIG_FILE).read()
    if any(header in f for header in ["[lagos]","[raven]","[fido]","[enki]"]):
        print("***********************************************************")
        print("* Upgrading configuration file to new format; saving old. *")
        print("***********************************************************")
        # This is of the old format
        cp = configparser.ConfigParser()
        cp.read(_OLD_CONFIG_FILE)
        # NOTE: To avoid having the 'DEFAULT' section here,
        # we are not passing in ytcfg_defaults to the constructor.
        new_cp = configparser.ConfigParser()
        new_cp.add_section("yt")
        for section in cp.sections():
            for option in cp.options(section):
                # We changed them all to lowercase
                if option.lower() in ytcfg_defaults:
                    new_cp.set("yt", option, cp.get(section, option))
                    print("Setting %s to %s" % (option, cp.get(section, option)))
        open(_OLD_CONFIG_FILE + ".old", "w").write(f)
        new_cp.write(open(_OLD_CONFIG_FILE, "w"))

    msg = (
        "The configuration file {} is deprecated. "
        "Please migrate your config to {} by running: "
        "'yt config migrate'"
    )
    warnings.warn(msg.format(_OLD_CONFIG_FILE, CURRENT_CONFIG_FILE))

if not os.path.exists(CURRENT_CONFIG_FILE):
    cp = configparser.ConfigParser()
    cp = {'yt': {}}
    try:
        with open(CURRENT_CONFIG_FILE, 'w') as new_cfg:
            toml.dump(cp, new_cfg)
    except IOError:
        warnings.warn("unable to write new config file")

# class YTConfigParser(configparser.ConfigParser, object):
#     def __setitem__(self, key, val):
#         self.set(key[0], key[1], val)

#     def __getitem__(self, key):
#         return self.get(key[0], key[1])

#     def get(self, section, option, *args, **kwargs):
#         val = super(YTConfigParser, self).get(section, option, *args, **kwargs)
#         if type(val) == str:
#             return os.path.expanduser(os.path.expandvars(val))
#         else:
#             return val

#     def get_field_config(self, keys, serializer, getter, default=None):
#         '''Iterate over all the configured fields.

#         Parameters
#         ----------
#         keys : str list
#            Get these items from the configuration.
#         serializer : callable
#            Use this function to determine the exact name of the
#            fields. This function should raise a `YTFieldNotFound` if
#            the field does not exist in the dataset.
#         getter : dict
#            What getter to use for each key. Can be any of 'get',
#            'getboolean', 'getfloat' or 'getint'. See note.
#         default : str, optional
#            If provided, use this value as a fallback.

#         Returns
#         -------
#         The function returns an iterator where each entry is given
#         (ftype, fname, cfg).

#         ftype, fname : str
#            The type and name of the configured field as given in the
#            configuration.
#         cfg : str
#            The value of the configured item.

#         Note
#         ----
#         The getter is the function used to access the configuration. It can any listed in
#         `https://docs.python.org/3.6/library/configparser.html#configparser.ConfigParser.get`.

#         For example `getfloat` will return float values and `getint` int values.
#         '''

#         # Check input values
#         ok_values = ('get', 'getboolean', 'getfloat', 'getint')
#         for key, val in getter.items():
#             if val not in ok_values:
#                 raise Exception("Expected one of %s, got `%s'" % (ok_values, val))

#         default = default if default else defaultdict(lambda: '')
#         for section in self.sections():
#             # Match lines like
#             match = SECTION_RE.match(section)
#             if match:
#                 data = match.groupdict()
#                 ftype = data['ftype']
#                 fname = data['fname']

#                 try:
#                     ftype, fname = serializer((ftype, fname))[0]
#                     for key in keys:
#                         _get = getattr(self, getter[key])
#                         try:
#                             value = _get(section, key)
#                         except NoOptionError:
#                             value = default[key]
#                         if value != '':
#                             yield (ftype, fname), key, value
#                 except YTFieldNotFound:
#                     pass

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class YTConfig(dict):
    def __getitem__(self, keys):
        if type(keys) == str:
            return super(YTConfig, self).__getitem__(keys)
        else:
            node = super(YTConfig, self).__getitem__(keys[0])
            for i in range(1, len(keys)):
                node = node[keys[i]]

            return node

    def __setitem__(self, keys, val):
        if len(keys) == 1:
            keys = keys[0]
        if type(keys) == str:
            return super(YTConfig, self).__setitem__(keys, val)
        else:
            node = self.__getitem__(keys[:-1])
            node[keys[-1]] = val

    def get(self, key, default=None):
        try:
            ret = self[key]
        except KeyError:
            ret = default

        if type(ret) == str:
            return os.path.expanduser(os.path.expandvars(ret))
        else:
            return ret
            

    def update(self, other):
        deep_update(self, other)

    def read(self, files):
        if type(files) == str:
            files = [files]
        for fname in files:
            if os.path.exists(fname):
                with open(fname, 'r') as f:
                    self.update(toml.load(f))

    def write(self, fd):
        toml.dump(self, fd)

    def get_field_config(self, keys, serializer, default=None):
        '''Iterate over all the configured fields.

        Parameters
        ----------
        keys : str list
           Get these items from the configuration.
        serializer : callable
           Use this function to determine the exact name of the
           fields. This function should raise a `YTFieldNotFound` if
           the field does not exist in the dataset.
        default : str, optional
           If provided, use this value as a fallback.

        Returns
        -------
        The function returns an iterator where each entry is given
        (ftype, fname, cfg).

        ftype, fname : str
           The type and name of the configured field as given in the
           configuration.
        cfg : str
           The value of the configured item.
        '''

        default = default if default else defaultdict(lambda: '')
        if 'config' not in self:
            return

        for ftype in self['config']:
            for fname in self['config', ftype]:
                try:
                    ftype, fname = serializer((ftype, fname))[0]
                    for key in keys:
                        value = self.get(['config', ftype, fname, key], default='')
                        if value != '':
                            yield (ftype, fname), key, value
                except YTFieldNotFound:
                    pass



ytcfg = YTConfig({'yt': ytcfg_defaults})
ytcfg.read((_OLD_CONFIG_FILE, CURRENT_CONFIG_FILE, 'yt.toml'))
# Now we have parsed the config file.  Overrides come from the command line.

# This should be implemented at some point.  The idea would be to have a set of
# command line options, fed through an option parser, that would override
# the settings in ytcfg.  *However*, because we want to have the command-line
# scripts work, we'd probably want to have them only be long options, and also
# along the lines of --yt-something=somethingelse.  The command line scripts
# would then not get their options from sys.argv, but instead from this module.
