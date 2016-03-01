import logging
import multiprocessing
import os
import re
import shutil

import snapcraft

logger = logging.getLogger(__name__)


def _get_parallel_build_count():
    build_count = 1
    try:
        build_count = multiprocessing.cpu_count()
    except NotImplementedError:
        logger.warning('Unable to determine CPU count; disabling parallel '
                       'build')

    return build_count


def _search_and_replace_contents(file_path, search_pattern, replacement):
    with open(file_path, 'r+') as f:
        try:
            original = f.read()
        except UnicodeDecodeError:
            # This was probably a binary file. Skip it.
            return

        replaced = search_pattern.sub(replacement, original)
        if replaced != original:
            f.seek(0)
            f.truncate()
            f.write(replaced)


class XFbossPlugin(snapcraft.BasePlugin):

    @classmethod
    def schema(cls):
        return {}

    def __init__(self, name, options):
        super().__init__(name, options)

        self.build_packages.extend(['git', 'cmake', 'make'])

    def pull(self):
        self.run(['git', 'clone', 'https://github.com/facebook/fboss.git',
                  self.sourcedir])
        self.run(['git checkout ea2f4bd3f1e91992b8ee1d84540ece948f843a68'],
                 cwd=self.sourcedir)

        # Patch the getdeps.sh script for folly to work on Trusty
        _search_and_replace_contents(os.path.join(self.sourcedir, 'getdeps.sh'),
            re.compile(r'update.*https://github.com/facebook/folly.git'),
            'update https://github.com/facebook/folly.git '
            '08dba5714790020d2fa677e34e624eb4f34a20ca')

        # Patch the getdeps.sh script for fbthrift to work on Trusty
        _search_and_replace_contents(os.path.join(self.sourcedir, 'getdeps.sh'),
            re.compile(r'update.*https://github.com/facebook/fbthrift.git'),
            'update https://github.com/facebook/fbthrift.git '
            '1b2b03a472c41915a8c481a06edc630674377e77')

        # This builds the dependencies right after pulling them. Not ideal for
        # the pull step, but it needs to be in the source directory so it makes
        # sense to keep it here rather than build.
        self.run(['./getdeps.sh'], cwd=self.sourcedir)

    def build(self):
        if os.path.exists(self.builddir):
            shutil.rmtree(self.builddir)
        os.mkdir(self.builddir)

        self.run(['cmake', self.sourcedir])
        self.run(['make', '-j{}'.format(_get_parallel_build_count())])

        # fboss has no install rules, so we'll need to install it all by
        # ourselves. FIXME: This should be fixed upstream.
        self._install()

    def _install(self):
        # TBD
        pass
