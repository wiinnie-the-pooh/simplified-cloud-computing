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
class TFilterFunctor :
    def __init__( self, the_start, the_end, the_precision = 1.0E-8 ) :
        self._precision = the_precision
        self._start = the_start
        self._end = the_end
        pass

    def __call__( self, the_x ) :
        return ( self._start - the_x ) < self._precision and ( the_x - self._end ) < self._precision
    
    pass


#--------------------------------------------------------------------------------------
def print_dict( the_x2y ) :
    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        pass
    pass


#--------------------------------------------------------------------------------------
def print2_dict( the_sub_xs, the_x2y ) :
    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        if a_x in the_sub_xs :
            print " + ", 
        else:
            print " - ", 
            pass
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        pass
    pass


#--------------------------------------------------------------------------------------
def calc_probability_interval( the_sub_xs, the_x2y ) :
    an_ok_counter = 0
    an_y_integral = 0.0
    a_start_x = the_sub_xs[ 0 ]
    for a_x in the_sub_xs :
        an_y = the_x2y[ a_x ]
        an_y_integral += an_y

        if an_y > 0.0 :
            an_ok_counter += 1
            pass
        pass

    an_average_y_ok = 0
    if an_ok_counter != 0 :
        an_average_y_ok = an_y_integral / float( an_ok_counter )
        pass

    an_average_y_all = an_y_integral / float( len( the_sub_xs ) )
    a_probability_interval = an_average_y_all / an_average_y_ok
    print "probability interval : %0.3f" % a_probability_interval

    return a_probability_interval


#--------------------------------------------------------------------------------------
def sub_algo( the_x2y, the_cost, the_fun, the_start_x, the_end_x, the_probability_interval, the_count_attempts ) :
    an_end_x = the_start_x + ( the_end_x - the_start_x ) * the_probability_interval
    a_sub_xs = filter( TFilterFunctor( the_start_x, an_end_x ), the_x2y.keys() )
    an_additional_attempts = max( the_count_attempts + 1 - len( a_sub_xs ), 1 )

    a_x = an_end_x
    a_step = ( an_end_x - the_start_x ) / float( an_additional_attempts + 1 )
    print "additional attempts : ",
    for an_id in range( an_additional_attempts ) :
        a_sub_xs.append( a_x )
        an_y = the_fun( a_x )
        the_x2y[ a_x ] = an_y
        print "%4d" % a_x,
        the_cost += a_x
        a_x -= a_step
        pass
    print

    a_probability_interval = calc_probability_interval( a_sub_xs, the_x2y )

    print2_dict( a_sub_xs, the_x2y )
    print "cost - %4d\n" % the_cost

    return the_x2y, the_cost, an_end_x, a_probability_interval


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_initial_x, the_finite_x, the_precision, the_count_attempts ):
    # To search optimize value we use "division by 2" method, in each point of we calculate F(x) "the_count_attempts" times and
    # search max F(x) * P(x)  
    # if we inside of the given precision - this is the result
    a_start_x = the_initial_x
    a_cost = a_start_x
    an_end_x = the_finite_x
    a_count_attempts = the_count_attempts
    a_test_x = an_end_x
    
    a_x2y = {}
    a_x = an_end_x
    a_step = ( an_end_x - a_start_x ) / float( a_count_attempts )
    for an_id in range( a_count_attempts + 1 ) :
        an_y = the_fun( a_x )
        a_x2y[ a_x ] = an_y
        a_cost += a_x
        a_x -= a_step
        pass

    print2_dict( a_x2y.keys(), a_x2y )

    a_probability_interval = calc_probability_interval( a_x2y.keys(), a_x2y )
    print "cost - %4d\n" % a_cost


    #-----------------------------------------------------------------------------------------
    while ( 1.00 - a_probability_interval ) > float( the_precision / 100.0 )  :
        a_x2y, a_cost, an_end_x, a_probability_interval = sub_algo( a_x2y, a_cost, the_fun, a_start_x, an_end_x, 
                                                                    a_probability_interval, a_count_attempts )    
        pass

    return


#---------------------------------------------------------------------------------------------
