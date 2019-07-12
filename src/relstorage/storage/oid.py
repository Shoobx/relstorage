# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, 2019 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
Implementation of the oid allocation algorithm.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ZODB.POSException import ReadOnlyError
from ZODB.utils import p64 as int64_to_8bytes

class OIDs(object):

    __slots__ = (
        'preallocated_oids',
        'max_new_oid',
        'oidallocator',
        '_with_store',
    )

    def __init__(self, oidallocator, with_store):
        self.preallocated_oids = None
        self.max_new_oid = 0
        self.oidallocator = oidallocator
        self._with_store = with_store

    def stale(self, e):
        return StaleOIDs(e, self)

    def no_longer_stale(self):
        return self

    def new_oid(self):
        # Prior to ZODB 5.1.2, this method was actually called on the
        # storage object of the DB, not the instance storage object of
        # a Connection. This meant that this method (and the oid
        # cache) was shared among all connections using a database and
        # was called outside of a transaction (starting its own
        # long-running transaction).

        # The DB.new_oid() method still exists, but shouldn't be used;
        # if it is, we'll open a database connection and transaction that's
        # going to sit there idle, possibly holding row locks. That's bad.
        # But we don't take any counter measures.

        # Connection.new_oid() can be called at just about any time
        # thanks to the Connection.add() API, which clients can use
        # at any time (typically before commit begins, but it's possible to
        # add() objects from a ``__getstate__`` method).
        #
        # Thus we may or may not have a store connection already open;
        # if we do, we can't restart it or drop it.
        if not self.preallocated_oids:
            self.preallocated_oids = self._with_store(self.__new_oid_callback)

        oid_int = self.preallocated_oids.pop()
        self.max_new_oid = max(self.max_new_oid, oid_int)
        return int64_to_8bytes(oid_int)

    def __new_oid_callback(self, _store_conn, store_cursor, _fresh_connection):
        return self.oidallocator.new_oids(store_cursor)


class ReadOnlyOIDs(object):

    def stale(self, e):
        return StaleOIDs(e, self)

    def no_longer_stale(self):
        return self

    def new_oid(self):
        raise ReadOnlyError

class StaleOIDs(object):

    __slots__ = (
        'stale_error',
        'previous',
    )

    def __init__(self, stale_error, previous):
        self.stale_error = stale_error
        self.previous = previous

    def no_longer_stale(self):
        return self.previous
