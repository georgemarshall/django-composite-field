#!/usr/bin/env python
import logging
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

EXCLUDE_FROM_PACKAGES = ['tests']


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# adapted from jaraco.classes.properties:NonDataProperty
class NonDataProperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)


class DjangoTest(TestCommand):
    user_options = [
        ('settings=', None,
         'The Python path to a settings module, e.g. '
         '"myproject.settings.main". If this isn\'t provided, the '
         'DJANGO_SETTINGS_MODULE environment variable will be used.'),

        ('noinput', None,
         "Tells Django to NOT prompt the user for input of any kind."
         "test."),
        ('failfast', None,
         "Tells Django to stop running the test suite after first failed "
         "test."),
        ('testrunner=', None,
         "Tells Django to use specified test runner class instead of "
         "the one specified by the TEST_RUNNER setting."),
        ('liveserver=', None,
         "Overrides the default address where the live server (used with "
         "LiveServerTestCase) is expected to run from. The default value is "
         "localhost:8081."),

        ('top-level-directory=', 't',
         "Top level of project for unittest discovery."),
        ('pattern=', 'p',
         "The test matching pattern. Defaults to test*.py."),
        ('keepdb', 'k',
         "Preserves the test DB between runs."),
        ('reverse', 'r',
         "Reverses test cases order."),
        ('debug-sql', 'd',
         "Prints logged SQL queries on failure."),
    ]

    def initialize_options(self):
        self.test_suite = 'DjangoTest'
        self.settings = None

        self.test_labels = None
        self.noinput = 0
        self.failfast = 0
        self.testrunner = None
        self.liveserver = None

        self.top_level_directory = None
        self.pattern = None
        self.keepdb = False
        self.reverse = False
        self.debug_sql = False

        self.output_dir = None

    def finalize_options(self):
        self.verbosity = self.verbose
        if self.settings:
            os.environ['DJANGO_SETTINGS_MODULE'] = self.settings

        if self.test_labels is not None:
            self.test_labels = self.test_labels.split(',')
        self.noinput = bool(self.noinput)
        self.failfast = bool(self.failfast)
        if self.liveserver is not None:
            os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = self.liveserver

        if self.pattern is None:
            self.pattern = 'test*.py'
        self.keepdb = bool(self.keepdb)
        self.reverse = bool(self.reverse)
        self.debug_sql = bool(self.debug_sql)

        if self.output_dir is None:
            self.output_dir = 'testxml'

    @NonDataProperty
    def test_args(self):
        return list(self._test_args())

    def _test_args(self):
        if self.verbose:
            yield '--verbose'
        if self.test_suite:
            yield self.test_suite

    def run(self):
        if self.verbosity > 0:
            # ensure that deprecation warnings are displayed during testing
            # the following state is assumed:
            # logging.capturewarnings is true
            # a "default" level warnings filter has been added for
            # DeprecationWarning. See django.conf.LazySettings._configure_logging
            logger = logging.getLogger('py.warnings')
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        TestCommand.run(self)
        if self.verbosity > 0:
            # remove the testing-specific handler
            logger.removeHandler(handler)

    def run_tests(self):
        import django
        django.setup()

        from django.conf import settings
        from django.test.utils import get_runner

        TestRunner = get_runner(settings, self.testrunner)

        test_runner = TestRunner(
            pattern=self.pattern, top_level=self.top_level_directory,
            verbosity=self.verbose, interactive=(not self.noinput),
            failfast=self.failfast, keepdb=self.keepdb, reverse=self.reverse,
            debug_sql=self.debug_sql, output_dir=self.output_dir
        )
        failures = test_runner.run_tests(self.test_labels)

        sys.exit(bool(failures))

setup(
    name='django-composite-field',
    version='0.7.4',
    description='CompositeField implementation for Django',
    long_description=read('README.rst'),
    author='Michael P. Jung',
    author_email='michael.jung@terreon.de',
    license='BSD',
    keywords='django composite field',
    url='http://bitbucket.org/bikeshedder/django-composite-field',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    tests_require=['Django'],
    cmdclass={
        'test': DjangoTest,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
