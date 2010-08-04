#!/usr/bin/env python


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""

#--------------------------------------------------------------------------------------
an_usage = \
"""
%prog \\
      --task-def-dir=~/rackspace \\
      --rackspace-user=${RACKSPACE_USER} \\
      --rackspace-key=${RACKSPACE_KEY}
"""

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--task-def-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "task_def_dir",
                            help = "(\"%default\", by default)",
                            default = "." )

a_option_parser.add_option( "--rackspace-user",
                            metavar = "< cloud user name >",
                            action = "store",
                            dest = "rackspace_user",
                            help = "(\"%default\", by default)",
                            default = None )
    
a_option_parser.add_option( "--rackspace-key",
                            metavar = "< cloud authentification key >",
                            action = "store",
                            dest = "rackspace_key",
                            help = "(\"%default\", by default)",
                            default = None )
    
if __name__ == '__main__' :
    an_options, an_args = a_option_parser.parse_args()

    # Check command line arguments first
    import os.path
    an_options.task_def_dir = os.path.abspath( an_options.task_def_dir )
    if not os.path.isdir( an_options.task_def_dir ) :
        print "The task defintion should a directory"
        os._exit( os.EX_USAGE )
        pass

    a_control_dir = os.path.join( an_options.task_def_dir, "control" )
    if not os.path.isdir( a_control_dir ) :
        print "The task defintion directory should contain 'control' sub directory"
        os._exit( os.EX_USAGE )
        pass

    a_launch_script = os.path.join( a_control_dir, "launch" )
    if not os.path.isfile( a_launch_script ) :
        print "The task definition 'control' sub directory should contain 'launch' start-up script"
        os._exit( os.EX_USAGE )
        pass
        
    if not os.path.isdir( os.path.join( an_options.task_def_dir, "data" ) ) :
        print "The task defintion directory should contain 'data' sub directory"
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_USER = an_options.rackspace_user
    if RACKSPACE_USER == None :
        RACKSPACE_USER = os.getenv( "RACKSPACE_USER" )
        pass


    RACKSPACE_KEY = an_options.rackspace_key
    if RACKSPACE_KEY == None :
        RACKSPACE_KEY = os.getenv( "RACKSPACE_KEY" )
        pass

    import tempfile
    a_working_dir = tempfile.mkdtemp()

    a_target_archive = os.path.join( a_working_dir, "task.tgz" )
    a_tar_command = "cd %s && tar --exclude-vcs -czf %s ./control ./data" % ( an_options.task_def_dir, a_target_archive )

    import os
    print "(%s)" % a_tar_command
    if os.system( a_tar_command ) != 0 :
        print "Can not execute command %s" % a_tar_command
        os._exit( os.EX_USAGE )
        pass

    import os
    os._exit( os.EX_OK )

    pass
