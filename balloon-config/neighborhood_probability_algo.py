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
        if a_x in the_sub_xs :
            print " + ", 
        else:
            print " - ", 
            pass
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        a_counter += 1
        pass
    pass


#--------------------------------------------------------------------------------------
def find_center( the_x2y, the_sub2_nb_attempts ) :
    an_average_y = {}

    a_xs = the_x2y.keys()
    a_nb_attempts = len( a_xs )

    a_xs.sort()
    for an_id in range( a_nb_attempts ) :
        a_center_x = a_x = a_xs[ an_id ]
        an_y = the_x2y[ a_x ]

        a_neighbor_nb_attemps = 0

        # print "[", 
        if an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += an_id
            for a_sub_id in range( an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id - the_sub2_nb_attempts, an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass

        # print "| %4d |" % a_center_x,

        if a_nb_attempts - an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += a_nb_attempts - an_id
            for a_sub_id in range( an_id, a_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id, an_id + the_sub2_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x, 
                pass
            pass
        an_average_y[ a_center_x ] = an_y / a_neighbor_nb_attemps
        # print "] = %4d" % an_average_y[ a_center_x ]

        pass

    #------------------------------------------------------------------------------------------
    # Finding out the best interval based on the corresponding average values
    a_max_average_y = 0.0
    an_average_y_index = 0
    for an_id in range( len( a_xs ) ) :
        a_x = a_xs[ an_id ]
        an_y = an_average_y[ a_x ]

        if an_y > a_max_average_y :
            an_average_y_index = an_id
            a_max_average_y = an_y
            pass

        pass

    a_center_x = a_xs[ an_average_y_index ]

    #------------------------------------------------------------------------------------------
    # Shift the 'center' to avoid mesurement of the same points
    if an_average_y_index == 0 :
        a_center_x -= ( a_xs[ an_average_y_index + 1 ] - a_xs[ an_average_y_index ] ) / 3.0
    elif an_average_y_index == a_nb_attempts - 1 :
        a_center_x += ( a_xs[ an_average_y_index ] - a_xs[ an_average_y_index - 1 ] ) / 3.0
    else:
        a_left_x = a_xs[ an_average_y_index - 1 ]
        a_right_x = a_xs[ an_average_y_index + 1 ]
        if an_average_y[ a_left_x ] < an_average_y[ a_right_x ] :
            a_center_x += ( a_right_x - a_center_x ) / 3.0
        else:
            a_center_x -= ( a_center_x - a_left_x ) / 3.0
            pass
        pass

    print "%4d - %4d\n" % ( a_center_x, a_max_average_y )    
    
    return a_center_x, a_max_average_y


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

    a_sub_xs = []
    a_x = an_end_x
    a_step = a_region_x / float( the_nb_attempts )
    for an_id in range( the_nb_attempts + 1 ) :
        if not the_x2y.has_key( a_x ) : 
            a_sub_xs.append( a_x )
            an_y = the_fun( a_x )
            the_x2y[ a_x ] = an_y
            the_cost += a_x
            pass
        a_x -= a_step
        pass

    print2_dict( a_sub_xs, the_x2y )
    print "cost : %4d\n" % the_cost

    return the_x2y, the_cost, a_region_x


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts ) :
    """ """
    a_center_x = the_center_x
    print "%4d - %4d\n" % ( a_center_x, 0.0 )
    a_sub_nb_attempts = the_nb_attempts / 1
    a_cost = 0.0
    a_x2y = {}

    #------------------------------------------------------------------------------------------
    a_max_average_y = 0.0
    a_precision = float( the_precision / 100.0 )
    while True:
        a_max_average_y2 = a_max_average_y
        a_center_x2 = a_center_x

        a_x2y, a_cost, a_region_x = get_stats( the_fun, a_x2y, a_cost, a_center_x, the_region_x, the_nb_attempts )
        a_center_x, a_max_average_y = find_center( a_x2y, a_sub_nb_attempts )

        if a_max_average_y < a_precision :
            continue

        import math
        if math.fabs( a_max_average_y - a_max_average_y2 ) / a_max_average_y > a_precision :
            continue

        if math.fabs( a_center_x - a_center_x2 ) / a_center_x > a_precision :
            continue

        break


    #------------------------------------------------------------------------------------------
    an_optimize_x = a_center_x
    print "solution : %4d / cost : %4d\n" % ( an_optimize_x, a_cost )

    return an_optimize_x, a_cost


#---------------------------------------------------------------------------------------------
