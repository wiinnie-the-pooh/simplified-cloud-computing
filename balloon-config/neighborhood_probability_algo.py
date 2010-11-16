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
    a_counter = 1
    an_y_integral = 0.0

    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        an_y_integral += the_x2y[ a_x ]
        if a_x in the_sub_xs :
            print " + ", 
        else:
            print " - ", 
            pass
        print "%4d : %4.0f [ %4.0f ]" % ( a_x, the_x2y[ a_x ], an_y_integral / float( a_counter ) )
        a_counter += 1
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

    print2_dict( a_sub_xs, the_x2y )

    a_probability_interval = calc_probability_interval( a_sub_xs, the_x2y )
    print "cost : %4d\n" % the_cost

    return the_x2y, the_cost, an_end_x, a_probability_interval


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_initial_x, the_finite_x, the_precision, the_nb_attempts ) :
    """ """
    a_center_x = ( the_finite_x - the_initial_x ) / 2.0
    a_region_x = ( the_finite_x - the_initial_x ) / 4.0

    a_start_x = a_center_x - a_region_x / 2.0
    an_end_x = a_center_x + a_region_x / 2.0

    a_nb_attempts = the_nb_attempts
    a_cost = 0.0
    
    a_x2y = {}
    a_x = an_end_x
    a_step = ( an_end_x - a_start_x ) / float( a_nb_attempts )
    for an_id in range( a_nb_attempts + 1 ) :
        an_y = the_fun( a_x )
        a_x2y[ a_x ] = an_y
        a_cost += a_x
        a_x -= a_step
        pass

    print2_dict( a_x2y.keys(), a_x2y )
    print "cost : %4d\n" % a_cost

    a_sub_nb_attempts = a_nb_attempts / 2
    a_sub2_nb_attempts = a_sub_nb_attempts / 2

    an_average_y = {}
    a_xs = a_x2y.keys()
    a_xs.sort()
    for an_id in range( len( a_xs ) ) :
        a_middle_x = a_x = a_xs[ an_id ]
        an_y = a_x2y[ a_x ]

        a_neighbor_nb_attemps = 0

        print "[", 
        if an_id < a_sub2_nb_attempts :
            a_neighbor_nb_attemps += an_id
            for a_sub_id in range( an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += a_x2y[ a_x ]
                print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += a_sub2_nb_attempts
            for a_sub_id in range( an_id - a_sub2_nb_attempts, an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += a_x2y[ a_x ]
                print "%4d" % a_x,
                pass
            pass

        print "| %4d |" % a_middle_x,

        if a_nb_attempts - an_id < a_sub2_nb_attempts :
            a_neighbor_nb_attemps += a_nb_attempts - an_id
            for a_sub_id in range( an_id, a_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += a_x2y[ a_x ]
                print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += a_sub2_nb_attempts
            for a_sub_id in range( an_id, an_id + a_sub2_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += a_x2y[ a_x ]
                print "%4d" % a_x, 
                pass
            pass
        an_average_y[ a_middle_x ] = an_y / a_neighbor_nb_attemps
        print "] = %4d" % an_average_y[ a_middle_x ]

        pass

    return None, a_cost


#---------------------------------------------------------------------------------------------
