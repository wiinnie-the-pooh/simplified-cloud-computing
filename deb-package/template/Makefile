## VulaSHAKA (Simultaneous Neutronic, Fuel Performance, Heat And Kinetics Analysis)
## Copyright (C) 2009-2010 Pebble Bed Modular Reactor (Pty) Limited (PBMR)
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
## 
## See https://vulashaka.svn.sourceforge.net/svnroot/vulashaka
##
## Author : Alexey PETROV
##


#--------------------------------------------------------------------------------------
DESTDIR=111
PYTHON_FLU_BIN=$(DESTDIR)/usr/local/bin
PYTHON_FLU_LIB=$(DESTDIR)/usr/local/lib/python2.6/dist-packages/

dirs := $(shell ls Foam/applications/solvers -F | grep / | sed 's/\///g')

solvers :=  $(addsuffix /*Foam.py, $(addprefix Foam/applications/solvers/, $(dirs)))

install: install-bin install-lib
	@ echo "That's all"

install-bin: $(wildcard $(solvers) )
	@ echo "Installing exe"
	@ install -d $(PYTHON_FLU_BIN)
	@ install -m 755 $^ $(PYTHON_FLU_BIN)

install-lib: 
	@ echo "Installing lib"
	@ install -d $(PYTHON_FLU_LIB)
	@ cp -rf Foam $(PYTHON_FLU_LIB)/

rm-solv: $(wildcard $(addprefix $(PYTHON_FLU_LIB), $(solvers)))
	@ echo "rm solvers"
	@ rm -f $^
       	
