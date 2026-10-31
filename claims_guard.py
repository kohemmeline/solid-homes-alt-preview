"""Claims guard (approved by Emmeline 24 + 30 Oct 2026). Strips unverified stats
(15+ years, 500+ families, $250M+, since 2009, 'independent' as a self-description),
and the sample homepage testimonials (Alex & Mei Ling, The Tan Family).
Used by build.py (scrub_claims) and postprocess.py. Idempotent."""
import re
AP="(?:’|'|&#8217;|&rsquo;)"
R=[
 # bios
 (r'agent with (?:more than|over) 15 years of experience advising','agent advising'),
 (r'With (?:more than|over) 15 years in Singapore real estate, I'+AP+r've helped hundreds of families make property decisions',"I help families make property decisions"),
 (r'I'+AP+r've been in Singapore real estate for (?:more than|over) 15 years\.',"I’ve been in Singapore real estate since 2004."),
 (r'(grounded in |through strategy, data and )15\+ years of experience',r'\1experience in Singapore real estate since 2004'),
 (r'\s*·\s*15\+ years(?=\s*<)',''),
 # chips / stat blocks / stat rows
 (r'<span class="(?:cred|credential)-chip"[^>]*>\s*(?:15\+ Years|500\+ Famil[^<]*|\$\s?250\s?M\+[^<]*)</span>\s*(?:<br\s*/?>)?\s*',''),
 (r'<span[^>]*>\s*15\+ Years\s*</span>\s*(?:<br\s*/?>)?\s*',''),
 (r'<div class="stat-block">\s*<p class="stat-block__number">(?:15\+|500\+|\$\s?250\s?M\+)</p>.*?</div>\s*',''),
 (r'<div class="st"><b>(?:15\+|500\s?\+|\$\s?250\s?M\+)</b><span>[^<]*</span></div>',''),
 (r'(?:15\+ Years|500\+ Families Helped|\$\s?250\s?M\+ Transactions)\s*<br\s*/?>\s*(?:\|\s*<br\s*/?>\s*)?',''),
 # generic fallbacks
 (r'(?:more than|over) 15 years(?: of experience)?','experience in Singapore real estate since 2004'),
 (r'15\+ [Yy]ears(?: of experience)?','experience in Singapore real estate since 2004'),
 (r'[Hh]undreds of families','families'),
 (r'500\+ (?:families|clients|homeowners)(?: (?:&amp; |&#038; |and )?(?:investors )?(?:helped|advised|served))?','clients'),
 (r'\$\s?250\s?M\+(?: (?:in )?(?:transactions|transaction value)(?: facilitated)?)?',''),
 (r'<section class="sec-warm">\s*<div class="wrap-sm txt-c">\s*<p[^>]*>What Clients Say</p>.*?</section>',''),
 # sample testimonials (homepage) -> keep the bio block, retitle with existing nav wording
 (r'\s*<p class="rv">What Clients Say</p>',''),
 (r'<h2 class="dh rv"><span class="s">Real feedback from real</span> <span class="o">clients</span></h2>','<h2 class="dh rv"><span class="s">About</span> <span class="o">Emmeline</span></h2>'),
 (r'(?:<p class="rv">“</p>\s*(?:<p class="rv">[^<]*</p>\s*){4})+',''),
 # --- numeric scores with stars (approved 30 Oct: "Remove the 8.6/10 scores")
 # raw WP verdict score block
 (r'<div class="score">\s*<div class="n">[^<]*</div>\s*<div class="of">[^<]*</div>\s*<div class="stars">[^<]*</div>\s*</div>\s*',''),
 # output: single-score stats row (whole wrapper), then any leftover score entry
 (r'\s*<div class="stats rv"><div class="st"><b>[\d.]+\s*/\s*10\s*★*</b><span>[^<]*</span></div></div>',''),
 (r'<div class="st"><b>[\d.]+\s*/\s*10\s*★*</b><span>[^<]*</span></div>',''),
 (r'<div class="st"><b>[^<]*★[^<]*</b><span>[^<]*</span></div>',''),
 (r'\s*<div class="stats rv">\s*</div>',''),
 # headings: keep the summary text, drop the "assessed" framing
 (r'(<h[1-6][^>]*>)\s*(?:Independently\s+)?assessed by Emmeline\s*(</h[1-6]>)',r'\1Emmeline’s view\2'),
 (r'(?:Independently\s+)?assessed by Emmeline','Emmeline’s view'),
 (r'\s*[\d.]+\s*/\s*10\s*★+',''),
 (r'★+',''),
 # --- 30 Oct (approved "Update the site's AI summary"): 'independent' as a description of her, wrong start year
 (r'since 2009','since 2004'),
 (r'\b(i)ndependent\s+(guidance|analysis|advice|insights?)\b',lambda m:(m.group(2)[0].upper()+m.group(2)[1:]) if m.group(1)=='I' else m.group(2)),
 (r'\b([Aa])n?\s+independent\s+((?:property\s+|real estate\s+)?(?:agent|adviser|advisor|consultant|strategist|realtor))\b',lambda m:(m.group(1)+('n ' if m.group(2)[0] in 'aeiou' else ' '))+m.group(2)),
 (r'\b([Ii])ndependent\s+((?:property\s+|real estate\s+)?(?:agent|adviser|advisor|consultant|strategist|realtor))\b',lambda m:(m.group(2)[0].upper()+m.group(2)[1:]) if m.group(1)=='I' else m.group(2)),
]
def scrub(s):
    for a,b in R: s=re.sub(a,b,s,flags=re.I|re.S)
    return facts(s)

