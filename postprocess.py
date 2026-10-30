#!/usr/bin/env python3
"""Idempotent post-build pass (run after build.py, and on the repo): site-wide
RealEstateAgent JSON-LD, FAQPage JSON-LD for visible FAQs, 'Updated' date on guide
pages, wa.me utm_source, and the 'How did you find me?' field on enquiry forms."""
import sys,os,re,json,glob,html
from bs4 import BeautifulSoup
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import claims_guard
D=sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.abspath(__file__))
S='https://emmelinekoh.sg'
AGENT={"@context":"https://schema.org","@type":"RealEstateAgent","@id":S+"/#agent",
 "name":"Emmeline Koh – PropNex Realty Pte. Ltd.","url":S+"/","telephone":"+6582754135",
 "email":"solidhomesbyemmeline@gmail.com","description":"Emmeline Koh – Your Trusted Singapore Property Advisor. In Singapore real estate since 2004. CEA Reg. No. R045542G.",
 "areaServed":{"@type":"Country","name":"Singapore"},
 "parentOrganization":{"@type":"Organization","name":"PropNex Realty Pte. Ltd.","identifier":"L3008022J"},
 "sameAs":["https://www.linkedin.com/in/emmelinekoh","https://www.instagram.com/emmelinekoh","https://www.tiktok.com/@emmelinekoh"]}
SRC='''<label>How did you find me? (optional)<select name="found-via"><option value="">Select</option><option>Google</option><option>ChatGPT / AI assistant</option><option>Instagram</option><option>TikTok</option><option>LinkedIn</option><option>PropertyGuru</option><option>Referral</option><option>Other</option></select></label>'''
lm={}
try:
    for loc,d in re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>',open(D+'/sitemap.xml').read()): lm[loc.replace(S,'').strip('/')]=d
except FileNotFoundError: pass
def ld(o,i): return f'<script type="application/ld+json" id="{i}">{json.dumps(o,ensure_ascii=False)}</script>'
# --- /privacy-policy/ regenerated from content/privacy-policy.md (Legal Officer draft) every run
PP=os.path.join(os.path.dirname(os.path.abspath(__file__)),'content','privacy-policy.md')
if os.path.exists(PP) and os.path.exists(D+'/about-us/index.html'):
    import markdown
    t=open(D+'/about-us/index.html').read()
    t=re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>','',t,flags=re.S)
    t=re.sub(r'<title>.*?</title>','<title>Privacy Policy | Emmeline Koh</title>',t,count=1)
    md=re.sub(r'^\W*Draft, pending[^\n]*\n+','',open(PP).read(),flags=re.M|re.I)
    md=re.sub(r'^\W*Last updated[^\n]*\n+','',md,flags=re.M|re.I)
    md=re.sub(r'^(# [^\n]*\n+)',r'\1Last updated 30 Oct 2026\n\n',md,count=1)
    body=markdown.markdown(md)
    t=t[:t.index('<main')]+'<main class="pg pg--legal"><section class="sec light"><div class="sec-in" style="max-width:760px;margin:0 auto;padding:120px 20px 60px">'+body+'</div></section></main>'+t[t.index('</main>')+7:]
    os.makedirs(D+'/privacy-policy',exist_ok=True); open(D+'/privacy-policy/index.html','w').write(t)
SM=D+'/sitemap.xml'
if os.path.exists(SM):
    sm=open(SM).read()
    if S+'/privacy-policy/' not in sm:
        sm=sm.replace('</urlset>','<url><loc>'+S+'/privacy-policy/</loc><lastmod>2026-10-30</lastmod></url>\n</urlset>'); open(SM,'w').write(sm)
