from tornado.testing import gen_test, AsyncTestCase
from tornado import gen
from tornado.ioloop import IOLoop
import motorm
from motorm import connect, _db
from schematics.types import StringType
import motor
import pymongo

from tornado.concurrent import return_future

db_test = "motorm_test"

class TestModel(motorm.AsyncModel):
    __collection__ = "AsyncModelTests"
    name = StringType()


class TesteAll(AsyncTestCase):
    @gen_test
    def test_async_save(self):
        """Teste async save of a model"""
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm_insance = yield tm.save()

        self.assertIsNotNone(tm_insance.id)

    @gen_test
    def teste_async_iter_cursor(self):
        connect(db_test, self.io_loop)

        instances = []
        tm = TestModel()
        tm.name = "iter_name1"
        instances.append((yield tm.save()))
        tm2 = TestModel()
        tm2.name = "iter_name2"
        instances.append((yield tm2.save()))

        tm_cursor = TestModel.objects.filter({"name": {"$regex": "iter_name."}})
        on_result = []
        while (yield tm_cursor.fetch_next):
            tm_instance = tm_cursor.next_object()
            for instance in instances:
                if tm_instance.name == instance.name:
                    on_result.append(True)

        self.assertEqual(sum(on_result), 2)

    @gen_test
    def test_async_get(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)

        self.assertIsNotNone(tm_fromdb)

    @gen_test
    def test_async_update(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)
        tm_fromdb = yield tm_fromdb.save()

        self.assertIsNotNone(tm_fromdb)

def tearDownModule():
        @gen.engine
        def drop_database():
            mc = connect(db_test, io_loop=IOLoop.instance())
            yield gen.Task(mc.drop_database,db_test)
            IOLoop.instance().stop()
        drop_database()
        IOLoop.instance().start()