# --- 31 Oct 2026 (approved): factual corrections, case-sensitive, idempotent.
# BSD: IRAS residential rates from 15 Feb 2023 (iras.gov.sg BSD page): 1% first 180k, 2% next 180k, 3% next 640k,
# 4% next 500k, 5% next 1.5M, 6% above 3M. S$1.5M=44,600; S$2M=69,600; S$2.5M=94,600.
EDGE_ORCH='https://www.edgeprop.sg/property-news/hong-leong-holdings-tid-joint-venture-submits-top-bid-1755-psf-ppr-orchard-boulevard-gls-site'
FACTS=[
 (r'~S\$39,600','~S$44,600'),(r'~S\$57,600','~S$69,600'),(r'~S\$75,600','~S$94,600'),
 (r'BSD is approximately S\$57,600','BSD is approximately S$69,600'),
 (r'BSD via CPF: S\$57,600','BSD via CPF: S$69,600'),
 (r'next S\$640,000 at 3%, and the remainder at 4%\.','next S$640,000 at 3%, next S$500,000 at 4%, next S$1,500,000 at 5%, and the remainder above S$3,000,000 at 6% (IRAS residential rates from 15 Feb 2023).'),
]
# Orchard Boulevard GLS: tender closed 29 Oct 2026; top bid confirmed by EdgeProp (29 Oct 2026, table sourced from URA). Scoped to that page.
ORCH=[
 (r'GLS Tender Closes 29 Oct 2026','GLS Tender Closed 29 Oct 2026'),
 (r'<b>29 Oct</b><span>Tender closes</span>','<b>S$1,755</b><span>Top bid psf ppr</span>'),
 (r'The tender closes on 29 October 2026 at 12 noon\. Until URA announces the bids and awards the site,','The tender closed on 29 October 2026 at 12 noon with five bids. The top bid was S$181.86 million, or S$1,755 psf ppr, from a joint venture between Hong Leong Holdings and TID (<a href="'+EDGE_ORCH+'" target="_blank" rel="noopener">EdgeProp, 29 Oct 2026</a>). A top bid is not an award: until URA awards the site,'),
 (r'Want the tender result the day it'+AP+r's out\?','Want URA’s award decision the day it’s out?'),
 (r'Tender closes 29 Oct 2026, 12 noon','Tender closed 29 Oct 2026, 12 noon (5 bids; top bid S$1,755 psf ppr, Hong Leong Holdings and TID)'),
 (r'1\. Tender closes(</h\d>\s*<p[^>]*>)29 Oct 2026, 12 noon\. URA then publishes the bids received\.',r'1. Tender closed\g<1>Closed 29 Oct 2026, 12 noon. URA published five bids; the top bid was S$1,755 psf ppr.'),
 (r'URA('+AP+r')s tender closes on 29 October 2026 at 12 noon\. No developer, project name, prices or launch date have been announced yet\.',r'URA\1s tender closed on 29 October 2026 with five bids; the top bid, S$1,755 psf ppr, came from Hong Leong Holdings and TID. URA has not yet awarded the site, and no project name, prices or launch date have been announced.'),
 (r'The GLS tender closes on 29 October 2026;','The GLS tender closed on 29 October 2026;'),
 (r'the tender result, the awarded developer','URA’s award decision, the developer'),
 (r'The tender closes on 29 Oct 2026; the developer is to be awarded\.','The tender closed on 29 Oct 2026 with a top bid of S$1,755 psf ppr; the site is not yet awarded.'),
]
FACT_BAD=re.compile(r'remainder at 4%|~S\$(?:39|57|75),600|BSD (?:is approximately|via CPF:) S\$57,600|GLS Tender Closes 29 Oct|Tender closes 29 Oct|tender closes on 29 Oct')
def facts(s):
    for a,b in FACTS: s=re.sub(a,b,s)
    if 'Orchard Boulevard' in s and '3,438' in s and '29 Oct' in s:
        for a,b in ORCH: s=re.sub(a,b,s)
    if 'S$44,600' in s and 'How Much Do I Need To Buy A Condo' in s: s=re.sub(r'(Updated:(?:</strong>)?\s*)July 2026',r'\1October 2026',s).replace('Updated 2026-06-18','Updated 2026-10-31')
    return s
