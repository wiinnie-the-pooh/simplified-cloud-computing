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
##
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
from neighborhood_probability_algo import print2_dict
from balloon.common import WorkerPool, Timer


#--------------------------------------------------------------------------------------
def update_x2y( the_fun, the_x2y, the_x ) :
    the_x2y[ the_x ] = the_fun( the_x )
    pass


#--------------------------------------------------------------------------------------
def get_stats( the_fun, the_x2y, the_cost, the_center_x, the_region_x, the_nb_attempts ) :
    an_end_x = the_center_x + the_region_x / 2.0
    a_start_x = the_center_x - the_region_x / 2.0

    a_region_x = the_region_x
    if a_start_x < 1.0 : # The special Amazon workaround
        a_start_x = 1000.0
        a_region_x = ( an_end_x - a_start_x ) / 2.0
        pass

    print "[ %4d - %4d ] : " % ( a_start_x, an_end_x )

    a_worker_pool = WorkerPool( the_nb_attempts )

    a_sub_xs = []
    a_x = an_end_x
    a_step = a_region_x / float( the_nb_attempts )
    for an_id in range( the_nb_attempts + 1 ) :
        if not the_x2y.has_key( a_x ) : 
            # a_worker_pool.charge( update_x2y, ( the_fun, the_x2y, a_x ) )
            update_x2y( the_fun, the_x2y, a_x )
            a_sub_xs.append( a_x )
            the_cost += a_x
            pass
        a_x -= a_step
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()

    print2_dict( a_sub_xs, the_x2y )
    print "cost : %4d\n" % the_cost

    return the_x2y, the_cost, a_region_x


#--------------------------------------------------------------------------------------
from real import create_boto_config
a_boto_config, a_saved_environ = create_boto_config()

from real_option_parser import main
a_region, a_logsuffix, an_initial_size, an_end_size, a_precision, a_nb_attempts = main()

from real import try_upload
an_engine = try_upload( a_region, a_logsuffix )
   
a_center_x = ( an_end_size + an_initial_size ) / 2.0
a_region_x = ( an_end_size - an_initial_size ) / 4.0

a_spent_time = Timer()

import neighborhood_probability_algo
an_optimize_x, a_cost = neighborhood_probability_algo.entry_point( an_engine, a_center_x, a_region_x, a_precision, a_nb_attempts, get_stats )

print "a_spent_time = %s, sec\n" % a_spent_time

from real import restore_environ
restore_environ( a_saved_environ, a_boto_config )


#--------------------------------------------------------------------------------------
