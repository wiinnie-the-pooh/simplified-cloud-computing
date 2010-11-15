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
def fun_division_by_2( fun, the_initial_x, the_finite_x, the_precision, the_count_attempts ):
    # To search optimize value we use "division by 2" method, in each point of we calculate F(x) "the_count_attempts" times and
    # search max F(x) * P(x)  
    # if we inside of the given precision - this is the result
    a_start_x = the_initial_x
    # we mean that in the start point the probability is 100%.
    a_FP_start_x = fun( a_start_x )
    a_cost = a_start_x
    an_end_x = the_finite_x
    a_count_attempts = the_count_attempts
    a_test_x = an_end_x
    
    a_xs = []
    a_x = a_start_x
    a_step = ( an_end_x - a_start_x ) / float( a_count_attempts )
    for an_id in range( a_count_attempts + 1 ) :
        a_xs.append( a_x )
        a_x += a_step
        pass

    print a_step, a_xs

    return


#---------------------------------------------------------------------------------------------