# Approved tagline, keep (Emmeline 30 Oct 2026): 'Your Trusted Singapore Property Advisor' must never be scrubbed or matched by BAD.
BAD=re.compile(r'15\+ ?years|(?:more than|over) 15 years|500\+|\$\s?250\s?M|hundreds of families|Mei Ling|Tan Family|What Clients Say|since 2009|\bAlex\b|\bindependent\s+(?:guidance|analysis|advice|insights?|(?:property\s+|real estate\s+)?(?:agent|adviser|advisor|consultant|strategist|realtor))\b|Assessed by Emmeline|/\s*10\s*★|★',re.I)

# --- footer disclaimer label + enquiry-form consent (approved 30 Oct: "Yes, put the form and footer changes live")
REQ_TXT='I consent to Emmeline Koh (PropNex) collecting and using my details to respond to this enquiry, per the <a href="/privacy-policy/">Privacy Policy</a>.'
MKT_TXT="I'd like to receive property updates and marketing from Emmeline Koh by WhatsApp, phone, SMS or email. I can withdraw anytime."
CALC_NOTE='<p class="ekc-note">Estimates only, not financing advice. Bank and HDB assessments apply.</p>'
SGT_JS='new Date(Date.now()+288e5).toISOString().slice(0,19)+"+08:00"'
def _form(m):
    f=m.group(0)
    if 'data-reg' in f: return f  # early-registration forms carry their own project-specific PDPA consent (launches.py)
    # standard forms: required consent label
    f=re.sub(r'<label class="chk"><input type="checkbox"(?![^>]*marketing_consent)[^>]*>.*?</label>',
             '<label class="chk"><input type="checkbox" name="pdpa_consent" value="yes" required> <span>'+REQ_TXT+'</span></label>',f,flags=re.S)
    # calculator gate
    f=re.sub(r'<p class="chk"><input id="g-pdpa"[^>]*/?><label for="g-pdpa">.*?</label></p>',
             '<p class="chk"><input id="g-pdpa" name="pdpa_consent" value="yes" required="" type="checkbox"/><label for="g-pdpa"><span>'+REQ_TXT+'</span></label></p>',f,flags=re.S)
    f=re.sub(r'<label class="chk"><input type="checkbox" name="marketing_consent"[^>]*>.*?</label>',
             '<label class="chk"><input type="checkbox" name="marketing_consent" value="yes"> <span>'+MKT_TXT+'</span></label>',f,flags=re.S)
    f=re.sub(r'<p class="chk"><input id="g-mkt"[^>]*/?><label for="g-mkt">.*?</label></p>',
             '<p class="chk"><input id="g-mkt" name="marketing_consent" value="yes" type="checkbox"/><label for="g-mkt"><span>'+MKT_TXT+'</span></label></p>',f,flags=re.S)
    if 'marketing_consent' not in f:
        if 'id="g-pdpa"' in f:
            f=re.sub(r'(<label for="g-pdpa">.*?</label></p>)',lambda x:x.group(1)+'\n<p class="chk"><input id="g-mkt" name="marketing_consent" value="yes" type="checkbox"/><label for="g-mkt">'+MKT_TXT+'</label></p>',f,count=1,flags=re.S)
        else:
            f=re.sub(r'(<label class="chk"><input type="checkbox" name="pdpa_consent"[^>]*>.*?</label>)',lambda x:x.group(1)+'<label class="chk"><input type="checkbox" name="marketing_consent" value="yes"> <span>'+MKT_TXT+'</span></label>',f,count=1,flags=re.S)
    return f
