#!/usr/bin/env python3
"""Upcoming launches: generates one page per upcoming project / awarded site, the /upcoming-launches/ hub,
adds the early-registration form to existing upcoming pages, and adds 'Upcoming Launches' to the nav.
Data: launches/launches.json. Idempotent. Run after build.py, before postprocess.py."""
import json,os,re,html,sys
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
from build import head,nav,foot,split_h,BASE,scrub_claims
E=lambda s:html.escape(str(s),quote=True)
DATA=json.load(open(f'{D}/launches/launches.json'))
NEW,EX=DATA['new'],DATA['existing']
TODAY='30 Oct 2026'; TODAY_ISO='2026-10-30'
ALL=sorted([dict(x,new=True) for x in NEW]+[dict(x,new=False) for x in EX],key=lambda x:x['sort'])
UNITS=['1 Bedroom','2 Bedroom','3 Bedroom','4 Bedroom','5 Bedroom / Penthouse','Not sure yet']
CSS=f'<link rel="stylesheet" href="{BASE}/launches.css">'
JS=f'<script src="{BASE}/reg.js" defer></script>'
IMGNOTE="<p class=\"imgnote rv\">All images are artist's impressions.</p>"
def consent(proj):
    return (f'<label class="chk"><input type="checkbox" name="pdpa_consent" value="yes" required> <span>I consent to Emmeline Koh (CEA R045542G), PropNex Realty Pte. Ltd., '
            f'collecting and using my name, mobile and email to contact me by phone, SMS, WhatsApp or email about {E(proj)}, including brochures, preview dates and price lists. '
            f'I can withdraw my consent anytime by messaging 8275 4135 or emailing solidhomesbyemmeline@gmail.com. See the <a href="{BASE}/privacy-policy/">Privacy Policy</a>.</span></label>')
def form(current=None):
    if current:
        pl=(f'<label><input type="checkbox" name="project" value="{E(current)}" checked> {E(current)}</label>'
            '<label><input type="checkbox" name="project" value="Other upcoming launches"> Other upcoming launches too</label>')
        cls='opts'; ctext=current
    else:
        pl=''.join(f'<label><input type="checkbox" name="project" value="{E(x["name"])}"> {E(x["name"])}</label>' for x in ALL)
        cls='opts plist'; ctext='the project(s) I selected'
    ut=''.join(f'<label><input type="checkbox" name="unit_type" value="{u}"> {u}</label>' for u in UNITS)
    return (f'<form class="mform reg rv" data-reg novalidate>'
      '<label>Name<input name="name" required autocomplete="name"></label>'
      '<label>Mobile<input name="mobile" type="tel" required autocomplete="tel" inputmode="tel" pattern="[+0-9 ()-]{8,}"></label>'
      '<label>Email<input name="email" type="email" required autocomplete="email"></label>'
      f'<fieldset><legend>Project(s)</legend><div class="{cls}">{pl}</div></fieldset>'
      f'<fieldset><legend>Unit type</legend><div class="opts">{ut}</div></fieldset>'
      '<input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">'
      f'{consent(ctext)}<button class="btn gold" type="submit">Register early</button><p class="reg-msg" role="status" aria-live="polite"></p></form>')
def regsec(current=None,title='Register early'):
    w=title.split(); 
    return ('<!--reg--><section class="sec dark room" id="register"><div class="sec-in two"><div><p class="lab rv">Early registration</p>'
      f'<h2 class="dh rv"><span class="s">{E(" ".join(w[:-1]))}</span> <span class="o">{E(w[-1])}</span></h2>'
      '<p class="rv">Register once and I will send you the brochure, floor plans, preview dates and price list as soon as the developer releases them. No obligation.</p>'
      '<p class="rv"><a href="tel:+6582754135">8275 4135</a> · <a href="mailto:solidhomesbyemmeline@gmail.com">solidhomesbyemmeline@gmail.com</a></p>'
      f'</div>{form(current)}</div></section><!--/reg-->')
def hero(lab,title,lead):
    w=title.split(' ',1)
    h=f'<span class="s">{E(w[0])}</span>'+(f' <span class="o">{E(w[1])}</span>' if len(w)>1 else '')
    return (f'<header class="phero phero--plain"><div class="phero-in"><p class="lab">{E(lab)}</p><h1 class="dh mega">{h}</h1>'
            f'<p class="lead">{E(lead)}</p><p class="lead">By Emmeline Koh · Last updated: {TODAY}</p></div></header>')
