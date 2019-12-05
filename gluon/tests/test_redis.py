#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Unit tests for redis """

import unittest
import os
import time
from datetime import datetime

from gluon._compat import to_bytes
from gluon.storage import Storage
from gluon.utils import web2py_uuid
from gluon.globals import Request, Response, Session, current
from gluon.contrib.redis_utils import RConn
from gluon.contrib.redis_session import RedisSession
from gluon.contrib.redis_cache import RedisCache


def setup_clean_session():
    request = Request(env={})
    request.application = 'a'
    request.controller = 'c'
    request.function = 'f'
    request.folder = 'applications/admin'
    response = Response()
    session = Session()
    session.connect(request, response)
    from gluon.globals import current
    current.request = request
    current.response = response
    current.session = session
    return current


def setUpModule():
    pass


def tearDownModule():
    if os.path.isfile('appconfig.json'):
        os.unlink('appconfig.json')


class TestRedis(unittest.TestCase):
    """ Tests the Redis contrib packages """

    def test_0_redis_session(self):
        """ Basic redis read-write """
        current = setup_clean_session()
        response = current.response
        rconn = RConn(host='redis')
        db = RedisSession(redis_conn=rconn, session_expiry=False)
        tname = 'testtablename'
        db.define_table(tname)
        table = db[tname]
        unique_key = web2py_uuid()
        dd = dict(
            locked=0,
            client_ip=response.session_client,
            modified_datetime=datetime.now().isoformat(),
            unique_key=unique_key
        )
        record_id = table.insert(**dd)
        data_from_db = db(table.id == record_id).select()[0]
        print('data_from_db=', data_from_db)
        self.assertDictEqual(Storage(dd), data_from_db)

