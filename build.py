#!/usr/bin/env python3
"""Solid Homes Kasane redesign: builds every page from the crawled WordPress JSON
(/workspace/crawl) through new templates. Text is reused word for word; old markup,
classes and inline styles are discarded."""
import json,glob,re,os,html,hashlib,shutil
from bs4 import BeautifulSoup,NavigableString,Comment,Tag
CR='/workspace/crawl'; OUT='/workspace/alt-design-kasane'; BASE=''
P=[p for f in sorted(glob.glob(CR+'/pages[0-9].json')) for p in json.load(open(f))]
POSTS=json.load(open(CR+'/posts.json'))
E=html.escape
# --- claims guard (approved 24 Oct 2026): no year/family counts; use "since 2004"
def scrub_claims(s):
    import sys as _s,os as _o; _s.path.insert(0,_o.path.dirname(_o.path.abspath(__file__)))
    import claims_guard; return claims_guard.consent(claims_guard.scrub(s))

def imgname(u): return re.sub(r'\.[a-zA-Z]+$','',re.sub(r'.*/uploads/','',u).replace('/','-'))+'.webp'
UP=re.compile(r'(?i)(?:https?://(?:www\.)?emmelinekoh\.sg)?/wp-content/uploads/[^"\'\s)]+?\.(?:jpe?g|png|webp|gif)')
def img_url(u):
    if UP.fullmatch(u or ''):
        n=imgname(u); return BASE+'/assets/img/'+n if os.path.exists(OUT+'/assets/img/'+n) else None
    return u if (u or '').startswith('http') else None
def link(h):
    if not h: return '#'
    m=re.match(r'(?:https?://(?:www\.)?emmelinekoh\.sg)?/(?!/)(.*)',h)
    if m and not re.match(r'(wp-|feed)',m.group(1)): return BASE+'/'+m.group(1)
    if re.fullmatch(r'https?://(www\.)?emmelinekoh\.sg/?',h): return BASE+'/'
    return h
# ---------- extraction ----------
SKIP={'script','style','noscript','svg','button','input','select','textarea','iframe','option','label','form','canvas','video','audio','source','link','meta'}
INL={'a','strong','b','em','i','br','sup','sub','span','small','mark','abbr','code','u','time','s','del','ins','q','cite','label'}
BLOCKY={'div','p','section','article','header','footer','ul','ol','table','figure','h1','h2','h3','h4','h5','h6','details','blockquote','aside','main','nav','dl','li','img','hr','form','fieldset'}
def txt(n): return re.sub(r'\s+',' ',n.get_text(' ') if isinstance(n,Tag) else str(n)).strip()
def inline(n):
    out=[]
    for c in (n.children if isinstance(n,Tag) else [n]):
        if isinstance(c,Comment): continue
        if isinstance(c,NavigableString): out.append(E(re.sub(r'\s+',' ',str(c)))); continue
        if c.name in SKIP: continue
        if c.name=='br': out.append('<br>'); continue
        inner=inline(c)
        if c.name=='a': out.append(f'<a href="{E(link(c.get("href")))}"'+(' target="_blank" rel="noopener"' if (c.get('href') or '').startswith('http') and 'emmelinekoh' not in c.get('href','') else '')+f'>{inner}</a>')
        elif c.name in('strong','b'): out.append(f'<strong>{inner}</strong>')
        elif c.name in('em','i'): out.append(f'<em>{inner}</em>')
        elif c.name in('sup','sub','code'): out.append(f'<{c.name}>{inner}</{c.name}>')
        elif c.name in('span','div','small','p','li'): out.append(' '+inner+' ')
        else: out.append(inner)
    s=''.join(out); s=re.sub(r'\s+([,.;:!?)])',r'\1',s); s=re.sub(r'(<br>\s*)+$','',re.sub(r'^\s*(<br>\s*)+','',s.strip())); return re.sub(r'\s{2,}',' ',s)
def cls(n): return ' '.join(n.get('class',[])) if isinstance(n,Tag) else ''
def is_card(n):
    if not isinstance(n,Tag) or n.name not in('div','article','li','a','section'): return False
    toks=n.get('class',[])
    ok=any(re.fullmatch(r'(.*-)?card(-[a-z]+)?|[a-z]card(--[a-z]+)?|card|tile|project-item|post-card|nh-card|.*-item',t) and '__' not in t for t in toks)
    if not ok: return False
    if len(txt(n))>900: return False
    return not any(is_card(d) for d in n.find_all(['div','article','li','a','section']))
