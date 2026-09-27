"""Predeclared conservative automatic checks; no model/method label is used."""
import re,collections,functools
import spacy
from sacrebleu.metrics import CHRF
NLP=None
@functools.lru_cache(maxsize=25000)
def doc(s):
 global NLP
 if NLP is None: NLP=spacy.load('en_core_web_sm')
 return NLP(s)
def norm(s):return re.sub(r'\W+',' ',s.lower()).strip()
def features(s):
 d=doc(s)
 lemma=[t.lemma_.lower() for t in d if not t.is_punct and not t.is_space and not(t.lower_ in {'will','shall'} and t.pos_=='AUX')]
 ents=[norm(e.text) for e in d.ents if e.label_ in {'PERSON','ORG','GPE','LOC','FAC','PRODUCT'}]
 dates=[norm(e.text) for e in d.ents if e.label_ in {'DATE','TIME'}]
 numbers=re.findall(r'\d+(?:[.,]\d+)*',s)
 neg=[t.lower_ for t in d if t.dep_=='neg' or t.lower_ in {'not',"n't",'never','no','neither','nor','without'}]
 future=any(t.lower_ in {'will','shall'} and t.dep_ in {'aux','auxpass'} and t.head.pos_ in {'VERB','AUX'} for t in d)
 return dict(lemma=lemma,entities=ents,dates=dates,numbers=numbers,negation=neg,future=future)
def edit_similarity(a,b):
 if not a and not b:return 1.
 prev=list(range(len(b)+1))
 for i,x in enumerate(a):
  row=[i+1]
  for j,y in enumerate(b):row.append(min(row[-1]+1,prev[j+1]+1,prev[j]+(x!=y)))
  prev=row
 return 1-prev[-1]/max(len(a),len(b),1)
def evaluate(source,output,reference,eos=True):
 a,b=features(source),features(output)
 out={'attribute_auto':b['future']}
 for k in ['lemma','entities','dates','numbers','negation']:out[k+'_preserved_auto']=a[k]==b[k]
 out['content_auto']=all(out[k+'_preserved_auto'] for k in ['lemma','entities','dates','numbers','negation'])
 w=output.lower().split(); counts=collections.Counter(tuple(w[i:i+3]) for i in range(len(w)-2))
 reasons=[]
 if not output.strip():reasons.append('empty')
 if not eos:reasons.append('truncated_no_eos')
 if not re.search('[a-zA-Z]',output):reasons.append('no_english_letters')
 if max(counts.values(),default=0)>=4:reasons.append('repeated_trigram')
 out.update(valid_auto=not reasons,Joint_auto=bool(out['attribute_auto'] and out['content_auto'] and not reasons),exact_reconstruction=source==output,word_reconstruction_similarity=edit_similarity(source.split(),output.split()),reference_chrf=CHRF().sentence_score(output,[reference]).score)
 if not out['attribute_auto']:reasons.append('future_not_detected')
 if not out['content_auto']:reasons.append('strict_content_changed')
 out['failure_reasons']=reasons
 return out
