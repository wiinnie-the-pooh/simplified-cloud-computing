#!/usr/bin/env python


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import os, os.path, uuid


#--------------------------------------------------------------------------------------
an_usage = \
"""
%prog \\
      --task-def-dir=~/rackspace \\
      --rackspace-user=${RACKSPACE_USER} \\
      --rackspace-key=${RACKSPACE_KEY} \\
      --aws-access-key-id=${AWS_ACCESS_KEY_ID} \\
      --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}

"""

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--pipe",
                            action = "store_true",
                            help = "prints only 'container name' as its output",
                            dest = "enable_pipe",
                            default = False )

a_option_parser.add_option( "--task-def-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "task_def_dir",
                            help = "(\"%default\", by default)",
                            default = "." )

a_option_parser.add_option( "--rackspace-user",
                            metavar = "< Rackspace user >",
                            action = "store",
                            dest = "rackspace_user",
                            help = "(${RACKSPACE_USER}, by default)",
                            default = os.getenv( "RACKSPACE_USER" ) )
    
a_option_parser.add_option( "--rackspace-key",
                            metavar = "< Rackspace key >",
                            action = "store",
                            dest = "rackspace_key",
                            help = "(${RACKSPACE_KEY}, by default)",
                            default = os.getenv( "RACKSPACE_KEY" ) )
    
a_option_parser.add_option( "--aws-access-key-id",
                            metavar = "< Amazon key id >",
                            action = "store",
                            dest = "aws_access_key_id",
                            help = "(${AWS_ACCESS_KEY_ID}, by default)",
                            default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
a_option_parser.add_option( "--aws-secret-access-key",
                            metavar = "< Amazon secret key >",
                            action = "store",
                            dest = "aws_secret_access_key",
                            help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                            default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    

#--------------------------------------------------------------------------------------
if __name__ == '__main__' :
    an_options, an_args = a_option_parser.parse_args()

    # Check command line arguments first
    #---------------------------------------------------------------------------
    an_is_debug = not an_options.enable_pipe


    #---------------------------------------------------------------------------
    def print_d( the_message ) :
        if an_is_debug : 
            print the_message,
            pass

        pass


    #---------------------------------------------------------------------------
    def run_command( the_command ) :
        if an_is_debug : 
            print "(%s)" % the_command
            pass
        
        import os
        if os.system( the_command ) != 0 :
            print "Can not execute command %s" % the_command
            os._exit( os.EX_USAGE )
            pass
        
        pass


    #---------------------------------------------------------------------------
    def ssh_command( the_ssh_client, the_command ) :
        if an_is_debug : 
            print "[%s]" % the_command
            pass
        
        stdin, stdout, stderr = the_ssh_client.exec_command( the_command )
        
        if an_is_debug : 
            for a_line in stderr.readlines() : print "\t", a_line,
            for a_line in stdout.readlines() : print "\t", a_line,
            pass
        
        pass


    #---------------------------------------------------------------------------
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
        print "Define RACKSPACE_USER parameter through '--rackspace-user' option"
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_KEY = an_options.rackspace_key
    if RACKSPACE_KEY == None :
        print "Define RACKSPACE_KEY parameter through '--rackspace-key' option"
        os._exit( os.EX_USAGE )
        pass

    AWS_ACCESS_KEY_ID = an_options.aws_access_key_id
    if AWS_ACCESS_KEY_ID == None :
        print "Define AWS_ACCESS_KEY_ID parameter through '--aws-access-key-id' option"
        os._exit( os.EX_USAGE )
        pass

    AWS_SECRET_ACCESS_KEY = an_options.aws_secret_access_key
    if AWS_SECRET_ACCESS_KEY == None :
        print "Define AWS_SECRET_ACCESS_KEY parameter through '--aws-secret-access-key' option"
        os._exit( os.EX_USAGE )
        pass


    #---------------------------------------------------------------------------
    # Packaging of the local data
    import os, tempfile
    a_working_dir = tempfile.mkdtemp()
    print_d( "a_working_dir = %s\n" % a_working_dir )

    a_control_name = "task_control.tgz"
    a_control_archive = os.path.join( a_working_dir, a_control_name )
    run_command( "cd %s && tar --exclude-vcs -czf %s ./control" % ( an_options.task_def_dir, a_control_archive ) )

    a_data_name = "task_data.tgz"
    a_data_archive = os.path.join( a_working_dir, a_data_name )
    run_command( "cd %s && tar --exclude-vcs -czf %s ./data" % ( an_options.task_def_dir, a_data_archive ) )


    #---------------------------------------------------------------------------
    # To upload the task into cloud
    import cloudfiles
    a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
    print_d( "a_cloudfiles_conn = %r\n" % a_cloudfiles_conn )

    a_container_name = str( uuid.uuid4() )
    a_cloudfiles_container = a_cloudfiles_conn.create_container( a_container_name )
    print_d( "a_cloudfiles_container = %r\n" % a_cloudfiles_container )

    a_file_object = a_cloudfiles_container.create_object( a_data_name )
    a_file_object.load_from_filename( a_data_archive )
    print_d( "a_file_object = %r\n" % a_file_object )


    #---------------------------------------------------------------------------
    # To boot a node in cloud
    from libcloud.types import Provider 
    from libcloud.providers import get_driver 
    
    Driver = get_driver( Provider.RACKSPACE ) 
    a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
    print_d( "a_libcloud_conn = %r\n" % a_libcloud_conn )

    an_images = a_libcloud_conn.list_images() 
    print_d( "an_images = %r\n" % an_images )

    a_sizes = a_libcloud_conn.list_sizes() 
    print_d( "a_sizes = %r\n" % a_sizes )

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

    a_node_name = a_container_name
    a_node = a_libcloud_conn.deploy_node( name = a_node_name, image = an_images[ 9 ] , size = a_sizes[ 0 ], deploy = a_msd ) 
    print_d( "a_node = %r\n" % a_node )


    #---------------------------------------------------------------------------
    import paramiko
    a_ssh_client = paramiko.SSHClient()
    a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    a_ssh_client.connect( hostname = a_node.public_ip[ 0 ], port = 22, username = 'root')
    ssh_command( a_ssh_client, 'mkdir %s' % a_working_dir )

    a_sftp_client = a_ssh_client.open_sftp()
    a_sftp_client.put( a_control_archive, a_control_archive )

    a_command = 'cd %s && tar -xzf %s' % ( a_working_dir, a_control_name )
    ssh_command( a_ssh_client, a_command )

    a_command = '%s/control/launch' % ( a_working_dir ) 
    a_command += " --container-name='%s'" % a_container_name
    a_command += " --data-name='%s'" % a_data_name
    a_command += " --working-dir='%s'" % a_working_dir
    a_command += " --rackspace-user='%s'" % RACKSPACE_USER
    a_command += " --rackspace-key='%s'" % RACKSPACE_KEY
    a_command += " --aws-access-key-id='%s'" % AWS_ACCESS_KEY_ID
    a_command += " --aws-secret-access-key='%s'" % AWS_SECRET_ACCESS_KEY
    ssh_command( a_ssh_client, a_command )


    #---------------------------------------------------------------------------
    import shutil
    shutil.rmtree( a_working_dir )


    #---------------------------------------------------------------------------
    # This refenrece value could be used further in cloud management pipeline
    print a_container_name


    #---------------------------------------------------------------------------
    pass


#--------------------------------------------------------------------------------------
