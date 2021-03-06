# -*- coding: utf-8 -*-
"""Webapp2 request argument parsing module.

Example: ::

    import webapp2

    from marshmallow import fields
    from webargs.webobparser import use_args

    hello_args = {
        'name': fields.Str(missing='World')
    }

    class MainPage(webapp2.RequestHandler):

        @use_args(hello_args)
        def get_args(self, args):
            self.response.write('Hello, {name}!'.format(name=args['name']))

        @use_kwargs(hello_args)
        def get_kwargs(self, name=None):
            self.response.write('Hello, {name}!'.format(name=name))

    app = webapp2.WSGIApplication([
        webapp2.Route(r'/hello', MainPage, handler_method='get_args'),
        webapp2.Route(r'/hello_dict', MainPage, handler_method='get_kwargs'),
    ], debug=True)
"""
import logging

from webargs import core
import webapp2
import webapp2_extras.json
import webob.multidict

logger = logging.getLogger(__name__)


class Webapp2Parser(core.Parser):
    """webapp2 request argument parser."""

    def parse_json(self, req, name, field):
        """Pull a json value from the request."""
        try:
            json_data = webapp2_extras.json.decode(req.body)
            return core.get_value(json_data, name, core.is_multiple(field))
        except ValueError:
            return core.missing

    def parse_querystring(self, req, name, field):
        """Pull a querystring value from the request."""
        return core.get_value(req.GET, name, core.is_multiple(field))

    def parse_form(self, req, name, field):
        """Pull a form value from the request."""
        return core.get_value(req.POST, name, core.is_multiple(field))

    def parse_cookies(self, req, name, field):
        """Pull the value from the cookiejar."""
        return core.get_value(req.cookies, name, core.is_multiple(field))

    def parse_headers(self, req, name, field):
        """Pull a value from the header data."""
        return core.get_value(req.headers, name, core.is_multiple(field))

    def parse_files(self, req, name, field):
        """Pull a file from the request."""
        files = ((k, v) for k, v in req.POST.items() if hasattr(v, 'file'))
        return core.get_value(webob.multidict.MultiDict(files), name, core.is_multiple(field))

    def parse(self, argmap, req=None, locations=None, validate=None, force_all=False):
        """Wrap :meth:`core.Parser.parse` to inject the active :class:`webapp2.Request` in"""
        req = req or webapp2.get_request()
        return super(Webapp2Parser, self).parse(argmap, req, locations, validate, force_all)

parser = Webapp2Parser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
