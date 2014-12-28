import random

from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, TypeDecorator, Text
from flask import json

from flask.ext.sqlalchemy import SQLAlchemy

from .pager import Pager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/test'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship


def generat_id():
    id = random.randint(17592186044416, 281474976710655)
    return hex(id)[2:]


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class.
    """
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(128), primary_key=True, autoincrement=False,
                   server_default=generat_id())

    @classmethod
    def get_by_id(cls, id):
        # if any(
        #     (isinstance(id, basestring) and id.isdigit(),
        #      isinstance(id, (int, float))),
        # ):
        #     return cls.query.get(int(id))
        # return None
        return cls.query.get(id)


def ReferenceCol(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = ReferenceCol('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey("{0}.{1}".format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class JsonString(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return JsonString(self.impl.length)


class JsonText(JsonString):
    impl = Text

    def copy(self):
        return JsonText(self.impl.length)


class User(SurrogatePK, Model):

    __tablename__ = 'user'
    __table_args__ = (
        db.Index('ix_user_email_password', 'email', 'password'),
    )

    email = db.Column(db.String(128), nullable=False, unique=True)
    mobile = db.Column(db.String(128), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    created_time = db.Column(db.DateTime(timezone=True),
                             index=True, nullable=False,
                             server_default=db.func.current_timestamp())


@app.route('/user')
def user():
    query = User.query
    pager = Pager(query.count())
    users = query.all()
    return render_template('user.html', users=users, pager=pager)


if __name__ == '__main__':
    manager.run()
