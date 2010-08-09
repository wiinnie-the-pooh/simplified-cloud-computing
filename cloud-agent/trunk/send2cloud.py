#!/usr/bin/env python

#--------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import sys, os, os.path, uuid
import balloon.rackspace as rackspace
import balloon.amazon as amazon


#--------------------------------------------------------------------------------------
# Define command line interface

an_usage_description = "%prog --task-def-dir=~/rackspace"
an_usage_description += rackspace.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--debug",
                            action = "store_true",
                            dest = "enable_debug",
                            help = "print debug information",
                            default = True )

a_option_parser.add_option( "--task-def-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "task_def_dir",
                            help = "(\"%default\", by default)",
                            default = "." )

rackspace.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    

#--------------------------------------------------------------------------------------
if __name__ == '__main__' :
    an_options, an_args = a_option_parser.parse_args()

    # Check command line arguments first
    #---------------------------------------------------------------------------
    an_is_debug = an_options.enable_debug


    #---------------------------------------------------------------------------
    def print_d( the_message ) :
        if an_is_debug : 
            sys.stderr.write( the_message )
            pass

        pass


    #---------------------------------------------------------------------------
    def print_e( the_message ) :
        sys.stderr.write( the_message )

        pass


    #---------------------------------------------------------------------------
    def run_command( the_command ) :
        print_d( "(%s)\n" % the_command )
        
        if os.system( the_command ) != 0 :
            print_e( "Can not execute command %s\n" % the_command )
            os._exit( os.EX_USAGE )
            pass
        
        pass


    #---------------------------------------------------------------------------
    def ssh_command( the_ssh_client, the_command ) :
        print_d( "[%s]\n" % the_command )
        
        stdin, stdout, stderr = the_ssh_client.exec_command( the_command )
        
        for a_line in stderr.readlines() : print_d( "\t%s" % a_line )
        for a_line in stdout.readlines() : print_d( "\t%s" % a_line )
        
        pass


    #---------------------------------------------------------------------------
    import os.path
    an_options.task_def_dir = os.path.abspath( an_options.task_def_dir )
    if not os.path.isdir( an_options.task_def_dir ) :
        print_e( "The task defintion should a directory\n" )
        os._exit( os.EX_USAGE )
        pass

    a_control_dir = os.path.join( an_options.task_def_dir, "control" )
    if not os.path.isdir( a_control_dir ) :
        print_e( "The task defintion directory should contain 'control' sub directory\n" )
        os._exit( os.EX_USAGE )
        pass

    a_launch_script = os.path.join( a_control_dir, "launch" )
    if not os.path.isfile( a_launch_script ) :
        print_e( "The task definition 'control' sub directory should contain 'launch' start-up script\n" )
        os._exit( os.EX_USAGE )
        pass
        
    if not os.path.isdir( os.path.join( an_options.task_def_dir, "data" ) ) :
        print_e( "The task defintion directory should contain 'data' sub directory\n" )
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


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
    # a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-paramiko" ) )
    # a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-libcloud" ) )
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
