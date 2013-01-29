import os
from datetime import datetime
from subprocess import Popen
from celery import task
from django.contrib.auth.models import User
from settings import MEDIA_ROOT, SERVER_EXEC


@task()
def run_server(path, server):
    log_path = os.path.join(MEDIA_ROOT, 'logs', server.owner.username, server.mod.title)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    with open(os.path.join(log_path, '{0}_{1}_{2}.txt'.format(server.id, datetime.now().strftime("%y%m%d%H%M%S"), User.objects.make_random_password())), 'w') as f:
        p = Popen((os.path.join(path, SERVER_EXEC), '-f', os.path.join(path, 'servers', server.owner.username, '{0}'.format(server.id), 'generated.cfg')), cwd=path, stdout=f, stderr=f)
        server.pid = p.pid
        server.online = True
        server.locked = False
        server.save()
        p.wait()


@task()
def check_server_state():
    from mod.models import Server
    servers = Server.active.all()
    for server in servers:
        old_is_online = server.is_online
        server.check_online()
        if server.automatic_restart and old_is_online and not server.is_online:
            server.set_online()