files=[D+'/index.html']+sorted(glob.glob(D+'/*/index.html'))
for f in files:
    s=open(f).read(); o=s
    if 'http-equiv="refresh"' in s: continue
    slug=os.path.basename(os.path.dirname(f)) if f!=D+'/index.html' else 'home'
    path='' if slug=='home' else slug
    s=claims_guard.scrub(s)
    s=claims_guard.consent(s)
    # consent checkbox links to the privacy policy
    s=re.sub(r'(<label class="chk"><input[^>]*>[^<]*?)(</label>)',lambda m:m.group(0) if ('privacy-policy' in m.group(0) or 'marketing_consent' in m.group(0)) else m.group(1)+' See the <a href="/privacy-policy/">Privacy Policy</a>.'+m.group(2),s)
    if 'id="ld-agent"' not in s: s=s.replace('</head>',ld(AGENT,'ld-agent')+'</head>',1)
    # FAQPage for visible <div class="faq"> blocks, when the page has none
    if '<div class="faq">' in s and '"FAQPage"' not in s:
        soup=BeautifulSoup(s,'html.parser'); qa=[]
        for d in soup.select('div.faq > details'):
            q=d.find('summary'); a=d.find('div')
            if q and a: qa.append({"@type":"Question","name":q.get_text(' ',strip=True),"acceptedAnswer":{"@type":"Answer","text":re.sub(r'\s+',' ',a.get_text(' ',strip=True))}})
        if qa: s=s.replace('</head>',ld({"@context":"https://schema.org","@type":"FAQPage","@id":f"{S}/{path+'/' if path else ''}#faq","mainEntity":qa},'ld-faq')+'</head>',1)
    # visible date on guide pages (landing/article) that show none
    if re.search(r'pg--(landing|article)',s) and not re.search(r'Last updated|Updated \d|Updated [A-Z]|class="pg-updated"',s) and path in lm:
        s=re.sub(r'(</header>)(\s*(?:<nav class="toc[^>]*>.*?</nav>)?\s*<section[^>]*><div class="sec-in[^"]*">)',lambda m:m.group(1)+m.group(2)+f'<p class="pg-updated rv"><time datetime="{lm[path]}">Updated {lm[path]}</time></p>',s,count=1,flags=re.S)
        if 'pg-updated' not in s: s=re.sub(r'(</aside>\s*<(?:div|article)[^>]*>)',lambda m:m.group(1)+f'<p class="pg-updated"><time datetime="{lm[path]}">Updated {lm[path]}</time></p>',s,count=1)
    # utm_source on wa.me links
    s=re.sub(r'href="(https://wa\.me/6582754135[^"]*)"',lambda m:'href="%s"'%(m.group(1) if 'utm_source=' in m.group(1) else m.group(1)+('&amp;' if '?' in m.group(1) else '?')+'utm_source='+slug),s)
    # enquiry form source field
    if 'data-mailto' in s and 'name="found-via"' not in s:
        s=re.sub(r'(<form[^>]*data-mailto[^>]*>.*?)(<label class="chk">|<button)',lambda m:m.group(1)+SRC+m.group(2),s,count=1,flags=re.S)
    # tagline removed at Emmeline's request (25 Oct 2026)
    s=re.sub(r'(How I work)\s*[:\-–—]\s*Guide first[.,]?\s*Sell second\.?',r'\1',s,flags=re.I)
    s=re.sub(r'\s*Guide first[.,]?\s*sell second\.?','',s,flags=re.I)
    # 'not the official website' wording removed at Emmeline's request (25 Oct 2026)
    for _p in [r"\s*This website is not the official website of any developer\.",r"\s*(?:It|This)(?: website| page| site)? is not (?:the|a|any) (?:developer(?:’|'|&#8217;)s )?official (?:website|site)(?: of [^.<]*)?\.?",r"\s*Not the developer(?:’|'|&#8217;)s (?:official )?(?:website|site)\."]: s=re.sub(_p,'',s)
    if s!=o: open(f,'w').write(s)
# Google Search Console verification file + home meta (keep permanently)
claims_guard.gsv(D)
# Canonical host + exactly one self canonical on every page (keep permanently)
claims_guard.canon_all(D)
