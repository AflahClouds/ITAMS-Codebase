import os

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # ready() fires for every manage.py subcommand (test, migrate, shell, ...), and
        # runserver's autoreloader re-executes this module in a watcher process on top of
        # that. Only start the scheduler in the actual long-running dev server process:
        # skip entirely for non-runserver commands, and (when the reloader is active)
        # skip the watcher process — only the RUN_MAIN='true' subprocess is the real server.
        argv = os.sys.argv
        if 'runserver' not in argv:
            return
        if '--noreload' not in argv and os.environ.get('RUN_MAIN') != 'true':
            return
        from . import scheduler
        scheduler.start()