GRP={'named':'Upcoming launch','gls':'Land awarded (GLS)','enbloc':'Collective sale'}
def page(x):
    kindtxt={'EC':'executive condominium','Condo':'private condominium','Mixed':'redevelopment'}[x['kind']]
    lead=f'{x["location"]}. An upcoming {kindtxt} by {x["developer"]}. Upcoming project, details TBC: name, unit mix, prices and launch date are still to be confirmed by the developer.'
    if x['group']=='named': lead=f'{x["location"]}. An upcoming {kindtxt} by {x["developer"]}. {x["status"]}. Unit mix, prices and showflat details are still to be confirmed.'
    st=[(x['units'],'Estimated units'),(x['psf'],'Land price psf ppr'),(x['bid'],'Winning bid' if x['group']!='enbloc' else 'Sale price'),(x['preview'],'Expected preview')]
    stats='<div class="stats rv">'+''.join(f'<div class="st"><b>{E(a)}</b><span>{E(b)}</span></div>' for a,b in st)+'</div>'
    kv=[('Status',x['status']),('Location',x['location']),('Developer',x['developer']),('Winning bid' if x['group']!='enbloc' else 'Collective sale price',x['bid']),
        ('Land price (psf ppr)',x['psf']),('Estimated units',x['units']),('Tenure',x['tenure']),('Nearest MRT',x['mrt']),
        ('Awarded' if x['group']!='enbloc' else 'Sale agreed',x.get('award','TBC')),('Expected preview',x['preview']),('Unit mix, prices' if x['group']=='named' else 'Project name, unit mix, prices','TBC')]
    kvh='<dl class="kv rv">'+''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a,b in kv)+'</dl>'
    ext=''.join(f'<p class="rv">{E(t)}</p>' for t in x.get('extra',[]))
    src='<p class="srcs rv">Sources: '+'; '.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(l)}</a>' for l,u in x['src'])+'. "Approx., OneMap" means a straight-line distance I measured on OneMap from the road, not a walking distance; the exact site boundary is not checked. Facts marked "reported" come from news or industry sources and are not yet confirmed by the developer.</p>'
    main=(hero(f'{GRP[x["group"]]} · {x["status"]}',x['name'],lead)+
      f'<section class="sec light room"><div class="sec-in">{stats}</div></section>'
      f'<section class="sec dark room"><div class="sec-in"><div class="sh"><p class="lab rv">01</p>{split_h("Key facts","h2","rv")}</div>{kvh}{ext}</div></section>'
      f'<section class="sec light room"><div class="sec-in"><div class="sh"><p class="lab rv">02</p>{split_h("What happens next","h2","rv")}</div>'
      '<p class="rv">Upcoming project, details TBC. The developer still has to release the project name, design, unit mix, prices and preview date. Register below and I will send you the brochure and preview details once they are out.</p>'
      f'<p class="rv">See every project I am tracking on the <a href="{BASE}/upcoming-launches/">Upcoming Launches</a> page.</p>{src}{IMGNOTE}</div></section>'+regsec(x['name']))
    title=f'{x["name"]}: {"Upcoming New Launch" if x["group"]=="named" else "Upcoming Project"}, Register Early'
    desc=f'{x["name"]}, {x["location"]}: {x["status"]}. Developer {x["developer"]}, {x["units"]} units est., land price {x["psf"]} psf ppr. Register early with Emmeline Koh (PropNex).'
    return head(f'{E(title)} | Emmeline Koh',f'<meta name="description" content="{E(desc)}"><link rel="canonical" href="https://emmelinekoh.sg/{x["slug"]}/">'+CSS)+nav()+f'<main class="pg pg--landing">{main}</main>'+foot()+JS+'</body></html>'
