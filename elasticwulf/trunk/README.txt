DataWrangling ElasticWulf cluster configuration scripts v 1.6

3/17/08
------------------------------------
* now supports 64 bit large and extra large AMI types
* NFS mounted /home/beowulf and /mnt/data directories visible on workers
* Ganglia web monitoring on master node configured on launch
* Handles launch of separate master and worker image types
* openmpi, lam, mpich1, mpich2 installed
* Twisted, mpi4py, Ipython1 installed and configured
* boto available on images for S3 data access
* Xwindows installed on master node
* TODO: modify code to use subprocess instead of os.system calls
* TODO: fix start-cluster command line option parsing (not working..need to use config file to modify params)
* TODO: modify management code to use boto instead of EC2 sample library
* TODO: add option to update Ipython1 egg during configuration
* TODO: add pdsh (parallel distributed shell) for cluster management
* TODO: add hadoop cluster filesystem (HDFS) and python bindings? 

------------------------------------
7/24/07

changes:

* fixed lamuser home directory permissions bug
* fixed section of ec2-mpi-config.py which clobbered existing rsa keys on the client machine
* updated calls of AWS python EC2 library to use API version 2007-01-19
http://developer.amazonwebservices.com/connect/entry.jspa?externalID=552&categoryID=85
* fixed mpdboot issue by using amazon internal DNS names in hosts files
* scripts should now work on windows/cygwin client environments


-------------------------------------

The code in this directory is used to manage the Sample Fedora Core 6 + MPICH2 + Numpy/PyMPI compute node public image on Amazon EC2

see the following blog posts for more info and detailed instructions:

http://www.datawrangling.com/on-demand-mpi-cluster-with-python-and-ec2-part-1-of-3.html
http://www.datawrangling.com/mpi-cluster-with-python-and-amazon-ec2-part-2-of-3.html


The process is pretty simple once you have an Amazon EC2 account and keys, just download the Python scripts and you can be running a compute cluster in a few minutes. 

Prerequisites:

   1. Get a valid Amazon EC2 account
   2. Complete the “getting started guide” tutorial on Amazon EC2 and create all needed web service accounts, authorizations, and keypairs
   3. Download and install the Amazon EC2 Python library
   4. Download the Amazon EC2 MPI cluster management scripts



