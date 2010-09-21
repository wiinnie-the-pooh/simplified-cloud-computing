#!/usr/bin/env python
''' 
ec2-mpi-config.py

Created by Peter Skomoroch on 2007-04-09.
Copyright (c) 2007 DataWrangling. All rights reserved.

'''

import sys
import getopt
import EC2
import os
import commands
import socket
from EC2config import *

help_message = '''
SYNOPSIS
   ec2-mpi-config (ec2-MPI-configuration)
   ec2-mpi-config [-rsh False] 
GENERAL NOTES
   #
DESCRIPTION
    Before running, change the configuration strings in EC2config.py to match your AWS keys

    This script will:

    1. Generate list of your running or pending Elasticwulf node instances on EC2
    2. Select the first node as the master, and scp over the host files to all machines in the MPI cluster
    3. If the master node is still in a "pending" state, the script will sleep and try again until cancelled by the user


    Note: *The ssh variable StrictHostKeyChecking is set to "no". This is an evil hack to avoid the tedious adding of each compute
    node host when managing a large cluster...I'm assuming these EC2 nodes will only connect to eachother and S3, please be careful.

    See http://www.securityfocus.com/infocus/1806
OPTIONS
    #
'''

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value              
                
        configure()
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


def remote(host, cmd='scp',
           user='root', src=None, dest=None,
           credential=None,
           silent=False, test=False):
    d = {
         'cmd':cmd,
         'user':user,
         'src':src,
         'dest':dest,
         'host':host,
         }

    d['switches'] = ''
    if credential:
            d['switches'] = '-i %s' % credential
    
    if cmd == 'scp':
            
        template = '%(cmd)s %(switches)s -o "StrictHostKeyChecking no" %(src)s %(user)s@%(host)s:%(dest)s' 
    else:
        template = 'ssh -o "StrictHostKeyChecking no" %(user)s@%(host)s "%(cmd)s" '

    cmdline = template % d  

    if not silent:
        print "\n",cmdline,"\n\n"
    if not test:
        os.system(cmdline)



def configure():
    import shutil
    conn = EC2.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    instance_response=conn.describe_instances()
    parsed_response=instance_response.parse()  
    mpi_instances=[]
    mpi_amis=[]
    mpi_hostnames=[]
    mpi_externalnames=[]
    machine_state=[]

    for chunk in parsed_response:
        if chunk[0]=='INSTANCE':
            if chunk[-1]=='running' or chunk[-1]=='pending':
                if (chunk[2] == IMAGE_ID) or (chunk[2] == MASTER_IMAGE_ID) :
                    mpi_instances.append(chunk[1])
                    mpi_amis.append(chunk[2])
                    mpi_externalnames.append(chunk[3])  
                    mpi_hostnames.append(chunk[4])                          
                    machine_state.append(chunk[-1])

    # list the nodes
    if len(mpi_instances) > 0:
        print "\n---- MPI Cluster Details ----"
        print "Numer of nodes = %s" % len(mpi_instances)

        for i, machine in enumerate(mpi_instances):
            print "Instance= %s external_name = %s hostname= %s state= %s" %(machine, mpi_externalnames[i], mpi_hostnames[i], machine_state[i])

    master_node = mpi_externalnames[mpi_amis.index(MASTER_IMAGE_ID)]
    print "\nThe master node is %s" % master_node

    master_gmond_file = "gmond_master.conf"
    worker_gmond_file = "gmond_worker.conf"

    # Configure mpd.hosts: write out the hostnames to a mpd.hosts file
    print "\nWriting out mpd.hosts file"
    hosts_file= "mpd.hosts"
    output=open(hosts_file,'w')
    for host in mpi_hostnames:
        print >> output, "%s" % host
    output.close()
    
    homedir = os.path.expanduser( '~' )
    try:
        # check if key already in id_rsa...
        rsakeys = open(homedir + "/.ssh/id_rsa", 'r').read()
        keyfile = open(KEY_LOCATION,'r').read()
        keyval = keyfile.split('-----')[2]
        key_index = rsakeys.split('-----').index(keyval)
        print "Key already in id_rsa..."
    except ValueError:
        # if not, add it...
        print "Appending key to id_rsa..."
        os.system("cat %s >> %s/.ssh/id_rsa" % (KEY_LOCATION, homedir) )
        os.system("chmod 600 %s/.ssh/id_rsa" % homedir)

    # Copy over the EC2 keys and host configuration to all machines in cluster (both /root and /home/lamuser).
    # We scp the amazon private key you created (id_rsa-gsg-keypair or whatever you named it) to the master and 
    # copy it to the compute nodes, opening passwordless ssh between the nodes.
    # Note we are only uploading the EC2 specific key found in KEY_LOCATION (keeping other private keys off the cloud)
    for host in mpi_externalnames:
        remote(host, src=KEY_LOCATION, dest="~/.ssh/id_rsa", credential=KEY_LOCATION)
        remote(host, cmd="touch .ssh/authorized_keys")
        remote(host, cmd="cp -r .ssh /home/lamuser/")
        remote(host, src=hosts_file, dest="/etc/")
        remote(host, src=hosts_file, dest="/home/lamuser/")
        remote(host, cmd="chown -R lamuser:lamuser /home/lamuser")
        #next we upload the default ganglia config files:
        remote(host, src=master_gmond_file, dest="/etc/gmond.conf") 
        remote(host, src=worker_gmond_file, dest="~/gmond.conf")


    # scp over "create_hosts.py" script to master node, then run it on the master node 
    # to construct hosts file with internal AWS names across the cluster
    print "Creating hosts file on master node and copying hosts file to compute nodes..."
    remote(master_node, src="create_hosts.py", dest="/etc/")
    remote(master_node, cmd="python /etc/create_hosts.py")

    # mount nfs home directories
    for host in mpi_externalnames:
        remote(host, cmd="service netfs restart")

    print ""
    print "Configuration complete, ssh into the master node as lamuser and boot the cluster:"
    print "$ ssh lamuser@%s " % master_node
    print "> mpdboot -n %s -f mpd.hosts " % len(mpi_instances)
    print "\n You can check that MPI is working by running the following commands...\n"
    print "> mpdtrace"
    print "> mpiexec -n %s /usr/local/src/mpich2-1.0.6p1/examples/cpi" % len(mpi_instances)
    print "> mpdringtest 100"
    print "> mpiexec -l -n %s hostname\n" % len(mpi_instances)
    print "Test PyMPI: "
    print "> mpirun -np %s pyMPI /home/beowulf/pyMPI-2.4b2/examples/fractal.py\n" % len(mpi_instances)
    print "Test mpi4py: "
    print "> mpiexec -n %s python /home/beowulf/mpi4py-0.5.0/tests/cpi-buf.py\n" % len(mpi_instances) 
    print "\nYou can monitor your cluster performance in your web browser at: \n  http://%s/ganglia" % master_node
    print "\nDirectories /mnt/data and /home/beowulf are NFS mounted on all nodes\n"
    print "For interactive graphical sessions, start x11 on your local machine then ssh in with the following options: "
    print "ssh -2 -C -Y lamuser@%s \n"  % master_node
    print "Once logged in, you can start up ipython: "
    print "[lamuser@ip-12-345-67-89]$ ipython -pylab\n\n"


if __name__ == "__main__":
    sys.exit(main())
