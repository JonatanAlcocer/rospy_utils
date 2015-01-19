
# :version:      0.1.0
# :copyright:    Copyright (C) 2014 Universidad Carlos III de Madrid.
#                Todos los derechos reservados.
# :license       LASR_UC3M v1.0, ver LICENCIA.txt

# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los terminos de la Licencia Academica Social Robotics Lab - UC3M
# publicada por la Universidad Carlos III de Madrid, tanto en su version 1.0
# como en una version posterior.

# Este programa se distribuye con la intencion de que sea util,
# pero SIN NINGUNA GARANTIA. Para mas detalles, consulte la
# Licencia Academica Social Robotics Lab - UC3M version 1.0 o posterior.

# Usted ha recibido una copia de la Licencia Academica Social
# Robotics Lab - UC3M en el fichero LICENCIA.txt, que tambien se encuentra
# disponible en <URL a la LASR_UC3Mv1.0>.

PKG = 'rospy_utils'
import unittest
from mock import patch
import operator as op
import rospy
from std_msgs.msg import String

from rospy_utils import coroutines as co

# Utility functions
inc = lambda x: x + 1
is_even = lambda x: x % 2 == 0
is_odd = lambda x: x % 2 != 0


class TestCoroutines(unittest.TestCase):

    def __init__(self, *args):
        super(TestCoroutines, self).__init__(*args)

    @co.coroutine
    def list_evaluator(self, expected):
        ''' Sink coroutine that evaluates received list against expected '''
        while True:
            data = (yield)
            self.assertEqual(expected, data)

    @co.coroutine
    def item_evaluator(self, expected):
        ''' Same as evaluator, but this one expects to receive items 1 by 1 '''
        expected = iter(expected)
        while True:
            data = (yield)
            self.assertEqual(next(expected), data)

    def setUp(self):
        self.data = xrange(5)

    def tearDown(self):
        pass

    def test_buffer(self):
        expected = list(self.data)
        tester = self.list_evaluator(expected)
        test_buff = co.buffer(len(self.data), tester)
        for c in self.data:
            # At the end of the loop, co.buffer should send all data
            # to self.evaluator who which will execute the assertion.
            test_buff.send(c)

    def test_sliding_window(self):
        expected = [[0], [0, 1], [0, 1, 2], [1, 2, 3], [2, 3, 4]]
        tester = self.item_evaluator(expected)
        test_sliding = co.sliding_window(3, tester)
        for i in self.data:
            test_sliding.send(i)

    def test_transformer(self):
        expected = map(inc, self.data)
        tester = self.item_evaluator(expected)
        test_transformer = co.transformer(inc, tester)
        for i in self.data:
            test_transformer.send(i)

    def test_filter(self):
        expected = filter(is_even, self.data)
        tester = self.item_evaluator(expected)
        test_filter = co.filter(is_even, tester)
        for i in self.data:
            test_filter.send(i)

    def test_splitter(self):
        tester1 = self.item_evaluator(self.data)
        tester2 = self.item_evaluator(self.data)
        tester3 = self.item_evaluator(self.data)
        test_splitter = co.splitter(tester1, tester2, tester3)
        for i in self.data:
            test_splitter.send(i)

    def test_either(self):
        evens = filter(is_even, self.data)
        odds = filter(is_odd, self.data)
        tester_evens = self.item_evaluator(evens)
        tester_odds = self.item_evaluator(odds)
        test_either = co.either(is_even, tester_evens, tester_odds)
        for i in self.data:
            test_either.send(i)

    def test_accumulator(self):
        expected = [2, 4, 8, 16, 32]
        tester = self.item_evaluator(expected)
        test_accumulator = co.accumulator(op.mul, 1, tester)
        for _ in xrange(5):
            test_accumulator.send(2)

    def test_pipe(self):
        self.fail()


class TestConsumerCoroutines(unittest.TestCase):

    def __init__(self, *args):
        super(TestConsumerCoroutines, self).__init__(*args)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('rospy.Publisher')
    def test_publisher(self, mock_pub):
        co.publisher('my_topic', String).send('Hello World!')
        mock_pub.assert_called()

    @patch('rospy.logerr')
    def test_logger(self, mock_loggerr):
        err_logger = co.logger(rospy.logerr, prefix="ERROR: ", suffix="!!!")
        err_logger.send("This is an error message")
        mock_loggerr.assert_called_with("ERROR: This is an error message!!!")

    # @patch('print')
    # def test_printer(self, mock_print):
    #     p = co.printer()
    #     p.send("Hello World!")
    #     mock_print.assert_called()


if __name__ == '__main__':
    import rosunit
    rosunit.unitrun(PKG, 'test_coroutines', TestCoroutines)
    rosunit.unitrun(PKG, 'test_consumer_coroutines', TestConsumerCoroutines)