def is_stat(n):
    if not isinstance(n,Tag) or n.name not in('div','li','span'): return False
    ch=[c for c in n.children if isinstance(c,Tag)]
    if not 2<=len(ch)<=3 or any(c.name in('h1','h2','h3','ul','table','img') for c in ch): return False
    a=txt(ch[0]); b=txt(ch[1])
    c0=' '.join(ch[0].get('class',[]))
    return bool(a) and len(a)<=16 and len(b)<=90 and bool(b) and (re.search(r'[\d–\-—$%]',a) or c0 in('num','n','v','big','value','stat-num') or ch[0].name in('b','strong')) and len(txt(n))==len(' '.join(txt(c) for c in ch)) or False
def is_kv(n):
    if not isinstance(n,Tag): return False
    t=n.get('class',[])
    if not any('row' in x for x in t): return False
    ch=[c for c in n.children if isinstance(c,Tag)]
    return len(ch)==2 and all(len(txt(c))<200 for c in ch)
class X:
    def __init__(s): s.b=[]
    def add(s,*a): s.b.append(a)
    def walk(s,n):
        for c in list(n.children):
            if isinstance(c,Comment): continue
            if isinstance(c,NavigableString):
                t=re.sub(r'\s+',' ',str(c)).strip()
                if t and len(t)>1: s.add('p',E(t))
                continue
            s.node(c)
    def node(s,c):
        nm=c.name; k=cls(c)
        if nm=='form': return s.add('form',formfields(c))
        if nm in SKIP:
            if nm=='iframe' and 'google.com/maps' in (c.get('src') or ''): s.add('map',c.get('src'))
            return
        if nm=='nav' or re.search(r'\b(filter-tabs|category-links|search-bar|tr-anchor|hc-dots|breadcrumb)\b',k): return
        if is_card(c): return s.card(c)
        if is_stat(c):
            ch=[x for x in c.children if isinstance(x,Tag)]
            return s.add('stat',inline(ch[0]),inline(ch[1]),inline(ch[2]) if len(ch)>2 else '')
        if is_kv(c):
            ch=[x for x in c.children if isinstance(x,Tag)]; return s.add('kv',inline(ch[0]),inline(ch[1]))
        if re.search(r'(qa-box|quick-answer|d15-takeaway|verdict|callout|note|highlight)',k):
            sub=X(); sub.walk(c); return s.add('callout',sub.b)
        if nm in('h1','h2','h3','h4','h5','h6'):
            t=inline(c)
            if t: s.add('h',int(nm[1]),t)
            return
        if nm=='img':
            u=img_url(c.get('src'))
            if u: s.add('img',u,c.get('alt',''),'')
            return
        if nm=='figure':
            im=c.find('img')
            if im: im.extract()
            cap=inline(c)
            if im and img_url(im.get('src')): s.add('img',img_url(im.get('src')),im.get('alt',''),cap)
            elif cap: s.add('p',inline(cap))
            return
        if nm=='table':
            return s.add('table',table(c))
        if nm=='details':
            sm=c.find('summary'); q=inline(sm) if sm else ''
            if sm: sm.extract()
            sub=X(); sub.walk(c); return s.add('faq',q,sub.b)
        if nm in('ul','ol'):
            lis=c.find_all('li',recursive=False)
            if not lis:
                for x in c.children:
                    if isinstance(x,Tag): s.card(x) if x.name=='a' else s.node(x)
                return
            if lis and all(li.find('a') and li.find(['div','p','span']) and len(txt(li))>40 for li in lis):
                for li in lis: s.card(li)
                return
            items=[]
            for li in lis:
                if li.find(BLOCKY - {'li'}): 
                    sub=X(); sub.walk(li); items.append(('blocks',sub.b))
                else: items.append(('t',inline(li)))
            return s.add('list',nm,items)
        if nm=='dl':
            for dt in c.find_all('dt'):
                dd=dt.find_next_sibling('dd'); s.add('kv',inline(dt),inline(dd) if dd else '')
            return
        if nm=='blockquote': return s.add('quote',inline(c))
        if nm=='hr': return
        if nm=='a':
            if c.find(BLOCKY): sub=X(); sub.walk(c); s.b+=sub.b; return
            t=inline(c)
            if t: s.add('cta',link(c.get('href')),t, bool(re.search(r'btn|button|cta',k)))
            return
        da=[x for x in c.children if isinstance(x,Tag) and x.name=='a']
        if da and any(re.search(r'btn|button|cta',cls(x)) for x in da) and all((isinstance(x,Tag) and x.name in('a','br')) or (isinstance(x,NavigableString) and not str(x).strip()) or isinstance(x,Comment) for x in c.children):
            for x in da: s.add('cta',link(x.get('href')),inline(x),True)
            return
        if nm!='a' and len(da)>=2 and all(x.find(['span','div','strong','img','h3','h4']) or len(txt(x))>8 for x in da) and sum(len(txt(x)) for x in da)>=0.85*len(txt(c)) and (c.name in('ul','ol','div','nav','section') ) and not c.find('p'):
            for x in c.children:
                if isinstance(x,Tag): s.card(x) if x.name=='a' else s.node(x)
            return
        if (nm=='p' and not c.find(BLOCKY)) or (not c.find(BLOCKY) and not any(is_card(d) for d in c.find_all(['a','div','li','article']))):
            t=inline(c)
            if not t: return
            if re.search(r'(label|eyebrow|badge|pill|kicker|tag|d15-label|section-label)',k) and len(txt(c))<120: return s.add('eye',t)
            if re.search(r'(subheading|lead|d15-sub|intro|sub\b)',k): return s.add('lead',t)
            return s.add('p',t)
        s.walk(c)
    def card(s,c):
        im=c.find('img'); u=img_url(im.get('src')) if im else None
        a=c if c.name=='a' else c.find('a'); href=link(a.get('href')) if a else None
        hd=c.find(['h1','h2','h3','h4','h5','h6'])
        pieces=[]
        for el in c.find_all(string=True):
            if isinstance(el,Comment) or el.parent.name in SKIP: continue
            t=re.sub(r'\s+',' ',str(el)).strip()
            if not t: continue
            par=el.parent
            if hd and (par is hd or hd in par.parents): key='H'
            else: key=id(par)
            if pieces and pieces[-1][0]==key: pieces[-1][1].append(t)
            else: pieces.append([key,[t]])
        pieces=[(k,' '.join(v)) for k,v in pieces]
        tag='';title=''
        if hd:
            title=inline(hd); i=[k for k,_ in pieces].index('H') if 'H' in [k for k,_ in pieces] else 0
            pre=[t for k,t in pieces[:i]]; body=pre[1:] if pre else []
            if pre: tag=pre[0]
            body=body+[t for k,t in pieces[i+1:]]
        else:
            ts=[t for k,t in pieces]
            if len(ts)>=2 and len(ts[0])<=24: tag,title,body=ts[0],E(ts[1]),ts[2:]
            elif ts: title,body=E(ts[0]),ts[1:]
            else: body=[]
        s.add('card',title,[E(b) for b in body],href,u,E(tag))
