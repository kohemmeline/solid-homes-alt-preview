"""Claims guard (approved by Emmeline 24 + 30 Oct 2026). Strips unverified stats
(15+ years, 500+ families, $250M+), and the sample homepage testimonials.
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
]
def scrub(s):
    for a,b in R: s=re.sub(a,b,s,flags=re.I|re.S)
    return s
BAD=re.compile(r'15\+ ?years|(?:more than|over) 15 years|500\+|\$\s?250\s?M|hundreds of families|Mei Ling|Tan Family|What Clients Say|Assessed by Emmeline|/\s*10\s*★|★',re.I)
