import zipfile, re, sys, json
from xml.etree import ElementTree as ET

A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
P='{http://schemas.openxmlformats.org/presentationml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

path=sys.argv[1]
z=zipfile.ZipFile(path)

# slide order
pres=ET.fromstring(z.read('ppt/presentation.xml'))
rels=ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
rmap={c.get('Id'):c.get('Target') for c in rels}
order=[]
for sid in pres.find(P+'sldIdLst'):
    t=rmap[sid.get(R+'id')].split('/')[-1]
    order.append((sid.get('id'), t))

# sections (p14 ext)
sections=[]
for ext in pres.iter():
    if ext.tag.endswith('}sectionLst'):
        for s in ext:
            ids=[c.get('id') for c in s.iter() if c.tag.endswith('}sldId')]
            sections.append((s.get('name'), ids))

def shape_texts(sp):
    out=[]
    for tx in sp.iter(A+'p'):
        t=''.join(n.text or '' for n in tx.iter(A+'t'))
        if t.strip(): out.append(t.strip())
    return out

def slide_info(fn):
    root=ET.fromstring(z.read('ppt/slides/'+fn))
    title=None; body=[]
    for sp in root.iter(P+'sp'):
        ph=None
        for x in sp.iter(P+'ph'): ph=x.get('type')
        txts=shape_texts(sp)
        if ph in ('title','ctrTitle') and txts and title is None:
            title=' '.join(txts)
        else:
            body+=txts
    if title is None and body: title=body[0]
    # notes
    notes=''
    nrp='ppt/slides/_rels/%s.rels'%fn
    try:
        rr=ET.fromstring(z.read(nrp))
        for c in rr:
            if 'notesSlide' in (c.get('Type') or ''):
                np='ppt/notesSlides/'+c.get('Target').split('/')[-1]
                nroot=ET.fromstring(z.read(np))
                ns=[]
                for sp in nroot.iter(P+'sp'):
                    ph=None
                    for x in sp.iter(P+'ph'): ph=x.get('type')
                    if ph=='body': ns+=shape_texts(sp)
                notes=' / '.join(ns)
    except KeyError: pass
    return title or '', body, notes

data=[]
for i,(sid,fn) in enumerate(order,1):
    t,b,n=slide_info(fn)
    data.append(dict(n=i, sid=sid, file=fn, title=t, body=b, notes=n))

json.dump(dict(sections=sections, slides=data), open(sys.argv[2],'w'), ensure_ascii=False, indent=1)
print('slides in order:', len(order))
print('sections:', len(sections))
for name,ids in sections: print('  -', name, len(ids))
