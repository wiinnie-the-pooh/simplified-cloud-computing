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
from real import create_boto_config
a_boto_config, a_saved_environ = create_boto_config()

from real_option_parser import main
a_region, a_logsuffix, an_initial_size, an_end_size, a_precision, a_nb_attempts = main()

from real import try_upload
an_engine = try_upload( a_region, a_logsuffix )
   
a_center_x = ( an_end_size + an_initial_size ) / 2.0
a_region_x = ( an_end_size - an_initial_size ) / 4.0

import neighborhood_probability_algo
an_optimize_x, a_cost = neighborhood_probability_algo.entry_point( an_engine, a_center_x, a_region_x, a_precision, a_nb_attempts )

from real import restore_environ
restore_environ( a_saved_environ, a_boto_config )


#--------------------------------------------------------------------------------------
