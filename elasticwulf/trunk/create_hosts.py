#!/usr/bin/env python
# encoding: utf-8
"""
create_hosts.py

run as root on Master node.

Created by Peter Skomoroch on 2007-07-23.
Copyright (c) 2007 DataWrangling. All rights reserved.
"""

import sys
import os
import socket
import time

RSH_ENABLED = False
# rsh configuration option.. since rsh is a security risk it will be off by default
# this is only available for benchmarking or legacy programs which require it
#
# For details see https://www.middleware.georgetown.edu/confluence/display/HPCT/Stage+1+~+Master+Prep
# also http://blizzard.rwic.und.edu/~nordlie/deuce/
# and http://www.cs.hofstra.edu/~cscccl/csc145/setup.txt


def main():
    # read the internal domain names listed in mpd.hosts to construct /etc/hosts
    name_file = open("/etc/mpd.hosts", 'r')
    h_output=open("/etc/hosts",'w') 
    root_rhosts_output=open("temp_root_rhosts",'w')
    lamuser_rhosts_output=open("temp_lamuser_rhosts",'w')       
    
    #For python c3 cluster management tools,  http://www.csm.ornl.gov/torc/C3/
    c3_output = open("/etc/c3.conf","w")
    
    #for NFS security   
    worker_ips =[]
    master_ip = ' '
    
    # setting up an nfs export mask is not going to work properly.
    # This is tripped me up on EC2 until I realized the subnet is highly dynamic, it could be 10.254, 13.255, etc. so
    # we need to always construct the explicit list of cluster ips
    # see: http://developer.amazonwebservices.com/connect/thread.jspa?messageID=43418&#43418
    #
    # "Note that launching a number of instances in the same group, however, has no bearing on whether 
    # the instances really are on the same IP subnet."
    #
    # so we either need blanket access for *.compute-1.internal or we need to 
    # enumerate each client machine (more secure), i.e. something like:
    # /home        192.168.0.1(rw) 192.168.0.2(rw)
    
    export_string = ' '
    export_template = ' %s(rw,sync,no_root_squash)'
    workernames=[]
    
    for i, line in enumerate(name_file.readlines()):
        host = line.strip()
        #host example: domU-12-31-35-00-1C-A4.z-2.compute-1.internal
        ip = socket.gethostbyname(host)     
        shortname = host.split('.')[0]
        print host

        if i == 0:
            print >> h_output, "# Do not remove the following line or programs that require network functionality will fail"
            print >> h_output, "%s %s %s master" % (ip, host, shortname)    
            print >> h_output, "127.0.0.1 localhost.localdomain localhost"  
            print >> h_output, ""
            print >> h_output, "# Compute Nodes"    
            print >> c3_output, "cluster ec2wulf {"
            print >> c3_output, "       master"
            print >> c3_output, "       dead remove_line_for_0-indexing"        
            print >> root_rhosts_output, "master root"
            print >> lamuser_rhosts_output, "master lamuser"                        

            master_ip = ip
                        
        else:
            workernames.append(host)
            print >> h_output, "%s %s %s node%s" % (ip, host, shortname, str(i))    
            print >> c3_output, "       node%s" %  str(i)       
            print >> root_rhosts_output, "node%s root" % str(i)
            print >> lamuser_rhosts_output, "node%s lamuser" % str(i)                                       
            export_string +=  export_template % ip
            worker_ips.append(ip)
            
    print >> c3_output, "}"
    h_output.close()
    root_rhosts_output.close()
    lamuser_rhosts_output.close()
    
    # more nfs configuration
    os.system('mkdir -p /mnt/data') 
    os.system('chown -R lamuser:lamuser /mnt/data')
    
    out_exp=open('/etc/exports', 'w')
    print >> out_exp, "/home/beowulf     " + export_string
    print >> out_exp, "/mnt/data     " + export_string
        
    out_exp.close() 
    time.sleep(1)       
    os.system('exportfs -rv' )  
    
    #copy hosts file to lamuser directory
    os.system('cp /etc/hosts /home/lamuser/' )
    os.system("chown -R lamuser:lamuser /home/lamuser") 
    
    if RSH_ENABLED: 
        os.system('cp /etc/hosts /etc/hosts.equiv' )
        os.system('cp temp_root_rhosts .rhosts' )
        os.system('cp temp_lamuser_rhosts /home/lamuser/.rhosts' )          
        os.system('chown -R lamuser:lamuser /home/lamuser' )        
        
    for host in workernames:
        #send a copy of the hosts file to each of the compute nodes...
        os.system('scp -o "StrictHostKeyChecking no" /etc/hosts root@%s:/etc/' %  host )
        os.system('scp -o "StrictHostKeyChecking no" /etc/hosts lamuser@%s:/home/lamuser/' %  host )
        
        #scp over default ganglia gmond.conf file to workers...
        os.system('scp -o "StrictHostKeyChecking no" ~/gmond.conf root@%s:/etc/' %  host )      

        # nfs data mounts
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "mkdir -p /mnt/data"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chown -R lamuser:lamuser /mnt/data"' % host)      
        
        # rsh config
        if RSH_ENABLED: 
            os.system('scp -o "StrictHostKeyChecking no" /etc/hosts.equiv root@%s:/etc/' %  host )
            os.system('scp -o "StrictHostKeyChecking no" temp_root_rhosts root@%s:.rhosts' %  host )            
            os.system('scp -o "StrictHostKeyChecking no" temp_lamuser_rhosts lamuser@%s:/home/lamuser/.rhosts' %  host )        
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "chown -R lamuser:lamuser /home/lamuser"' % host)          

   ###########################  
    # NFS security configuration...
    # we need a dynamically generated list of hosts for hosts.allow
    # i.e. portmap: 192.168.0.1 , 192.168.0.2
    hosts_allow_output = open("/etc/hosts.allow","w")
     
    allow_services = ["portmap", "lockd", "mountd", "rquotad", "statd" ]
    if RSH_ENABLED:
        allow_services = ["portmap", "lockd", "mountd", "rquotad", "statd","rsh","rlogin","rexec" ]
     
    for service in allow_services:
        print >> hosts_allow_output, "%s: %s" % ( service,  ", ".join(worker_ips) )
    
    os.system('service portmap restart')
    os.system('service nfs restart')

    os.system('chkconfig portmap off')
    os.system('chkconfig nfs off')
    os.system('chkconfig nfslock off')

    #Ganglia config
    os.system('chkconfig --level 345 gmond on')
    os.system('chkconfig --level 345 gmetad on')

    os.system('service gmond restart')
    os.system('service gmetad restart')

    os.system('chkconfig httpd on')
    os.system('apachectl restart')  
    
    # At this point, you should be able to see the admin interface on your master node address
    # which is something like: http://ec2-67-202-59-237.compute-1.amazonaws.com/ganglia/
    # You can change the cluster name and monitoring config in /etc/gmond.conf on the master node....

    os.system('chkconfig  --level 345 portmap on')
    os.system('chkconfig  --level 345 nfs on')
    os.system('chkconfig  --level 345 nfslock on')  

    if RSH_ENABLED:
        os.system('chkconfig rexec on')         
        os.system('chkconfig rsh on')   
        os.system('chkconfig rlogin on')    
        os.system('service xinetd restart')                         
        os.system('in.rshd start')
        
    client_hosts_output = open("client_hosts_allow","w") 
    for service in allow_services:
        print >> client_hosts_output, "%s: %s" % ( service, master_ip ) 
    client_hosts_output.close()

    for host in workernames:        
        os.system('scp -o "StrictHostKeyChecking no" ~/client_hosts_allow root@%s:/etc/hosts.allow' %  host )
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "service portmap restart"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "service nfs restart"' % host)     
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "service nfslock restart"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig portmap off"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig nfs off"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig nfslock off"' % host)   
        
        #for ganglia monitoring
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig --level 345 gmond on"' % host)
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "service gmond restart"' % host)                   
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig  --level 345 portmap on"' % host)   
        os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig  --level 345 nfslock on"' % host)               

        if RSH_ENABLED:     
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig rexec on"' % host)          
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig rsh on"' % host)    
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "chkconfig rlogin on"' % host) 
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "service xinetd restart"' % host)                          
            os.system('ssh -o "StrictHostKeyChecking no" root@%s "in.rshd start"' % host)               
        
if __name__ == '__main__':
    main()

