from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, HiddenField
from wtforms.validators import DataRequired

class MyForm(Form):
    name = TextField('content', validators=[DataRequired()])

class NewCollectionForm(Form):
    cname = TextField('Collection Name', validators=[DataRequired()])
    desc = TextAreaField('Description')
    
class NewGroupForm(Form):
    gname = TextField('Group Name', validators=[DataRequired()])
    
class NewResourceForm(Form):
    url = TextField('URL', validators=[DataRequired()])
    title = TextField('Title', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    image_url = HiddenField('Image')
    
class NewRelationForm(Form):
    relation_name = TextField('Relation Name', validators=[DataRequired()])
    