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

    an_archive_name = "task_input.tgz"
    a_target_archive = os.path.join( a_working_dir, an_archive_name )
    a_tar_command = "cd %s && tar --exclude-vcs -czf %s ./control ./data" % ( an_options.task_def_dir, a_target_archive )

    import os
    print "(%s)" % a_tar_command
    if os.system( a_tar_command ) != 0 :
        print "Can not execute command %s" % a_tar_command
        os._exit( os.EX_USAGE )
        pass


    #---------------------------------------------------------------------------
    # To upload the task into cloud
    import cloudfiles
    a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
    a_container_name = os.path.basename( a_working_dir )
    a_cloudfiles_container = a_cloudfiles_conn.create_container( a_container_name )
    a_file_object = a_cloudfiles_container.create_object( an_archive_name )
    a_file_object.load_from_filename( a_target_archive )


    #---------------------------------------------------------------------------
    # To boot a node in cloud
    from libcloud.types import Provider 
    from libcloud.providers import get_driver 
    
    Driver = get_driver( Provider.RACKSPACE ) 
    a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 

    images = a_libcloud_conn.list_images() 
    sizes = a_libcloud_conn.list_sizes() 

    a_deployment_steps = []
    from libcloud.deployment import MultiStepDeployment, ScriptDeployment, SSHKeyDeployment
    a_deployment_steps.append( SSHKeyDeployment( open( os.path.expanduser( "~/.ssh/id_rsa.pub") ).read() ) )
    a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-boto" ) )
    a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-paramiko" ) )
    a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-libcloud" ) )
    a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-software-properties" ) )
    a_deployment_steps.append( ScriptDeployment( "add-apt-repository ppa:chmouel/rackspace-cloud-files" ) )
    a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-rackspace-cloudfiles" ) )

    a_msd = MultiStepDeployment( a_deployment_steps ) 
    a_node_name = os.path.basename( a_working_dir )
    a_node = a_libcloud_conn.deploy_node( name = a_node_name, image = images[ 9 ] , size = sizes[ 0 ], deploy = a_msd ) 
    print "a_node.public_ip[ 0 ] = '%s'" % a_node.public_ip[ 0 ]

    #---------------------------------------------------------------------------
    import paramiko
    a_ssh_client = paramiko.SSHClient()
    a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    a_ssh_client.connect( hostname = a_node.public_ip[ 0 ], port = 22, username = 'root')
    stdin, stdout, stderr = a_ssh_client.exec_command( 'mkdir %s' % a_working_dir )

    a_sftp_client = a_ssh_client.open_sftp()
    a_sftp_client.put( a_target_archive, a_target_archive )

    a_command = 'cd %s && tar -xzf %s' % ( a_working_dir, an_archive_name )
    stdin, stdout, stderr = a_ssh_client.exec_command( a_command )

    a_command = '%s/control/launch %s %s %s' % ( a_working_dir, RACKSPACE_USER, RACKSPACE_KEY, a_container_name )
    stdin, stdout, stderr = a_ssh_client.exec_command( a_command )
    for a_line in stderr.readlines() : print a_line,
    for a_line in stdout.readlines() : print a_line,


    #---------------------------------------------------------------------------
    # a_cloudfiles_conn.delete_container( a_cloudfiles_container )
    # a_node.destroy()

    import shutil
    # shutil.rmtree( a_working_dir )

    import os
    print "OK"
    os._exit( os.EX_OK )

    pass


#--------------------------------------------------------------------------------------
