#!/usr/bin/env python
# encoding: utf-8
"""
EC2config.py

Created by Peter Skomoroch on 2007-04-09.
Copyright (c) 2007 DataWrangling. All rights reserved.
"""

import sys
import os

#replace these with your AWS keys
AWS_ACCESS_KEY_ID = 'YOUR_KEY_ID_HERE'
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_KEY_HERE'
#change this to your keypair name & location (see the EC2 getting started guide tutorial on using ec2-add-keypair)
KEYNAME = "mpi-keypair"
KEY_LOCATION = "/Users/myname/id_rsa-mpi-keypair"
# remove these next two lines when you've updated your credentials.
print "update %s with your AWS credentials" % sys.argv[0]
sys.exit()

# ElasticWulf 64 bit Pycon Images
INSTANCE_TYPE = 'm1.large'  #either 'm1.large', 'm1.xlarge', or 'm1.small' ensure this matches the ami type
MASTER_IMAGE_ID = "ami-e813f681"
IMAGE_ID = "ami-eb13f682"

DEFAULT_CLUSTER_SIZE = 2

# # Amazon Fedora 64 base images...
# INSTANCE_TYPE = 'm1.large'  #either 'm1.large', 'm1.xlarge', or 'm1.small' ensure this matches the ami type
# MASTER_IMAGE_ID = "ami-36ff1a5f"
# IMAGE_ID = "ami-36ff1a5f"

# Old 32 bit images...no NFS, ganglia, etc
# MASTER_IMAGE_ID = "ami-3e836657"
# IMAGE_ID = "ami-3e836657"