def consent(s):
    s=s.replace('Disclaimer (DRAFT, pending Legal Officer review).','Disclaimer:')
    s=re.sub(r'<form\b.*?</form>',_form,s,flags=re.S)
    # calculator: disclaimer near result, consent fields in the mailto body (and the dormant CF7 path)
    if 'id="t-hint"' in s and 'class="ekc-note"' not in s:
        s=s.replace('<p id="t-hint"></p>','<p id="t-hint"></p>'+CALC_NOTE,1)
    s=s.replace('"\\nEmail: "+$("g-email").value+"\\n\\n"+summary)',
                '"\\nEmail: "+$("g-email").value+"\\n\\n"+summary+"\\n\\npdpa_consent: yes\\nmarketing_consent: "+($("g-mkt")&&$("g-mkt").checked?"yes":"no")+"\\nconsent_timestamp: "+'+SGT_JS+')')
    if 'fd.append("marketing_consent"' not in s:
        s=s.replace('fd.append("ek-pdpa","1");','fd.append("ek-pdpa","1");fd.append("marketing_consent",$("g-mkt")&&$("g-mkt").checked?"yes":"no");fd.append("consent_timestamp",'+SGT_JS+');')
    return s
CONSENT_BAD=re.compile(r'Disclaimer \(DRAFT|in line with the PDPA|under the PDPA\. See|contacting me by phone, WhatsApp or email about property advice')


# --- Google Search Console verification (approved by Emmeline 30 Oct 2026, 'request a re-crawl'). KEEP PERMANENTLY.
GSV_FILE='googleeb065822e5d9910f.html'
GSV_BODY='google-site-verification: googleeb065822e5d9910f.html'
GSV_META='<meta name="google-site-verification" content="vGxmULZYScGRBCGXPZ8Ao_VoH1mDMVyNCSsBIsIW6pc" />'
def gsv_meta(s):
    """Ensure the GSC meta tag is in <head> exactly once (home page)."""
    s=re.sub(r'\s*<meta name="google-site-verification"[^>]*>','',s)
    return re.sub(r'(<meta name="viewport"[^>]*>)',lambda m:m.group(1)+'\n'+GSV_META,s,count=1) if '<meta name="viewport"' in s else s.replace('<head>','<head>\n'+GSV_META,1)
def gsv(D):
    """Write the GSC verification file (exact body, no trailing newline) and the home meta tag."""
    import os
    f=os.path.join(D,GSV_FILE)
    if not os.path.exists(f) or open(f).read()!=GSV_BODY: open(f,'w').write(GSV_BODY)
    h=os.path.join(D,'index.html')
    if os.path.exists(h):
        t=open(h).read(); n=gsv_meta(t)
        if n!=t: open(h,'w').write(n)


# --- Canonical host (30 Oct 2026, Emmeline's re-crawl approval). KEEP: GitHub Pages serves the bare domain
# https://emmelinekoh.sg/ (www and http 301 to it). Every self-reference must use it; every page gets exactly
# one self canonical (meta-refresh redirect stubs keep their canonical to the target).
SITE='https://emmelinekoh.sg'
_UPL=re.compile(r'(?i)(?:https?://(?:www\.)?emmelinekoh\.sg)?/wp-content/uploads/([^"\'\s)<>]+?)\.(?:jpe?g|png|webp|gif)')
def host(s,D=None):
    """Old WordPress image URLs -> local /assets/img copy (if present); www/http self refs -> https bare domain."""
    import os
    if D:
        def _m(m):
            n=m.group(1).replace('/','-')+'.webp'
            return '/assets/img/'+n if os.path.exists(os.path.join(D,'assets','img',n)) else m.group(0)
        s=_UPL.sub(_m,s)
    # empty WordPress upload refs (no file name) -> drop the element cleanly (30 Oct 2026, 'Yes, fix them')
    _E=r'(?:https?://(?:www\.)?emmelinekoh\.sg)?/wp-content/uploads/'
    s=re.sub(r'<figure>\s*<img[^>]*src="'+_E+r'"[^>]*>\s*</figure>','',s)
    s=re.sub(r'<img[^>]*src="'+_E+r'"[^>]*>','',s)
    s=re.sub(r'<div class="gal[^"]*">\s*</div>','',s)
    s=re.sub(r'\s*style="--hero:url\(\''+_E+r'\'\)"','',s)
    return re.sub(r'(?i)https?://www\.emmelinekoh\.sg|http://emmelinekoh\.sg',SITE,s)
