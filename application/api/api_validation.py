from werkzeug.exceptions import HTTPException
from flask import make_response
from datetime import datetime

class NotFoundError(HTTPException):
    def __init__(self, entity, status_code=404, msg=None):
        if msg:
            self.response = make_response(f'{entity} not found', status_code, msg=msg)
        else:
            self.response = make_response(f'{entity} not found', status_code)

class InternalServerError(HTTPException):
    def __init__(self, status_code=500):
        self.response = make_response('Internal Server Error', status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code,
                   "error_message": error_message}
        self.response = make_response(message, status_code)

def validate_int(val, ecode, emsg):
    if val is None or not val.isdecimal():
        raise BusinessValidationError(  status_code=400,
                                        error_code=ecode,
                                        error_message=emsg)
    else:
        return int(val)

def validate_str(val, ecode, emsg, req='NN_NE'):
    if req == 'NN_NE':
        if val is None or val == '':
            raise BusinessValidationError(  status_code=400,
                                            error_code=ecode,
                                            error_message=emsg)
        else:
            if len(val) > 50 or len(val) < 4:
                raise BusinessValidationError(  status_code=400,
                                                error_code=ecode,
                                                error_message=emsg)
            return val
    if req == 'NE':
        if val is None:
            return None
        else:
            if len(val) > 50 or len(val) < 4:
                raise BusinessValidationError(  status_code=400,
                                                error_code=ecode,
                                                error_message=emsg)
            else:
                return val

def validate_dt(val, ecode, emsg):
    if val is not None:
        try:
            val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
        except:
            raise BusinessValidationError(  status_code=400,
                                            error_code=ecode,
                                            error_message=emsg)
        else:
            return val
    else:
        return None

def validate_date(val, ecode, emsg):
    if val:
        try:
            val = datetime.strptime(val, '%Y-%m-%d').date()
        except:
            raise BusinessValidationError(status_code=400, error_code=ecode, error_message=emsg)
        else:
            return val
    else:
        raise BusinessValidationError(status_code=400, error_code=ecode, error_message=emsg)

def validate_bool(val, ecode, emsg):
    if val is not None:
        if val == 'True':
            return True
        elif val == 'False':
            return False
        else:
            raise BusinessValidationError(
                status_code=400,
                error_code=ecode,
                error_message=emsg)