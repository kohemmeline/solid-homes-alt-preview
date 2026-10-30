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