def page_url(D,f):
    import os
    rel=os.path.relpath(f,D).replace(os.sep,'/')
    return SITE+'/'+(rel[:-len('index.html')] if rel.endswith('index.html') else rel)
def canonical(s,url):
    if '<head' not in s: return s
    if re.search(r'(?i)<meta[^>]*http-equiv=["\']refresh',s) and re.search(r'(?i)rel=["\']canonical',s): return s
    s=re.sub(r'(?i)\s*<link[^>]*rel=["\']canonical["\'][^>]*>','',s)
    tag='<link rel="canonical" href="%s">'%url
    if re.search(r'<meta name="viewport"[^>]*>',s): return re.sub(r'(<meta name="viewport"[^>]*>)',lambda m:m.group(1)+'\n'+tag,s,count=1)
    return re.sub(r'(<head[^>]*>)',lambda m:m.group(1)+'\n'+tag,s,count=1)
def canon_all(D):
    """Apply host() + one self canonical (+ og:url/twitter:url self, if present) to every served page; host() on sitemap/robots/llms."""
    import os,glob
    for f in glob.glob(os.path.join(D,'**','*.html'),recursive=True):
        if '/.git/' in f or '/overrides/' in f or 'backup' in f: continue
        t=open(f).read(); u=page_url(D,f); n=host(t,D)
        if '<head' in n:
            n=canonical(n,u)
            n=re.sub(r'(<meta[^>]*(?:property|name)=["\'](?:og|twitter):url["\'][^>]*content=["\'])[^"\']*',lambda m:m.group(1)+u,n)
        if n!=t: open(f,'w').write(n)
    for x in ('sitemap.xml','robots.txt','llms.txt'):
        f=os.path.join(D,x)
        if os.path.exists(f):
            t=open(f).read(); n=host(t)
            if n!=t: open(f,'w').write(n)


# --- 31 Oct 2026 (approved): sitemap.xml regenerated on every postprocess run (keep permanently).
# Lists every served page as https://emmelinekoh.sg/<path>/ (apex, https, trailing slash); skips meta-refresh
# stubs, noindex pages, 404, the GSC verification file and non-page dirs. Keeps existing lastmods; new or
# touched pages get today's SGT date. Validates XML and keeps the Sitemap line in robots.txt.
SKIP_DIRS={'assets','overrides','launches','node_modules','404'}
def sitemap(D,touch=()):
    import os,datetime,xml.dom.minidom
    sm=os.path.join(D,'sitemap.xml'); old={}; order=[]
    if os.path.exists(sm):
        for u,d in re.findall(r'<loc>\s*([^<\s]+)\s*</loc>\s*<lastmod>\s*([^<\s]+)\s*</lastmod>',open(sm).read()):
            u=host(u)
            if u not in old: old[u]=d; order.append(u)
    today=(datetime.datetime.utcnow()+datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    pages=set()
    for root,ds,fs in os.walk(D):
        ds[:]=[x for x in ds if not x.startswith('.') and x not in SKIP_DIRS]
        if 'index.html' not in fs: continue
        t=open(os.path.join(root,'index.html'),errors='ignore').read()
        if re.search(r'http-equiv=["\']?refresh',t,re.I) or re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex',t,re.I): continue
        rel=os.path.relpath(root,D).replace(os.sep,'/')
        pages.add(SITE+'/'+('' if rel=='.' else rel.strip('/')+'/'))
    touch={SITE+'/'+(t.strip('/')+'/' if t.strip('/') else '') for t in touch}
    urls=[u for u in order if u in pages]+sorted(pages-set(order))
    if SITE+'/' in urls: urls.remove(SITE+'/'); urls.insert(0,SITE+'/')
    out='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        d=today if (u in touch or u not in old) else old[u]
        out+='<url><loc>%s</loc><lastmod>%s</lastmod></url>\n'%(u.replace('&','&amp;'),d)
    out+='</urlset>\n'
    xml.dom.minidom.parseString(out.encode())
    if not os.path.exists(sm) or open(sm).read()!=out: open(sm,'w').write(out)
    rb=os.path.join(D,'robots.txt')
    if os.path.exists(rb):
        r=open(rb).read()
        if 'Sitemap: '+SITE+'/sitemap.xml' not in r:
            r=re.sub(r'(?im)^Sitemap:.*\n?','',r).rstrip('\n')+'\n\nSitemap: '+SITE+'/sitemap.xml\n'; open(rb,'w').write(r)
    return len(urls)
