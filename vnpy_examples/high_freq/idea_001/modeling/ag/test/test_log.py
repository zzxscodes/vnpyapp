import unittest

from vnpy_app.utility.log import TimeInspector
from vnpy_app.utility.log import get_module_logger


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.logger = get_module_logger('user.normal')
        self.logger.debug('debug')
        self.logger.info('info')
        self.logger.warn('warn')
        self.logger.error('error')

    def test_time_inspector(self):
        with TimeInspector.logt('timer'):
            self.test_something()


if __name__ == '__main__':
    unittest.main()
