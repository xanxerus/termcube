#!/usr/bin/env python3
#Must run this script with -m flag

from termcube.cube import Cube
from termcube.turn import TurnSequence
from wsgiref.simple_server import make_server, demo_app

def test(environ, start_response):
	"""Simplest possible application object""" 
	status = '200 OK'
	response_headers = [('Content-type','text/html; charset=utf-8')]
	start_response(status, response_headers)
	
	r = Cube(6)
	one = r.visualize()
	
	r.scramble()
	two = r.visualize()
	print(r)
	
	r.apply("z2 x'")
	three = r.visualize()
	
	template = '<img src="%s"/><br>'
	return [(template % three).encode("utf-8")]

httpd = make_server('', 8000, test)
print("Serving HTTP on port 8000...")

httpd.serve_forever()