def formfields(f):
    fl=[]
    for lab in f.find_all('label'):
        ctl=f.find(id=lab.get('for')) if lab.get('for') else lab.find(['input','select','textarea'])
        if ctl is None:
            w=lab.find_parent(['p','div']); ctl=w.find(['input','select','textarea']) if w else None
        if ctl is None or ctl.get('type')=='hidden': continue
        lt=inline(BeautifulSoup(str(lab),'html.parser').label) if True else ''
        opts=[txt(o) for o in ctl.find_all('option')] if ctl.name=='select' else []
        fl.append((txt(lab),ctl.name,ctl.get('type','text'),opts,ctl.get('name') or ctl.get('id') or 'field'))
    # checkbox with sibling text (CF7 acceptance)
    for cb in f.find_all('input',{'type':'checkbox'}):
        if any(x[4]==(cb.get('name') or cb.get('id')) for x in fl): continue
        w=cb.find_parent(['label','span','p','div']); t=txt(w) if w else ''
        if t: fl.append((t,'input','checkbox',[],cb.get('name') or 'consent'))
    sub=f.find(['button','input'],{'type':'submit'}) or f.find('button')
    st=(sub.get('value') or txt(sub)) if sub else 'Send'
    return fl,st
def r_form(fl,st):
    o=[]
    for lab,tg,ty,opts,nm in fl:
        if ty=='checkbox': o.append(f'<label class="chk"><input type="checkbox" name="{E(nm)}" required> {E(lab)}</label>')
        elif tg=='select': o.append(f'<label>{E(lab)}<select name="{E(nm)}">'+''.join(f'<option>{E(x)}</option>' for x in opts)+'</select></label>')
        elif tg=='textarea': o.append(f'<label>{E(lab)}<textarea name="{E(nm)}" rows="4"></textarea></label>')
        else: o.append(f'<label>{E(lab)}<input name="{E(nm)}" type="{E(ty if ty in ("email","tel","number","date","text") else "text")}"></label>')
    return f'<form class="mform rv" action="mailto:solidhomesbyemmeline@gmail.com" method="post" enctype="text/plain" data-mailto>{"".join(o)}<button class="btn gold" type="submit">{E(st)}</button></form>'
def table(t):
    rows=[]
    for tr in t.find_all('tr'):
        cells=''.join(f'<{c.name}>{inline(c)}</{c.name}>' for c in tr.find_all(['th','td']))
        rows.append(f'<tr>{cells}</tr>')
    return '<div class="tbl"><table>'+''.join(rows)+'</table></div>'
def extract(h):
    h=re.sub(r'(?s)<!--.*?-->','',h)
    soup=BeautifulSoup(h,'html.parser')
    for t in soup(['script','style','noscript']): t.decompose()
    x=X(); x.walk(soup); return x.b
