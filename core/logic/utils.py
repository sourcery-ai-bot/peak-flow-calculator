'''
utils.py 

Some utilities
'''

import os, time

from arcpy import AddMessage, AddWarning, AddError, CreateUniqueName
from arcpy import SetProgressor, SetProgressorLabel, SetProgressorPosition, ResetProgressor
from arcpy import env

import click

def msg(text, arc_status=None, set_progressor_label=False):
    """
    output messages through Click.echo (cross-platform shell printing) 
    and the ArcPy GP messaging interface and progress bars
    """
    click.echo(text)

    if arc_status == "warning":
        AddWarning(text)
    elif arc_status == "error":
        AddError(text)
    else:
        AddMessage(text)
    
    if set_progressor_label:
        SetProgressorLabel(text)

def so(prefix, suffix="random", where="fgdb"):
    """complete path generator for Scratch Output (for use with ArcPy GP tools)

    Generates a string represnting a complete and unique file path, which is
    useful to have for setting as the output parameters for ArcPy functions,
    especially those for intermediate data.

    Inputs:
        prefix: a string for a temporary file name, prepended to suffix
        suffix: unique value type that will be used to make the name unique:
            "u": filename using arcpy.CreateUniqueName(),
            "t": uses local time,
            "r": uses a hash of local time
            "<user string>": any other value provided will be used directly
        where: a string that dictates which available workspace will be
            utilized:
            "fgdb": ArcGIS scratch file geodatabase. this is the default
            "folder": ArcGIS scratch file folder. use sparingly
            "in_memory": the ArcGIS in-memory workspace. good for big
                datasets, but not too big. only set to this for intermediate
                data, as the workspace is not persistent.
                
    Returns:
        A string representing a complete and unique file path.

    """
    
    # set workspace location
    if where == "folder":
        location = env.scratchFolder
    elif where == "in_memory":
        location = "in_memory"
    else:
        location = env.scratchGDB

    # create and return full path
    if suffix == "unique":
        return CreateUniqueName(prefix, location)
    elif suffix == "random":
        return os.path.join(
            location,
            "{0}_{1}".format(
                prefix,
                abs(hash(time.strftime("%Y%m%d%H%M%S", time.localtime())))
            )
        )
    elif suffix == "timestamp":
        return os.path.join(
            location,
            "{0}_{1}".format(
                prefix,
                time.strftime("%Y%m%d%H%M%S", time.localtime())
            )
        )
    else:
        return os.path.join(location,"{0}_{1}".format(prefix,suffix))

# 3rd party dependencies
# (not included with Esri ArcMap; attempt to install when not available)

def attempt_pkg_install(pkg):
    msg("This tool requires the {0} package to be installed. Attempting installation...".format(pkg))
    from pkg_resources import WorkingSet , DistributionNotFound
    working_set = WorkingSet()
    try:
        dep = working_set.require(pkg)
    except DistributionNotFound:
        try:
            from setuptools.command.easy_install import main as install
            install([pkg])
        except:
            msg("This tool was unable to find or install a required dependency: {0}".format(pkg))
            exit

def clean(val):
    """post-process empty values ("") from ArcPy geoprocessing tools.
    """
    if val in ["", None]:
        return 0
    else:
        return val