import os
import warnings
import configparser
import pytoml

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
    storeParameterFiles = False,
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
    sketchfab_api_key = 'None',
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
_OLD_CONFIG_FILE = os.path.join(CONFIG_DIR, 'ytrc')

# Here is the upgrade.  We're actually going to parse the file in its entirety
# here.  Then, if it has any of the Forbidden Sections, it will be rewritten
# without them.
if os.path.exists(_OLD_CONFIG_FILE):
    print((
        'Detected old config file "%s". '
        'You can update to the new config format using `yt migrate config` '
        'or manually create a new config in "%s".') % (_OLD_CONFIG_FILE, CURRENT_CONFIG_FILE))


import collections.abc

def _deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = _deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
        
class YTConfigParser:
    def __init__(self, defaults={}):
        self.config = {'yt': defaults}

    def read(self, filenames):
        if isinstance(filenames, str):
            filenames = [filenames]
        ok_filenames = []
        for i, fname in enumerate(filenames):
            if not os.path.exists(fname):
                continue
            try:
                with open(fname, 'r') as f:
                    cfg = pytoml.load(f)
                _deep_update(self.config, cfg)

                ok_filenames.append(fname)
            except pytoml.TomlError:
                pass
        return ok_filenames

    def get(self, *keys, default=None):
        head = self.config

        for k in keys:
            head = head.get(k, default)
            if head is None:  # couldn't find anything!
                return default
        else:
            return head

    def getint(self, section, key, **kwa):
        ret = self.get(section, key, **kwa)
        assert isinstance(ret, int)
        return ret

    def getboolean(self, section, key, **kwa):
        ret = self.get(section, key, **kwa)
        assert isinstance(ret, bool)
        return ret

    def getfloat(self, section, key, **kwa):
        ret = self.get(section, key, **kwa)
        assert isinstance(ret, float)
        return ret

    def has_section(self, section):
        return section in self.config

    def add_section(self, section):
        if not self.has_section(section):
            self.config[section] = {}

    def remove_section(self, section):
        if self.has_section(section):
            del self.config[section]

    def set(self, section, key, value):
        self.config[section][key] = value

    def __setitem__(self, path, value):
        self.set(path[0], path[1], value)

    def write(self, fd):
        pytoml.dump(self.config, fd)

    def remove_option(self, section, option):
        if self.has_section(section):
            if option in self.config[section]:
                del self.config[section][option]


ytcfg = YTConfigParser(ytcfg_defaults)
ytcfg.read([CURRENT_CONFIG_FILE, 'yt.toml'])

# Now we have parsed the config file.  Overrides come from the command line.

# This should be implemented at some point.  The idea would be to have a set of
# command line options, fed through an option parser, that would override
# the settings in ytcfg.  *However*, because we want to have the command-line
# scripts work, we'd probably want to have them only be long options, and also
# along the lines of --yt-something=somethingelse.  The command line scripts
# would then not get their options from sys.argv, but instead from this module.