# ---------- grouping ----------
def group(blocks):
    """merge consecutive cards/stats/kv/faq/img into compound blocks"""
    out=[]
    for b in blocks:
        t=b[0]
        m={'card':'cards','stat':'stats','kv':'kvs','img':'gallery','faq':'faqs'}.get(t)
        if m and out and out[-1][0]==m: out[-1][1].append(b)
        elif m: out.append((m,[b]))
        else: out.append(b)
    return out
def sections(blocks):
    hero={'eye':[],'title':None,'lead':[],'img':None,'ctas':[]}
    i=0; pre=[]
    hi=next((k for k,b in enumerate(blocks) if b[0]=='h' and b[1]==1),None)
    if hi is not None:
        # eyebrows directly before h1
        j=hi-1
        while j>=0 and blocks[j][0]=='eye': hero['eye'].insert(0,blocks[j][1]); j-=1
        pre=blocks[:j+1]; hero['title']=blocks[hi][2]; i=hi+1
        while i<len(blocks) and blocks[i][0] in('lead','p','eye','cta') and len(hero['lead'])<2 and not (blocks[i][0]=='p' and hero['lead'] and len(blocks[i][1])>400):
            b=blocks[i]
            if b[0]=='cta': hero['ctas'].append(b)
            elif b[0]=='eye': hero['eye'].append(b[1])
            else: hero['lead'].append(b[1])
            i+=1
        while i<len(blocks) and blocks[i][0]=='cta': hero['ctas'].append(blocks[i]); i+=1
    rest=pre+blocks[i:]
    for b in blocks:
        if b[0]=='img': hero['img']=b[1]; break
    secs=[]; cur={'title':None,'eye':[],'blocks':[]}
    for b in rest:
        if b[0]=='h' and b[1]<=2:
            if cur['title'] or cur['blocks']: secs.append(cur)
            cur={'title':b[2],'eye':[],'blocks':[]}
            if secs and not secs[-1]['blocks'] and not secs[-1]['title'] and secs[-1]['eye']: cur['eye']=secs.pop()['eye']
        elif b[0]=='eye' and not cur['blocks'] and cur['title'] is None: cur['eye'].append(b[1])
        else: cur['blocks'].append(b)
    if cur['title'] or cur['blocks'] or cur['eye']: secs.append(cur)
    # move trailing eyebrow of a section into next section's eyebrow
    for k in range(len(secs)-1):
        while secs[k]['blocks'] and secs[k]['blocks'][-1][0]=='eye' and secs[k+1]['title']:
            secs[k+1]['eye'].insert(0,secs[k]['blocks'].pop()[1])
    for s in secs: s['blocks']=group(s['blocks'])
    return hero,secs
# ---------- rendering ----------
def split_h(t,tag='h2',cls_=''):
    words=t.split(' ')
    if len(words)>=2 and '<' not in words[-1] and '>' not in words[-1]:
        return f'<{tag} class="dh {cls_}"><span class="s">{" ".join(words[:-1])}</span> <span class="o">{words[-1]}</span></{tag}>'
    return f'<{tag} class="dh {cls_}"><span class="s">{t}</span></{tag}>'
def r_blocks(bs,dark=False):
    o=[]
    for b in bs:
        t=b[0]
        if t=='p': o.append(f'<p class="rv">{b[1]}</p>')
        elif t=='lead': o.append(f'<p class="lead rv">{b[1]}</p>')
        elif t=='eye': o.append(f'<p class="lab rv">{b[1]}</p>')
        elif t=='h': o.append(f'<h{min(b[1]+1,5)} class="h{min(b[1],5)} rv">{b[2]}</h{min(b[1]+1,5)}>')
        elif t=='quote': o.append(f'<blockquote class="rv">{b[1]}</blockquote>')
        elif t=='table': o.append(f'<div class="rv">{b[1]}</div>')
        elif t=='form': o.append(r_form(*b[1]))
        elif t=='map': o.append(f'<div class="map rv"><iframe src="{E(b[1])}" loading="lazy" title="Map"></iframe></div>')
        elif t=='callout': o.append(f'<aside class="callout rv">{r_blocks(b[1])}</aside>')
        elif t=='cta': o.append(f'<p class="rv"><a class="{"btn gold" if b[3] else "tlink"}" href="{E(b[1])}">{b[2]}</a></p>')
        elif t=='list':
            lis=''.join(f'<li>{x[1]}</li>' if x[0]=='t' else f'<li>{r_blocks(x[1])}</li>' for x in b[2])
            o.append(f'<{b[1]} class="lst rv">{lis}</{b[1]}>')
        elif t=='cards': o.append(r_cards(b[1]))
        elif t=='stats':
            o.append('<div class="stats rv">'+''.join(f'<div class="st"><b>{s[1]}</b><span>{s[2]}</span>'+(f'<small>{s[3]}</small>' if s[3] else '')+'</div>' for s in b[1])+'</div>')
        elif t=='kvs': o.append('<dl class="kv rv">'+''.join(f'<div><dt>{k[1]}</dt><dd>{k[2]}</dd></div>' for k in b[1])+'</dl>')
        elif t=='faqs': o.append('<div class="faq">'+''.join(f'<details class="rv"><summary>{f[1]}</summary><div>{r_blocks(f[2])}</div></details>' for f in b[1])+'</div>')
        elif t=='gallery':
            ims=b[1]
            if len(ims)==1: o.append(f'<figure class="band par rv"><img src="{ims[0][1]}" alt="{E(ims[0][2])}" loading="lazy">'+'</figure>'+'<p class="imgnote">All images are artist\'s impressions.</p>')
            else: o.append('<div class="gal rv">'+''.join(f'<figure><img src="{m[1]}" alt="{E(m[2])}" loading="lazy">'+'</figure>' for m in ims)+'</div><p class="imgnote">All images are artist\'s impressions.</p>')
    return '\n'.join(o)
