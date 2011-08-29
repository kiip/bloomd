"""
This module is responsible for reading and maintaining
the system configuration for BloomD.
"""
import sys
import os.path
from ConfigParser import ConfigParser

def read_config(filename='bloomd.cfg'):
    cfp = ConfigParser()
    cfp.read([filename])

    # Copy from defaults, update
    settings = dict(DEFAULTS)
    for key,val in DEFAULTS.iteritems():
        if not cfp.has_option("bloomd", key): continue
        provided = cfp.get("bloomd", key)
        expected_type = type(val)
        try:
            provided = expected_type(provided)
            settings[key] = provided
        except:
            print "Setting '%s' has invalid type!" % key
            sys.exit(1)

    # Perform custom validation
    for key,validator in VALIDATORS.iteritems():
        try:
            validator(settings[key])
        except Warning, e:
            print e
        except EnvironmentError, e:
            print e
            sys.exit(1)

    # Return the settings
    return settings

def valid_data_dir(dir):
    "Checks that the data dir is valid"
    if not os.path.exists(dir):
        raise EnvironmentError, "Providied data dir is does not exist!"
    if not os.path.isdir(dir):
        raise EnvironmentError, "Providied data dir is not a directory!"
    try:
        test_file = os.path.join(dir, "PERMTEST")
        fh = open(test_file, "a+")
        fh.close()
        os.remove(test_file)
    except:
        raise EnvironmentError, "Cannot write to data directory!"

def sane_scale_size(scale):
    "Checks the scale size is sane"
    if scale < 2:
        raise EnvironmentError, "Scale size must be at least 2!"
    elif scale > 4:
        raise Warning, "Scale size over 4 not recommended!"

def sane_probability(prob):
    "Checks the default probability is sane"
    if prob == 1:
        raise EnvironmentError, "Probability should not be 1!"
    elif prob > 0.01:
        raise Warning, "Probability set very high! Continuing..."

def valid_log_level(lvl):
    if lvl not in ("DEBUG","INFO","WARN","ERROR","CRITICAL"):
        raise EnvironmentError, "Invalid log level!"

# Define our defaults here
DEFAULTS = {
    "port" : 8673,
    "data_dir" : "/tmp/bloomd",
    "log_file" : "/var/log/bloomd.log",
    "log_level" : "DEBUG",
    "initial_size" : 16*1024*1024, # 32MB
    "scale_size" : 4,
    "default_probability": 1E-6,
    "probability_reduction" : 0.9,
    "initial_k" : 4,
    "flush_interval" : 60,
}

VALIDATORS = {
    "data_dir": valid_data_dir,
    "scale_size": sane_scale_size,
    "default_probability": sane_probability,
    "log_level": valid_log_level,
}

