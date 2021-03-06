# -*- coding: utf-8 -*-
"""Flask request argument parsing module.

Example: ::

    from flask import Flask
    from marshmallow import fields
    from webargs.flaskparser import use_args

    app = Flask(__name__)

    hello_args = {
        'name': fields.Str(required=True)
    }

    @app.route('/')
    @use_args(hello_args)
    def index(args):
        return 'Hello ' + args['name']
"""
import logging

from flask import request, abort as flask_abort
from werkzeug.exceptions import HTTPException

from webargs import core

logger = logging.getLogger(__name__)

def abort(http_status_code, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.

    From Flask-Restful. See NOTICE file for license information.
    """
    try:
        flask_abort(http_status_code)
    except HTTPException as err:
        if len(kwargs):
            err.data = kwargs
        raise err


class FlaskParser(core.Parser):
    """Flask request argument parser."""

    def parse_json(self, req, name, field):
        """Pull a json value from the request."""
        # Fail silently so that the webargs parser can handle the error
        json_data = req.get_json(silent=True)
        if json_data:
            return core.get_value(json_data, name, core.is_multiple(field))
        else:
            return core.missing

    def parse_querystring(self, req, name, field):
        """Pull a querystring value from the request."""
        return core.get_value(req.args, name, core.is_multiple(field))

    def parse_form(self, req, name, field):
        """Pull a form value from the request."""
        try:
            return core.get_value(req.form, name, core.is_multiple(field))
        except AttributeError:
            pass
        return core.missing

    def parse_headers(self, req, name, field):
        """Pull a value from the header data."""
        return core.get_value(req.headers, name, core.is_multiple(field))

    def parse_cookies(self, req, name, field):
        """Pull a value from the cookiejar."""
        return core.get_value(req.cookies, name, core.is_multiple(field))

    def parse_files(self, req, name, field):
        """Pull a file from the request."""
        return core.get_value(req.files, name, core.is_multiple(field))

    def handle_error(self, error):
        """Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        logger.error(error)
        status_code = getattr(error, 'status_code', self.DEFAULT_VALIDATION_STATUS)
        abort(status_code, messages=error.messages, exc=error)

    def parse(self, argmap, req=None, *args, **kwargs):
        """Parses the request using the given arguments map.
        Uses Flask's context-local request object if req=None.
        """
        req_obj = req or request  # Default to context-local request
        return super(FlaskParser, self).parse(argmap, req_obj, *args, **kwargs)

parser = FlaskParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