def r_cards(cs):
    o=[]
    for c in cs:
        title,body,href,img,tag=c[1:]
        inner=(f'<div class="ci"><img src="{img}" alt="" loading="lazy"></div>' if img else '')+(f'<span class="tag">{tag}</span>' if tag else '')+(f'<h3>{title}</h3>' if title else '')+''.join(f'<p>{x}</p>' for x in body)
        o.append(f'<a class="card rv" href="{E(href)}">{inner}<span class="arr" aria-hidden="true">→</span></a>' if href and href!='#' and '<a ' not in title else f'<div class="card rv">{inner}</div>')
    return f'<div class="cards {"has-img" if any(c[4] for c in cs) else ""}">'+''.join(o)+'</div>'
POOL=['grand-arrival','olive-lounge','maple-room','pes-lawn-view','infinity-lap-pool','leisure-pool','grand-lawn','cedar-room']
def pool(slug): return BASE+'/assets/img/'+POOL[int(hashlib.md5(slug.encode()).hexdigest(),16)%len(POOL)]+'.webp'
def r_hero(h,slug,kind,title_fallback):
    img=h['img'] or pool(slug)
    t=h['title'] or E(title_fallback)
    eye=' · '.join(h['eye'])
    lead=''.join(f'<p class="lead">{l}</p>' for l in h['lead'])
    ctas=''.join(f'<a class="btn {"gold" if k==0 else "ghost"}" href="{E(c[1])}">{c[2]}</a>' for k,c in enumerate(h['ctas']))
    return f'''<header class="phero phero--{kind}" style="--hero:url('{img}')"><div class="phero-bg par" aria-hidden="true"></div><div class="phero-in">
{f'<p class="lab">{eye}</p>' if eye else ''}{split_h(t,'h1','mega')}{lead}{f'<div class="ctas">{ctas}</div>' if ctas else ''}</div><div class="scroll-cue" aria-hidden="true"></div></header>'''
def r_sections(secs,kind):
    o=[];n=0
    for k,s in enumerate(secs):
        dark=k%2==1 and kind!='article'
        n+=1 if s['title'] else 0
        eye=' · '.join(s['eye'])
        head=''
        if s['title']:
            head=f'<div class="sh"><p class="lab rv">{f"{n:02d}"}{" · "+eye if eye else ""}</p>'+split_h(s['title'],'h2','rv')+'</div>'
        elif eye: head=f'<p class="lab rv">{eye}</p>'
        o.append(f'<section class="sec {"dark" if dark else "light"} room"><div class="sec-in">{head}{r_blocks(s["blocks"],dark)}</div></section>')
    return '\n'.join(o)
# ---------- chrome ----------
NAV=[('property-guides','Property Guides'),('new-launch-singapore','New Launches'),('upcoming-launches','Upcoming Launches'),('affordability-calculator','Affordability Calculator'),('about-us','About'),('contact-us','Contact')]
WA='https://wa.me/6582754135?text=Hi%20Emmeline%2C%20I%20found%20your%20website%20and%20would%20like%20a%20property%20consultation.'
DISC='''<p class="k-disc"><strong>Disclaimer:</strong> The information on this website is provided for general information only and does not constitute financial, legal, tax or investment advice. While reasonable care has been taken, prices, availability, project details and policies may change and should be verified independently before making any decision. Artist's impressions and AI-generated images are for illustration only.</p>'''
def head(title,extra=''):
    return f'''<!doctype html><html lang="en-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/chrome.css"><link rel="stylesheet" href="{BASE}/site.css">{extra}</head><body>'''
