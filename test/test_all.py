from tornado.testing import gen_test, AsyncTestCase
from tornado import gen
from tornado.ioloop import IOLoop
import motorm
from motorm import connect, disconnect
from schematics.types import StringType
import pymongo


db_test = "motorm_test"


def setUpModule():
    @gen.engine
    def drop_database():
        mc = connect(db_test, io_loop=IOLoop.instance())
        yield gen.Task(mc.drop_database, db_test)
        IOLoop.instance().stop()
    drop_database()
    IOLoop.instance().start()


class TestModel(motorm.AsyncModel):
    __collection__ = "AsyncModelTests"
    name = StringType()


class TestWOCModel(motorm.AsyncModel):
    name = StringType()



class TesteAll(AsyncTestCase):

    @gen_test
    def test_async_update_WOC(self):
        connect(db_test, self.io_loop)

        tm = TestWOCModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestWOCModel.objects.get(id=tm.id)
        tm_fromdb.name = "new_name"
        tm_fromdb = yield tm_fromdb.save()

        self.assertIsNotNone(tm_fromdb)
        disconnect()

    @gen_test
    def test_async_save(self):
        """Teste async save of a model"""
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm_insance = yield tm.save()

        self.assertIsNotNone(tm_insance.id)
        disconnect()

    @gen_test
    def test_async_delete(self):
        """Teste async delete of a model"""
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()
        self.assertIsNotNone(tm.id)

        yield tm.delete()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)

        self.assertIsNone(tm_fromdb)

        disconnect()

    @gen_test
    def teste_async_iter_cursor_with_sort(self):
        connect(db_test, self.io_loop)

        instances = []
        tm = TestModel()
        tm.name = "iter_order1"
        instances.append((yield tm.save()))
        tm2 = TestModel()
        tm2.name = "iter_order2"
        instances.append((yield tm2.save()))

        tm_cursor = TestModel.objects.filter(
            {"name": {"$regex": "^iter_order"}}).sort(
                "name", pymongo.DESCENDING
        )

        tm_result = []
        while (yield tm_cursor.fetch_next):
            tm_instance = tm_cursor.next_object()
            tm_result.append(tm_instance)

        self.assertEqual(len(tm_result), 2)
        self.assertIn("order2", tm_result[0].name)
        disconnect()

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

        tm_cursor = TestModel.objects.filter(
            {"name": {"$regex": "iter_name."}})
        on_result = []
        while (yield tm_cursor.fetch_next):
            tm_instance = tm_cursor.next_object()
            for instance in instances:
                if tm_instance.name == instance.name:
                    on_result.append(True)

        self.assertEqual(sum(on_result), 2)
        disconnect()

    @gen_test
    def test_async_get(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)

        self.assertIsNotNone(tm_fromdb)
        disconnect()

    @gen_test
    def test_async_get_custom_field(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1_custom"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(name=tm.name)

        self.assertIsNotNone(tm_fromdb)

        disconnect()

    @gen_test
    def test_async_update(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)
        tm_fromdb.name = "new_name"
        tm_fromdb = yield tm_fromdb.save()

        self.assertIsNotNone(tm_fromdb)
        disconnect()

    @gen_test
    def test_async_update_without_change(self):
        connect(db_test, self.io_loop)

        tm = TestModel()
        tm.name = "name1"
        yield tm.save()

        tm_fromdb = yield TestModel.objects.get(id=tm.id)
        tm_fromdb = yield tm_fromdb.save()

        self.assertIsNotNone(tm_fromdb)
        disconnect()

    @gen_test
    def test_async_all(self):
        connect(db_test, self.io_loop)

        for i in range(10):
            tm = TestModel()
            tm.name = "alltest-%s" % i
            yield tm.save()

        tm_list = yield TestModel.objects.all()
        self.assertEqual(len(tm_list), 10, "List must be equal 10")
        disconnect()

    @gen_test
    def test_async_cursor_all(self):
        connect(db_test, self.io_loop)

        instances = []
        tm = TestModel()
        tm.name = "iter_all_name1"
        instances.append((yield tm.save()))
        tm2 = TestModel()
        tm2.name = "iter_all_name2"
        instances.append((yield tm2.save()))

        tm_cursor_all = yield TestModel.objects.filter(
            {"name": {"$regex": "iter_all_name."}}).all()

        self.assertEqual(len(tm_cursor_all), 2, "List must be equal 2")
        disconnect()

