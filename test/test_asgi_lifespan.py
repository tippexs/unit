import os
import pytest
from distutils.version import LooseVersion

from unit.applications.lang.python import TestApplicationPython
from conftest import option


class TestASGILifespan(TestApplicationPython):
    prerequisites = {
        'modules': {'python': lambda v: LooseVersion(v) >= LooseVersion('3.5')}
    }
    load_module = 'asgi'

    def test_asgi_lifespan(self):
        self.load('lifespan/empty')

        startup_path = option.test_dir + '/python/lifespan/empty/startup'
        shutdown_path = option.test_dir + '/python/lifespan/empty/shutdown'
        version_path = option.test_dir + '/python/lifespan/empty/version'

        open(startup_path, 'a').close()
        open(shutdown_path, 'a').close()
        open(version_path, 'a').close()

        assert self.get()['status'] == 204

        self.stop()

        is_startup = os.path.isfile(startup_path)
        is_shutdown = os.path.isfile(shutdown_path)

        if is_startup:
            os.remove(startup_path)

        if is_shutdown:
            os.remove(shutdown_path)

        with open(version_path, 'r') as f:
            version = f.read()

        os.remove(version_path)

        assert not is_startup, 'startup'
        assert not is_shutdown, 'shutdown'
        assert version == '3.0 2.0', 'version'

    def test_asgi_lifespan_failed(self):
        self.load('lifespan/failed')

        assert self.get()['status'] == 503

        assert (
            self.wait_for_record(r'\[error\].*Application startup failed')
            is not None
        ), 'error message'
        assert self.wait_for_record(r'Exception blah') is not None, 'exception'

    def test_asgi_lifespan_error(self):
        self.load('lifespan/error')

        self.get()

        assert self.wait_for_record(r'Exception blah') is not None, 'exception'

    def test_asgi_lifespan_error_auto(self):
        self.load('lifespan/error_auto')

        self.get()

        assert self.wait_for_record(r'AssertionError') is not None, 'assertion'
