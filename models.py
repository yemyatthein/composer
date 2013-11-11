from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost:3306/cmprdb'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


class Collection(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    desc = db.Column(db.String(120))
    created_date = db.Column(db.DateTime())
    modified_date = db.Column(db.DateTime())

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    created_by = db.relationship('User', backref=db.backref('collections', lazy='dynamic'))

    def __init__(self, name, desc='', created_by=None):
        from datetime import datetime as dt
        self.name = name
        self.desc = desc
        self.created_by = created_by
        self.created_date = dt.utcnow()

    def __repr__(self):
        return '%s (%s)' % (self.name, (self.desc[:10] + '...') if len(self.desc) > 10 else self.desc)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def __init__(self, name, email, password=None, first_name=None, last_name=None):
        self.name = name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '%s %s' % (self.first_name, self.last_name)

class CollectionGroup(db.Model):
    gid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    collection_id = db.Column(db.Integer, db.ForeignKey('collection.cid'))
    collection = db.relationship('Collection', backref=db.backref('collection_groups', lazy='dynamic'))

    def __init__(self, name, collection):
        self.name = name
        self.collection = collection

    def __repr__(self):
        return self.name

class Resource(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(100))
    desc = db.Column(db.String(500))
    image_url = db.Column(db.String(100))
    created_date = db.Column(db.DateTime())

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    created_by = db.relationship('User', backref=db.backref('resources', lazy='dynamic'))
        
    cgroup_id = db.Column(db.Integer, db.ForeignKey('collection_group.gid'))
    cgroup = db.relationship('CollectionGroup', backref=db.backref('resources', lazy='dynamic'))

    collection_id = db.Column(db.Integer, db.ForeignKey('collection.cid'))
    collection = db.relationship('Collection', backref=db.backref('resources', lazy='dynamic'))

    def __init__(self, title, url='', desc='', image_url='', created_by=None, cgroup=None, collection=None):
        from datetime import datetime as dt
        self.title = title
        self.url = url
        self.desc = desc
        self.image_url = image_url
        self.created_by = created_by
        self.cgroup = cgroup
        self.collection = collection
        self.created_date = dt.utcnow()
        
    def __repr__(self):
        return self.title

class ResourceRelation(db.Model):
    rlid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    # Supposed to be foreign key
    from_resource_id = db.Column(db.Integer)
    
    from_group_id = db.Column(db.Integer, db.ForeignKey('collection_group.gid'))
    from_group = db.relationship('CollectionGroup', backref=db.backref('relations', lazy='dynamic'))
    
    to_resource_id = db.Column(db.Integer, db.ForeignKey('resource.rid'))
    to_resource = db.relationship('Resource', backref=db.backref('related_from', lazy='dynamic'))
    
    def __init__(self, name, from_resource_id, from_group, to_resource):
        self.name = name
        self.from_resource_id = from_resource_id
        self.from_group = from_group
        self.to_resource = to_resource
        
    def __repr__(self):
        return self.name
