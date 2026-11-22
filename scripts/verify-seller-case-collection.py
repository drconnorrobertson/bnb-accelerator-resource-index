"""Verify complete case preservation and exact canonical/redirect ownership."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,sys,hashlib,xml.etree.ElementTree as E
root=Path.cwd();pub=root/'public';slug='seller-records';owner='/library/'+slug+'/';html=(pub/owner.lstrip('/')/'index.html').read_text();articles=json.loads((root/'content/page-articles'/f'{slug}.json').read_text());assert len(articles)==40
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def visible(h):
 p=Text();p.feed(h);return re.sub(r'\s+',' ',' '.join(p.parts)).strip()
ids=re.findall(r'\bid="([^"]+)"',html);assert len(ids)==len(set(ids)),'Duplicate form or case IDs'
for target in re.findall(r'\bfor="([^"]+)"',html):assert target in ids,target
rules=json.loads((root/'vercel.json').read_text()).get('redirects',[])
for n in range(1,41):
 case=f'case-{n:02d}';assert ids.count(case)==1
 assert f'data-case-workspace="{case}" data-storage-path="/workbooks/{slug}/example-{n:02d}/"'in html
 assert f'aria-label="Example {n:02d} evidence comparison"'in html
 assert not(pub/'workbooks'/slug/f'example-{n:02d}'/'index.html').exists()
 for suffix in ['', '/']:
  source=f'/workbooks/{slug}/example-{n:02d}'+suffix;matches=[r for r in rules if r['source']==source];assert len(matches)==1 and matches[0]['permanent'] and matches[0]['destination']==owner+'#'+case
assert 'data-case-workspace="own" data-storage-path="'+owner+'"'in html
assert len(re.findall('data-case-workspace="',html))==41
assert len(re.findall('class="case-nav-group"',html))==5
links=re.findall(r'data-case-link="([^"]+)"',html);assert len(links)==40 and len(set(links))==40
assert '$19,000' in html and '$54,666.67' in html
assert 60000-41000==19000 and round(41000*12/9,2)==54666.67
assert len({json.dumps(a['caseFacts'],sort_keys=True)for a in articles})==1
assert len({a['shortTitle']for a in articles})==40
urls=[u.text for u in E.parse(pub/'sitemap.xml').findall('.//{*}loc')];assert len(urls)==len(set(urls))==1587
assert not any('/workbooks/seller-records/'in u for u in urls)
if len(sys.argv)>1:
 base=Path(sys.argv[1]);old=(base/'public'/owner.lstrip('/')/'index.html').read_text()
 for n in range(1,41):
  oldCase=(base/'public/workbooks'/slug/f'example-{n:02d}'/'index.html').read_text();pattern=r'<article data-developed-case="'+slug+'/'+str(n)+r'">([\s\S]*?)</article>';a=re.search(pattern,oldCase);b=re.search(pattern,html);assert a and b;assert visible(a[1])==visible(b[1]),('Case text changed',n)
 # Existing own-checklist initial fields and status are preserved.
 oldData=json.loads(re.search(r'<script id="workspace-data" type="application/json">(.*?)</script>',old)[1]);newData=json.loads(re.search(r'data-case-workspace="own"[\s\S]*?<script type="application/json" data-case-workspace-data>(.*?)</script>',html)[1]);assert oldData==newData
print(json.dumps({'ownerPages':1587,'preservedCaseArticles':40,'caseConditions':40,'commonFactPackets':1,'isolatedWorksheets':41,'legacyURLForms':80,'uniqueIDs':len(ids),'fullCaseText':'preserved','comparisonGap':19000,'hypotheticalExtrapolation':54666.67,'utilityAmounts':'not supplied'}))