def hub():
    rows=''.join(f'<tr><td><a href="{BASE}/{x["slug"]}/">{E(x["name"])}</a></td><td>{E(x["kind"])}</td><td>{E(x["status"])}</td><td>{E(x["preview"])}</td></tr>' for x in ALL)
    tbl=f'<div class="rv"><div class="tbl"><table><tr><th>Project / site</th><th>Type</th><th>Status</th><th>Expected preview</th></tr>{rows}</table></div></div>'
    gls=open(f'{D}/launches/gls-lists.html').read()
    lead='Every Singapore new launch and recently awarded land site I am tracking, with its status and expected preview date. Register once to get brochures and preview details first.'
    main=(hero(f'Updated {TODAY} · {len(ALL)} projects and sites','Upcoming Launches',lead)+
      f'<section class="sec light room"><div class="sec-in"><div class="sh"><p class="lab rv">01</p>{split_h("Status and preview dates","h2","rv")}</div>'
      '<p class="rv">Dates marked "reported" or "target" come from news and industry sources and can change; developers confirm them closer to launch. TBC means not announced yet. Sorted by expected preview.</p>'
      f'{tbl}<p class="srcs rv">Main sources: <a href="https://www.ura.gov.sg/land-sales/current-ura-gls-sites/" target="_blank" rel="noopener">URA GLS</a>, HDB EC tender results, <a href="https://www.propkaki.com/singapore-property-research/gls-sites-and-tender-results" target="_blank" rel="noopener">PropKaki GLS table</a>, <a href="https://newlaunchradar.sg/projects" target="_blank" rel="noopener">New Launch Radar</a>, The Straits Times, The Business Times and EdgeProp. Each project page lists its own sources.</p>{IMGNOTE}</div></section>'
      +regsec(None,'Register early for upcoming launches')+gls)
    desc='Upcoming Singapore new launches and awarded GLS land sites, with status and expected preview dates. Register early with Emmeline Koh (PropNex) for brochures.'
    return head('Upcoming New Launches Singapore 2026–2027: Status, Preview Dates, Register Early | Emmeline Koh',f'<meta name="description" content="{E(desc)}"><link rel="canonical" href="https://emmelinekoh.sg/upcoming-launches/">'+CSS)+nav()+f'<main class="pg pg--landing">{main}</main>'+foot()+JS+'</body></html>'
NAVA=f'<a href="{BASE}/new-launch-singapore/">New Launches</a>'; NAVU=f'<a href="{BASE}/upcoming-launches/">Upcoming Launches</a>'
def fixnav(s): return s if NAVU in s else s.replace(NAVA,NAVA+NAVU)
if __name__=='__main__':
    g=f'{D}/launches/gls-lists.html'
    if not os.path.exists(g):  # one-time: keep the GLS confirmed / reserve lists from the old hub
        s=open(f'{D}/upcoming-launches/index.html').read(); secs=re.findall(r'(?s)<section class="sec [^"]*">.*?</section>',s)
        keep=[x for x in secs if 'Confirmed List' in x or 'Reserve List' in x]; assert len(keep)==2
        open(g,'w').write('\n'.join(keep).replace('<p class="lab rv">02</p>','<p class="lab rv">03</p>').replace('<p class="lab rv">03</p>','<p class="lab rv">04</p>',1) if False else '\n'.join(keep))
    for x in NEW:
        os.makedirs(f'{D}/{x["slug"]}',exist_ok=True); open(f'{D}/{x["slug"]}/index.html','w').write(scrub_claims(page(x)))
    open(f'{D}/upcoming-launches/index.html','w').write(scrub_claims(hub()))
    for x in EX:
        p=f'{D}/{x["slug"]}/index.html'; s=open(p).read()
        s=re.sub(r'(?s)<!--reg-->.*?<!--/reg-->','',s); s=re.sub(r'(?s)<!--upd-->.*?<!--/upd-->','',s)
        s=s.replace('</main>',regsec(x['name'])+'</main>',1)
        if x.get('update'): s=re.sub(r'(</header>)',lambda m:m.group(1)+f'<!--upd--><section class="sec light room"><div class="sec-in"><p class="upd rv">{E(x["update"])} <a href="{E(x["upd_src"])}" target="_blank" rel="noopener">Read the URA release</a>.</p></div></section><!--/upd-->',s,count=1)
        if CSS not in s: s=s.replace('</head>',CSS+'</head>',1)
        if JS not in s: s=s.replace('</body>',JS+'</body>',1)
        open(p,'w').write(s)
    import glob
    for p in glob.glob(f'{D}/*/index.html')+[f'{D}/index.html']:
        s=open(p).read(); t=fixnav(s)
        if t!=s: open(p,'w').write(t)
    sm=f'{D}/sitemap.xml'; s=open(sm).read()
    add=''.join(f'<url><loc>https://emmelinekoh.sg/{x["slug"]}/</loc><lastmod>{TODAY_ISO}</lastmod></url>\n' for x in NEW if f'emmelinekoh.sg/{x["slug"]}/<' not in s)
    if add: open(sm,'w').write(s.replace('</urlset>',add+'</urlset>'))
    print('pages',len(NEW),'existing updated',len(EX))