def nav():
    l=''.join(f'<a href="{BASE}/{s}/">{t}</a>' for s,t in NAV)
    return f'''<header class="k-nav" id="kNav"><a href="{BASE}/" class="k-brand" aria-label="Solid Homes by Emmeline Koh, home"><img src="{BASE}/assets/logo-on-dark.svg" alt="Solid Homes" width="200" height="46"></a>
<nav class="k-links" aria-label="Main navigation">{l}</nav>
<a class="k-cta" href="{WA}" target="_blank" rel="noopener">Book a Consultation</a>
<button class="k-burger" id="kBurger" aria-label="Open menu" aria-expanded="false" aria-controls="kMenu"><span></span><span></span><span></span></button></header>
<div class="k-menu" id="kMenu" hidden><nav aria-label="Mobile navigation">{l}<a href="{WA}" target="_blank" rel="noopener" class="k-menu-cta">Book a Consultation</a><a href="tel:+6582754135">Call 8275 4135</a></nav></div>'''
def foot():
    col=lambda h,items:f'<div><p class="k-fh">{h}</p><ul>'+''.join(f'<li><a href="{BASE}/{s}/">{t}</a></li>' for s,t in items)+'</ul></div>'
    return f'''<footer class="k-foot"><div class="k-fgrid"><div><img src="{BASE}/assets/logo-on-dark.svg" alt="Solid Homes" width="180" height="41"><p class="k-fdesc">Helping Singapore homeowners, investors and upgraders make smarter property decisions through strategy, data and experience in Singapore real estate since 2004.</p></div>
{col('Guides',[('property-guides','Buying Property'),('upgrade-property-singapore','Upgrading'),('new-launch-singapore','New Launches'),('property-investment-singapore','Investment')])}
{col('Explore',[('area-guides','Area Guides'),('school-guides','School Guides'),('mrt-guides','MRT Guides')])}
{col('Connect',[('about-us','About Emmeline'),('contact-us','Contact'),('privacy-policy','Privacy Policy')])}</div>
<p class="k-cea">Emmeline Koh, CEA R045542G, PropNex Realty Pte. Ltd. (L3008022J) · <a href="tel:+6582754135">8275 4135</a> · <a href="mailto:solidhomesbyemmeline@gmail.com">solidhomesbyemmeline@gmail.com</a></p>
{DISC}
<p class="k-rights">ALL RIGHTS RESERVED. 2026. Crafted and Designed by BK Han.</p>
</footer>
<script src="{BASE}/chrome.js" defer></script><script src="{BASE}/site.js" defer></script>'''
MAILFORM=f'''<form class="mform rv" action="mailto:solidhomesbyemmeline@gmail.com" method="post" enctype="text/plain" data-mailto>
<label>Name<input name="name" required autocomplete="name"></label><label>Mobile<input name="mobile" type="tel" required autocomplete="tel"></label>
<label>Email<input name="email" type="email" autocomplete="email"></label><label>Message<textarea name="message" rows="4"></textarea></label>
<label class="chk"><input type="checkbox" name="pdpa_consent" value="yes" required> <span>I consent to Emmeline Koh (PropNex) collecting and using my details to respond to this enquiry, per the <a href="/privacy-policy/">Privacy Policy</a>.</span></label><label class="chk"><input type="checkbox" name="marketing_consent" value="yes"> <span>I&#x27;d like to receive property updates and marketing from Emmeline Koh by WhatsApp, phone, SMS or email. I can withdraw anytime.</span></label>
<button class="btn gold" type="submit">Send enquiry</button></form>'''
# ---------- templates ----------
def classify(slug,isPost):
    if isPost: return 'article'
    return {'property-guides':'guides','new-launch-singapore':'launches','affordability-calculator':'calculator','about-us':'about','contact-us':'contact','thomson-reserve':'thomson'}.get(slug,'landing')
def page_title(t): return html.unescape(re.sub('<[^>]+>','',t))
def r_toc(secs):
    items=[s['title'] for s in secs if s['title']]
    if len(items)<3: return ''
    return '<nav class="toc" aria-label="On this page"><p class="lab">On this page</p><ol>'+''.join(f'<li><a href="#s{k+1}">{re.sub("<[^>]+>","",t)}</a></li>' for k,t in enumerate(items))+'</ol></nav>'
def add_ids(htm):
    k=[0]
    def f(m): k[0]+=1; return f'<section id="s{k[0]}" '+m.group(1)
    return re.sub(r'<section (class="sec [^"]*")',lambda m:f(m),htm)
