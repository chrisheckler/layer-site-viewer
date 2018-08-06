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
    open_port,
)

from charmhelpers.core.host import (
    service_running,
    service_start,
    service_restart,
)

from charmhelpers.core.templating import render


FLASK_DIR = Path('/srv/site_view_app')
FLASK_DEPS = FLASK_DIR / 'requirements.txt'
PIP = Path('/usr/bin/pip3')


@when_not('app.flask.installed')
def install_flask_deps():
    """Clones flask app and installs deps"""

    conf = config()
    status_set('maintenance', 'Flask/Dependencies Installing')

    if FLASK_DIR.exists():
        call(['rm', '-rf', str(FLASK_DIR)])
    call(['git', 'clone', conf.get('git-flask-repo'), str(FLASK_DIR)])
    call([str(PIP), 'install', '-r', str(FLASK_DEPS)])
    call([str(PIP), 'install', 'gunicorn'])

    status_set('active', 'Flask/Dependencies Installed')
    log('Flask and Dependencies Installed')
    set_flag('app.flask.installed')


@when('app.flask.installed')
@when_not('app.flask.running')
def flask_systemd_started():
    """Configure systemd to run application"""

    status_set('maintenance', 'Configuring systemd')

    render('flask.service.tmpl', '/etc/systemd/system/flaskapp.service',
           context={})
    call(['systemctl', 'flaskapp'])
    call(['systemctl', 'enable', 'flaskapp'])

    if not service_running('flaskapp'):
        service_start('flaskapp')
    else:
        service_restart('flaskapp')

    open_port(5000)

    status_set('active', 'Flask App Running')
    log('Flask App Running')
    set_flag('app.flask.running')



