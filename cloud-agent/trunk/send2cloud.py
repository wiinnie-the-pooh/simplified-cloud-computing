#!/usr/bin/env python


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""

#--------------------------------------------------------------------------------------
an_usage = \
"""
%prog \\
      --data-dir=~/rackspace/data \\
      --control-dir=~/rackspace/control \\
      --rackspace-user=${RACKSPACE_USER} \\
      --rackspace-key=${RACKSPACE_KEY}
"""

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--control-dir",
                            metavar = "< location of the task control scripts >",
                            action = "store",
                            dest = "control_dir",
                            help = "(\"%default\", by default)",
                            default = "./control" )

a_option_parser.add_option( "--data-dir",
                            metavar = "< location of the task dedicated data >",
                            action = "store",
                            dest = "data_dir",
                            help = "(\"%default\", by default)",
                            default = None )

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
    a_launch_script = os.path.join( an_options.control_dir, "launch" )
    if os.path.isdir( an_options.control_dir ) == False :
        print "Use --control-dir option to specify scripts to be executed on cloud side"
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

    a_target_archive = os.path.join( a_working_dir, "task.scc" )
    a_tar_command = "tar -czf %s %s" % ( a_target_archive, )
    os.path.isdir( an_options.data_dir )
    import os
    os.system( "tar -czf /tmp/task.scc data control" )

    import os
    os._exit( os.EX_OK )

    pass