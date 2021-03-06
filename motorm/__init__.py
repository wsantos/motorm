#!/bin/env python
from schematics.models import Model, ModelMeta
from schematics.contrib.mongo import ObjectIdType
from tornado import gen

#-- Tornado
from tornado.concurrent import return_future

#-- DB
import motor
from bson.objectid import ObjectId
import functools


__all__ = ['AsyncModel', 'connect']

_db = None
_mc = None
BATCH = 5


def connect(db, io_loop=None):
    global _db
    global _mc

    mc = motor.MotorClient(io_loop=io_loop or None)
    _mc = mc
    _db = mc[db]
    mc.write_concern = {'w': 1, 'wtimeout': 1000}
    return mc


def disconnect():
    _mc.disconnect()


class AsyncManagerCursor(object):

    def __init__(self, cls, cursor):
        self.cursor = cursor
        self.cls = cls

    @property
    def fetch_next(self):
        return self.cursor.fetch_next

    def next_object(self):
        result = self.cursor.next_object()
        return self.cls(result)

    def sort(self, *args, **kwargs):
        self.cursor = self.cursor.sort(*args, **kwargs)
        return self

    @return_future
    def all(self, callback):

        return_list = []

        def handle_all_response(response, error, return_list):
            if error:
                raise error
            else:
                if response:
                    return_list += [self.cls(document)
                                    for document in response]
                    self.cursor.to_list(
                        BATCH, callback=functools.partial(handle_all_response, return_list=return_list))
                else:
                    callback(return_list)

        self.cursor.to_list(BATCH, callback=functools.partial(
            handle_all_response, return_list=return_list))


class AsyncManager(object):

    def __init__(self, cls, collection):
        self.collection = collection
        self.cls = cls

    @return_future
    def get(self, **kwargs):
        callback = kwargs.pop("callback")

        def handle_get_response(response, error):
            if error:
                raise error
            else:
                if response is None:
                    callback(None)
                else:
                    callback(self.cls(response))

        id = kwargs.pop("id", None)

        qry = dict()
        if id:
            id = ObjectId(id) if not isinstance(id, ObjectId) else id

            qry = dict(
                _id=id
            )

        qry.update(kwargs)

        _db[self.collection].find_one(qry, callback=handle_get_response)

    def filter(self, query):
        cursor = _db[self.collection].find(query)
        return AsyncManagerCursor(self.cls, cursor)

    @return_future
    def all(self, callback):

        return_list = []

        def handle_all_response(response, error, return_list):
            if error:
                raise error
            else:
                if response:
                    return_list += [self.cls(document)
                                    for document in response]
                    cursor.to_list(BATCH, callback=functools.partial(
                        handle_all_response, return_list=return_list))
                else:
                    callback(return_list)

        cursor = _db[self.collection].find({})

        cursor.to_list(BATCH, callback=functools.partial(
            handle_all_response, return_list=return_list))


class AsyncManagerMetaClass(ModelMeta):

    def __new__(cls, name, bases, attrs):
        super_new = super(AsyncManagerMetaClass, cls).__new__

        parents = [b for b in bases if isinstance(b, AsyncManagerMetaClass) and
                   not (b.__mro__ == (b, object))]

        if not parents:
            return super_new(cls, name, bases, attrs)
        else:
            if "id" not in attrs:
                attrs["id"] = ObjectIdType(
                    serialized_name='_id', serialize_when_none=False)

            new_class = super_new(cls, name, bases, attrs)

            # Collection name
            attrs["__collection__"] = attrs.get(
                "__collection__", name.replace("Model", "").lower())

            collection = attrs["__collection__"]

            # Add all attributes to the class.
            for obj_name, obj in attrs.items():
                setattr(new_class, obj_name, obj)

            manager = AsyncManager(new_class, collection)
            setattr(new_class, "objects", manager)

            return new_class


class AsyncModel(Model):
    __metaclass__ = AsyncManagerMetaClass

    @return_future
    def delete(self, **kwargs):
        callback = kwargs.pop("callback")

        def handle_delete_response(response, error):
            if error:
                raise error
            else:
                callback(self)

        _db[self.__collection__].remove({"_id": self.id},
                                        callback=handle_delete_response)

    @return_future
    def save(self, **kwargs):
        callback = kwargs.pop("callback")

        # Ensure ObjectId for _id
        if self.id:
            self.id = ObjectId(self.id) if not \
                isinstance(self.id, ObjectId) else self.id

        def handle_save_response(response, error):
            if error:
                raise error
            else:
                self.id = response
                callback(self)

        def handle_update_response(response, error):
            if error:
                raise error
            else:
                callback(self)

        self.validate()

        if self._initial == {} or (self._initial != {} and
                                   self._data['id'] is None):
            _db[self.__collection__].save(
                self.to_native(), callback=handle_save_response)
        else:
            set_qry = dict()
            if self._initial != self._data:
                for field, value in self.to_native().items():
                    if value != self._initial[field]:
                        set_qry[field] = value

                set_qry.pop("_id", None)

                if set_qry:
                    _db[self.__collection__].update({"_id": self.id},
                                                    {"$set": set_qry}, callback=handle_update_response)
                else:
                    raise gen.Return()
