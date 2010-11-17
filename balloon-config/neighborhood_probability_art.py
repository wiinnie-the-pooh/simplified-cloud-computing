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
## Author : Andrey Simurzin
##


#--------------------------------------------------------------------------------------
from artificial_option_parser import main
a_fun, an_initial_x, a_finite_x, a_precision, a_nb_attempts = main()

a_center_x = ( a_finite_x + an_initial_x ) / 3.0
a_region_x = ( a_finite_x - an_initial_x ) / 4.0

import neighborhood_probability_algo
an_optimize_x, a_cost = neighborhood_probability_algo.entry_point( a_fun, a_center_x, a_region_x, a_precision, a_nb_attempts )


#---------------------------------------------------------------------------------------------
