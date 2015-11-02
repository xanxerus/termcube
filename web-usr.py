#!/usr/bin/env python
# -*- coding: utf-8 -*-
from turn import TurnSequence
from cube import Cube

def test(environ, start_response):
	"""Simplest possible application object""" 
	status = '200 OK'
	response_headers = [('Content-type','text/html')]
	start_response(status, response_headers)
	
	r = Cube(6)
	one = r.visualize()
	
	r.scramble()
	two = r.visualize()
	print(r)
	
	r.apply("z2 x'")
	three = r.visualize()
	
	template = '<img src="%s"/><br>'
	return [template % two, template % three]

from wsgiref.simple_server import make_server, demo_app

httpd = make_server('', 8000, test)
print "Serving HTTP on port 8000..."

httpd.serve_forever()
#~ httpd.handle_request()
