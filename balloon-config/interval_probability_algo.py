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
def fun_division_by_2( the_fun, the_initial_x, the_finite_x, the_precision, the_count_attempts ):
    # To search optimize value we use "division by 2" method, in each point of we calculate F(x) "the_count_attempts" times and
    # search max F(x) * P(x)  
    # if we inside of the given precision - this is the result
    a_start_x = the_initial_x
    a_cost = a_start_x
    an_end_x = the_finite_x
    a_count_attempts = the_count_attempts
    a_test_x = an_end_x
    
    a_xs = []
    a_x2y = {}
    a_x = a_start_x
    an_ok_counter = 0
    a_fun_sum_all = 1
    a_step = ( an_end_x - a_start_x ) / float( a_count_attempts )
    for an_id in range( a_count_attempts + 1 ) :
        a_xs.append( a_x )
        an_y = the_fun( a_x )
        a_x2y[ a_x ] = an_y
        a_fun_sum_all += an_y
        if an_y > 0.0 :
            an_ok_counter += 1
            pass
        a_x += a_step
        pass

    an_average_fun_ok = a_fun_sum_all / float( an_ok_counter )
    an_average_fun_all = a_fun_sum_all / float( a_count_attempts + 1 )
    a_probability_interval = an_average_fun_all / an_average_fun_ok
    print a_step, an_average_fun_ok, an_average_fun_all, a_probability_interval
    print a_xs
    print a_x2y
    
    an_end_x = a_start_x + ( an_end_x - a_start_x ) * a_probability_interval
    print an_end_x

    return


#---------------------------------------------------------------------------------------------