def calculator(p):
    c=p['content']['rendered']
    scr=html.unescape(re.findall(r'(?s)<script[^>]*>(.*?)</script>',c)[0])
    scr=scr.replace('if(!EK_FORM_ID){unlock();return}','location.href="mailto:solidhomesbyemmeline@gmail.com?subject="+encodeURIComponent("Affordability calculator enquiry")+"&body="+encodeURIComponent("Name: "+$("g-name").value+"\\nMobile: "+$("g-mobile").value+"\\nEmail: "+$("g-email").value+"\\n\\n"+summary);unlock();$("ekc-ty").hidden=false;return;if(!EK_FORM_ID){unlock();return}',1)
    soup=BeautifulSoup(re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->','',c),'html.parser')
    root=soup.find(id='ekc')
    for t in root.find_all(True):
        keep={k:v for k,v in t.attrs.items() if k in('id','type','inputmode','min','max','required','value','for','role','hidden','aria-live','aria-hidden','tabindex','autocomplete','name','href','class','novalidate')}
        if 'class' in keep: keep['class']=[x for x in keep['class'] if x in('g','hint','warn','big','teaser','locked','hp','chk','card','btn','gold','wa','eyebrow','disc')]
        t.attrs=keep
        if t.name=='a' and t.get('href'): t['href']=link(t['href'])
    disc=soup.find(class_='disc')
    h2=root.find('h2'); eye=root.find(class_='eyebrow'); lead=h2.find_next_sibling('p')
    hero={'eye':[inline(eye)],'title':inline(h2),'lead':[inline(lead)],'img':BASE+'/assets/img/olive-lounge.webp','ctas':[('cta','#calc','See my estimate',True)]}
    h2.decompose(); eye.decompose(); lead.decompose()
    body=f'''{r_hero(hero,'calc','calculator','')}<section class="sec light calc" id="calc"><div class="sec-in"><div class="sh"><p class="lab rv">01 · Your numbers</p>{split_h('Run the numbers','h2','rv')}</div>
<div class="calc-wrap">{str(root)}</div>{('<div class="calc-disc">'+inline(disc)+'</div>') if False else ''}<div class="calc-disc">{str(disc).replace(' class="disc"','')}</div></div></section>
<script>{scr}</script>'''
    return body
def render(p,isPost):
    slug=p['slug']; kind=classify(slug,isPost); t=page_title(p['title']['rendered'])
    if kind=='calculator': return kind,calculator(p)
    blocks=extract(p['content']['rendered'])
    hero,secs=sections(blocks)
    if not hero['title']: hero['title']=E(t)
    if kind=='article':
        meta=f'<p class="lab">Insights · {E(p["date"][:10])}</p>'
        hero['eye']=[f'Insights · {p["date"][:10]}']+hero['eye']
        main=r_hero(hero,slug,'article',t)+f'<div class="art"><aside class="art-side">{r_toc(secs)}</aside><div class="art-body">'+add_ids(r_sections(secs,'article'))+'</div></div>'
        main+='<div class="prog" aria-hidden="true"><i></i></div>'
        return kind,main
    if kind in('guides','launches'):
        # hub: lift all cards into a filterable grid
        allcards=[c for s in secs for b in s['blocks'] if b[0]=='cards' for c in b[1]]
        search=f'<div class="hub-tools rv"><label class="hub-search"><span class="lab">Search {"guides" if kind=="guides" else "projects"}</span><input type="search" placeholder="Type a name, area or topic" data-filter></label><p class="hub-count" aria-live="polite"></p></div>'
        main=r_hero(hero,slug,'hub',t)+f'<div class="hub" data-hub>{search}'+r_sections(secs,kind)+'</div>'
        return kind,main
    if kind=='contact':
        main=r_hero(hero,slug,'split',t)+r_sections(secs,kind)+f'<section class="sec dark room" id="enquire"><div class="sec-in two"><div><p class="lab rv">Enquire</p>{split_h("Send an enquiry","h2","rv")}<p class="big rv"><a href="tel:+6582754135">8275 4135</a></p><p class="rv"><a href="mailto:solidhomesbyemmeline@gmail.com">solidhomesbyemmeline@gmail.com</a></p></div>{MAILFORM}</div></section>'
        return kind,main
    if kind=='about':
        return kind,r_hero(hero,slug,'split',t)+r_sections(secs,kind)
    if kind=='thomson':
        main=r_hero(hero,slug,'project',t)+r_toc(secs).replace('class="toc"','class="toc toc--bar"')+add_ids(r_sections(secs,kind))+f'<section class="sec dark room" id="tr-register"><div class="sec-in two"><div><p class="lab rv">Register</p>{split_h("Register for VVIP preview","h2","rv")}</div>{MAILFORM}</div></section>'
        return kind,main
    return kind,r_hero(hero,slug,'landing',t)+r_sections(secs,kind)
def visible_words(h):
    s=BeautifulSoup(re.sub(r'(?s)<!--.*?-->','',h),'html.parser')
    for t in s(['script','style','noscript','button','select','option','input','textarea','nav']): t.decompose()
    for t in s.select('.filter-tabs,.category-links,.search-bar,.tr-anchor,.hc-dots,.breadcrumb'): t.decompose()
    return re.findall(r"[A-Za-z0-9$%]+",s.get_text(' '))
from collections import Counter
def coverage(orig,new):
    a=Counter(w.lower() for w in visible_words(orig)); b=Counter(w.lower() for w in re.findall(r"[A-Za-z0-9$%]+",BeautifulSoup(new,'html.parser').get_text(' ')))
    tot=sum(a.values()); return 1.0 if not tot else sum(min(v,b[k]) for k,v in a.items())/tot
# Follow Emmeline section: compact, consistent social cards (replaces scraped markup)
ARR='<svg class="fl-arr" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M4 12L12 4M6 4h6v6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
IC={'Instagram':'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>',
'TikTok':'<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5M14 3c.5 2.5 2.5 4.5 5 4.5"/>',
'LinkedIn':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7.5 10v7M7.5 7v.01M11.5 17v-7M11.5 13a2.5 2.5 0 0 1 5 0v4"/>'}
L=[('Instagram','@emmelinekoh','https://www.instagram.com/emmelinekoh'),('TikTok','@emmelinekoh','https://www.tiktok.com/@emmelinekoh'),('LinkedIn','in/emmelinekoh','https://www.linkedin.com/in/emmelinekoh')]
FOLLOW='<div class="follow rv">'+''.join(f'<a class="fl" href="{u}" target="_blank" rel="noopener me" aria-label="Emmeline Koh on {n} ({h}), opens in a new tab"><svg class="fl-ic" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{IC[n]}</svg><span class="tag">{n}</span><span class="fl-h">{h}</span>{ARR}</a>' for n,h,u in L)+'</div>'
PAT=re.compile(r'(<p class="rv">Follow Emmeline</p>\s*)(?:<div class="cards ?">(?:(?!</div>).)*</div>|<p class="rv">(?:(?!</p>).)*instagram(?:(?!</p>).)*</p>)',re.S|re.I)
def fix_follow(h): return PAT.sub(lambda m:m.group(1)+FOLLOW,h)
if __name__=='__main__':
    report=[];built=[]
    for p in P+POSTS:
        isPost=p in POSTS
        path=re.sub(r'https?://(www\.)?emmelinekoh\.sg/','',p['link']).strip('/')
        if not path: continue
        ov=f'{OUT}/overrides/{p["slug"]}.html'
        if os.path.exists(ov): p=dict(p,content={'rendered':open(ov).read()})
        kind,main=render(p,isPost)
        t=page_title(p['title']['rendered'])
        doc=head(f'{E(t)} | Emmeline Koh')+nav()+f'<main class="pg pg--{kind}">{fix_follow(main)}</main>'+foot()+'</body></html>'
        os.makedirs(f'{OUT}/{path}',exist_ok=True); open(f'{OUT}/{path}/index.html','w').write(scrub_claims(doc))
        cov=coverage(p['content']['rendered'],main)
        report.append((path,kind,round(cov,3))); built.append((path,t,'post' if isPost else 'page'))
    lis=''.join(f'<a class="card rv" href="{BASE}/{pa}/"><span class="tag">Insights</span><h3>{E(t)}</h3><span class="arr" aria-hidden="true">→</span></a>' for pa,t,k in built if k=='post')
    hero={'eye':['All posts'],'title':'Insights','lead':[],'img':pool('insights'),'ctas':[]}
    os.makedirs(OUT+'/insights',exist_ok=True)
    open(OUT+'/insights/index.html','w').write(scrub_claims(head('Insights | Emmeline Koh')+nav()+'<main class="pg pg--hub">'+r_hero(hero,'insights','hub','Insights')+f'<section class="sec light"><div class="sec-in"><div class="cards">{lis}</div></div></section></main>'+foot()+'</body></html>'))
    # homepage: live home <main> content through the same section renderer
    raw=open(CR+'/home-live.html').read(); raw=raw[raw.find('<main'):raw.find('</main>')+7]
    hb=extract(raw); hh,hs=sections(hb)
    first={'title':hh['title'],'eye':hh['eye'],'blocks':group([('lead',l) for l in hh['lead']]+list(hh['ctas']))}
    homesecs=r_sections([first]+hs,'home')
    tpl=open(OUT+'/index.tpl.html').read()
    open(OUT+'/index.html','w').write(scrub_claims(tpl.replace('<!--NAV-->',nav()).replace('<!--FOOT-->',foot()).replace('<!--HOMEMAIN-->',homesecs)))
    report.append(('',"home",round(coverage(raw,homesecs),3)))
    json.dump(report,open(CR+'/coverage.json','w')); json.dump(built,open(CR+'/pages-built.json','w'))
    from collections import Counter as C
    print(C(k for _,k,_ in report)); low=[r for r in report if r[2]<0.97]; print('low coverage',len(low)); print(sorted(low,key=lambda r:r[2])[:25])
    import subprocess;subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'launches.py')],check=True)
    subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'postprocess.py'),OUT],check=True)
