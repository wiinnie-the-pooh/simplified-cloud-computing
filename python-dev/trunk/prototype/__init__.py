"""This package provides Simpllified Cloud Computing interface."""

__version__ = '0.0.1'

import httplib, urllib
import json

global _Connection
global _Url
global _Port

#global configuration
_Url = "cloud-mockup.appspot.com";
_Port = 80;

def home_config():
	global _Url
	global _Port
	_Url = "localhost"
	_Port = 8888

def SCC_Connect():
	global _Connection
	_Connection = httplib.HTTPConnection(_Url, _Port)

def SCC_GETService():
	global _Connection
	params = urllib.urlencode( {'UID': 'abd', 'Method' : 'GETService' } )
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
	_Connection.request("POST", "/test", params, headers)
	response = _Connection.getresponse()
	#print response.status, response.reason
	print response.read()
	#jresponce = json.loads( response.read() ) # NVP: ("ServiceId",SERVICE_ID)

def SCC_PUTBucket( aContainer ):
	global _Connection

def SCC_GETBucket( aContainer ):
	global _Connection

def SCC_DELETEBucket( aContainer ):
	global _Connection

def SCC_PUTObject( anObject ):
	global _Connection


def SCC_DELETEObject( anObject ):
	global _Connection

def SCC_GETObject( anObject ):
	global _Connection




