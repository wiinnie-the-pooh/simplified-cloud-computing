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
    a_end_x = the_finite_x
    count_attempts = the_count_attempts
    a_test_x = a_end_x
    print "-----------------------------------------------------------------------------"
    print "                          Calculating optimize value"
    print "-----------------------------------------------------------------------------"
    print " N  \t Initial \t F(x)*P(x) \t Finite \t Test \t   F(x)*P(x) "
    print "iter\t    x    \t           \t    x   \t   x  \t             "
    print "-----------------------------------------------------------------------------"
    an_iter_num = 0
    while float( a_end_x - a_start_x ) / a_start_x > float( the_precision ) / float( 100 ) :
        print "%2d" %an_iter_num, 
        print " \t %4d " %a_start_x,
        print " \t  %4.0f " % a_FP_start_x,
        a_count_crash = 0
        a_summ_fun_x = 0
        for i in range( 0, count_attempts ):
           an_attempt = fun( a_test_x )
           a_cost = a_cost + a_test_x
           a_summ_fun_x += an_attempt
           if an_attempt == 0:
              a_count_crash += 1
              pass
           pass
        a_probability_test_x = 1 - float( a_count_crash ) / float( count_attempts )
        if a_count_crash == count_attempts:
           an_average_fun_test_x = 0
           pass
        else:
           an_average_fun_test_x = a_summ_fun_x / ( count_attempts - a_count_crash )
           pass
        a_FP_test_x = an_average_fun_test_x * a_probability_test_x

        print " \t %4d " %a_end_x,
        print " \t %4d " %a_test_x,
        print " \t%4.0f" % a_FP_test_x

        if a_FP_test_x > a_FP_start_x :
           a_start_x = a_test_x
           a_FP_start_x = a_FP_test_x
           pass
        else:
           a_end_x = a_test_x 
           pass
        a_test_x = a_start_x + float( a_end_x - a_start_x ) / float( 2 )
        an_optimize_x = a_start_x
        an_iter_num += 1
        pass
        
    print "-----------------------------------------------------------------------------"
    print "The optimize value is ", an_optimize_x
    print "The cost is ", a_cost
    return an_optimize_x
   

#---------------------------------------------------------------------------------------------
