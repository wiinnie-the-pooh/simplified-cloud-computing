"""This package provides Simpllified Cloud Computing interface."""

__version__ = '0.0.1'

import httplib, urllib

global _Connection

def SCC_Connect()
{
	global _Connection
	_Connection = httplib.HTTPConnection('cloud-mockup.appspot.com/test', 80)
	
	global _Connection
	params = urllib.urlencode( {'UID': 'abd' } )
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
	_Connection.request("POST", "/test", params, headers)
	response = _Connection.getresponse()
	print response.status, response.reason
	print response.read()
}

def SCC_GETService()
{	
}

def SCC_PUTBucket( aContainer )
{
}

def SCC_GETBucket( aContainer )
{
}

def SCC_DELETEBucket( aContainer )
{
}

def SCC_PUTObject( anObject )
{
}

def SCC_DELETEObject( anObject )
{
}

def SCC_GETObject( anObject )
{
}




