# Copyright (2018) Chris Heckler <hecklerchris@hotmail.com>

import os
from subprocess import call
from pathlib import Path

from charms.reactive import (
    when,
    when_not,
    set_flag,
)

from charmhelpers.core.hookenv import (
    status_set,
    log,
    config,
)

FLASK_DIR = Path('/srv/site-view-app')
FLASK_DEPS = Path(FLASK_DIR / 'requirements.txt')
PIP = Path('/usr/bin/pip3')


@when_not('app.flask.installed')
def install_flask_deps():
    """Clones flask app and installs deps"""

    conf = config()
    status_set('maintenance', 'Flask/Dependencies Installing')

    call(['git', 'clone', conf.get('git-flask-repo'), str(FLASK_DIR)])
    call([str(PIP), 'install', '-r', str(FLASK_DEPS)])
    call([str(PIP), 'install', 'gunicorn'])

    status_set('active', 'Flask and Dependencies Installed')
    log('Flask and Dependencies Installed')
    set_flag('app.flask.installed')



