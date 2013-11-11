from flask import Flask, render_template, url_for, request, jsonify
from forms import NewCollectionForm, NewGroupForm, NewResourceForm, NewRelationForm
from models import db, User, Collection, CollectionGroup, Resource, ResourceRelation
from sqlalchemy import and_, not_, or_

app = Flask(__name__)

import logging
#logging.basicConfig(filename='sys.log',level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_collection', methods=['GET', 'POST'])
def create_collection():
    user = User.query.first()
    form = NewCollectionForm(request.form, csrf_enabled=False)
    if request.method == 'POST':
        if form.validate():
            cl = Collection(request.form['cname'], request.form['desc'], created_by=user)
            db.session.add(cl)
            db.session.commit()
            form = NewCollectionForm(csrf_enabled=False)
    return render_template('create_collection.html',form=form)

@app.route('/all_collection', methods=['GET'])
def browse_collection():
    cls = Collection.query.all()
    image_dict = {}
    for c in cls:
        rel = Resource.query.filter_by(collection_id=c.cid).all()
        imgs = [x.image_url for x in rel if str(x.image_url) is not '']
        imgs = imgs[:3]
        image_dict[c.cid] = imgs
    return render_template('browse_collection.html',cls=cls, idict=image_dict)

@app.route('/one_collection/<cid>', methods=['GET'])
def view_collection(cid):
    cl = Collection.query.filter_by(cid=cid).first()
    groups = CollectionGroup.query.filter_by(collection_id=cid).all()
    group_res_dict = {}
    for group in groups:
        rel_resources = Resource.query.filter_by(cgroup_id=group.gid, collection_id=cl.cid).all()
        group_res_dict[group.gid] = rel_resources
    return render_template('one_collection.html',cl=cl, groups=groups, group_resources=group_res_dict)

@app.route('/new_group/<cid>', methods=['GET', 'POST'])
def create_group(cid):
    form = NewGroupForm(request.form, csrf_enabled=False)
    collection = Collection.query.filter_by(cid=cid).first()
    if request.method == 'POST':
        if form.validate():
            cg = CollectionGroup(request.form['gname'], collection)
            db.session.add(cg)
            db.session.commit()
            form = NewGroupForm(csrf_enabled=False)
    return render_template('create_group.html', form=form, cl=collection)
    
@app.route('/new_resource/<cid>/<gid>', methods=['GET', 'POST'])
def create_resource(cid, gid):
    form = NewResourceForm(csrf_enabled=False)
    creator = User.query.first()
    collection = Collection.query.filter_by(cid=cid).first()
    group = CollectionGroup.query.filter_by(gid=gid).first()
    if request.method == 'POST':
        res = Resource(request.form['title'], request.form['url'], request.form['desc'], request.form['image_url'], created_by=creator, cgroup=group, collection=collection)
        db.session.add(res)
        db.session.commit()
    return render_template('create_resource.html', form=form, cid=cid, gid=gid)
    

@app.route('/get_relation_names', methods=['GET'])
def ajax_get_relation_names():
    rid = request.args.get('rid', 0, type=str)
    rls = [r.name for r in ResourceRelation.query.filter_by(from_resource_id=rid).all()]
    return jsonify(relation_names=rls)
    
@app.route('/extract_webinfo', methods=['GET'])
def ajax_extract_webpage_info():
    import urllib2
    from BeautifulSoup import BeautifulSoup
    from urlparse import urlparse
    from PIL import Image
    import io
    
    url = request.args.get('url', 0, type=str)
    page = BeautifulSoup(urllib2.urlopen(url))
    title = page.find('title')
    desc = page.find('meta', {'name': ['Description', 'description']})
    if desc:
        desc = desc['content']
    else:
        ptags = page.findAll('p')
        max_length = 0
        for i in xrange(0, len(ptags)):
            if i >= len(ptags):
                break
            pstring = ptags[i].string
            if not pstring:
                continue
            if len(pstring) > max_length:
                desc = pstring
                max_length = len(pstring)
    images = page.findAll('img')
    images = [x['src'] for x in images if x.has_key('src')]
    #logging.debug(len(images))
    refined = []
    for x in images:
        try:
            fd = urllib2.urlopen(x)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)
            if im.size[0] > 50:
                refined.append(x)
        except:
            pass
    images = refined
    img1 = images[0] if images else ''
    #logging.debug('REFINED++>')
    #logging.debug(images)
    url_info = urlparse(url)
    if 'youtube' in url_info.netloc:
        images = []
        vid = url_info.query.split('&')[0].split('=')[1]
        images = ['http://img.youtube.com/vi/%s/hqdefault.jpg' % vid]
        img1 = images[0]
        
    return jsonify(title=title.string, desc=desc, img=img1, images=images[:25])

@app.route('/one_resource/<rid>', methods=['GET'])
def view_resource(rid):
    resource = Resource.query.filter_by(rid=rid).first()
    related_resources = ResourceRelation.query.filter_by(from_resource_id=rid).all()
    from_resources = ResourceRelation.query.filter_by(to_resource_id=rid).all()
    
    final_rel_resources = {}
    for rrs in related_resources:
        key = rrs.name
        value = rrs.to_resource
        if key in final_rel_resources:
            final_rel_resources[key].append(value)
        else:
            final_rel_resources[key] = [value]
    
    final_from_resources = []
    for rrs in from_resources:
        key = rrs.name
        from_res_id = rrs.from_resource_id
        tmp = Resource.query.filter_by(rid=from_res_id).first()
        final_from_resources.append(tmp)
    return render_template('view_resource.html', resource=resource, related=final_rel_resources, from_related=final_from_resources)

@app.route('/add_relation/<rid>/<gid>/<cid>', methods=['GET', 'POST'])
def add_relation(rid, gid, cid):
    form = NewRelationForm(csrf_enabled=False)
    temp = Resource.query.filter(and_(Resource.collection_id.like(cid), not_(Resource.rid.like(rid)))).all()
    available_resources = []
    for rs in temp:
        ax = ResourceRelation.query.filter(or_(and_(ResourceRelation.to_resource_id.contains(rs.rid), ResourceRelation.from_resource_id.contains(rid)), and_(ResourceRelation.from_resource_id.contains(rs.rid), ResourceRelation.to_resource_id.contains(rid)))).all()
        if len(ax) > 0:
            continue
        available_resources.append(rs) 
    if request.method == 'POST':
        rlist = request.form.getlist('resources')
        group = CollectionGroup.query.filter_by(gid=gid).first()
        for trid in rlist:
            to_resource = Resource.query.filter_by(rid=trid).first()
            rrl = ResourceRelation(request.form['relation_name'], rid, group, to_resource)
            db.session.add(rrl)
            db.session.commit()
    return render_template('add_relation.html', form=form, resources=available_resources, rid=rid, gid=gid, cid=cid)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
