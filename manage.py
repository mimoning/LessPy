#!/usr/bin/env python
import os

from app import create_app, db
from app.models import User, Role, Permission, Post, Comment

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,
                Post=Post, Comment=Comment)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
