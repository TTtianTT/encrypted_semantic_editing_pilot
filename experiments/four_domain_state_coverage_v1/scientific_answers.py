"""Derive concise Chinese research answers from actual completed CSV evidence."""
import csv,statistics
from collections import defaultdict
from common import *

def readcsv(base,name):
    p=base/name
    return list(csv.DictReader(p.open())) if p.exists() and p.stat().st_size>1 else []

def primary():
    out={}
    for model in MODELS:
        for domain in DOMAINS:
            out[(model,domain)]=ROOT.parent/'space_relation_confirmation_v1' if domain=='space' else ROOT
    return out

def research_answers():
    ph=defaultdict(lambda:[0,0]);presence=defaultdict(set);deltas=defaultdict(list);losses=defaultdict(lambda:[0,0]);completed=[];pending=[];failed=[]
    for (m,d),base in primary().items():
        ss=[r for r in readcsv(base,'completion_status.csv') if r['phase']=='formal' and r['model']==m and r['domain']==d]
        if len(ss)<3 or any(r['status']=='running_or_not_started' for r in ss):pending.append(f'{m}/{d}')
        if any(r['status']=='not_admitted' for r in ss):failed.append(f'{m}/{d}')
        if len(ss)==3 and all(r['status']=='completed' for r in ss):completed.append(f'{m}/{d}')
        for r in readcsv(base,'current_correct_next_failure.csv'):
            if (r['model'],r['domain'])==(m,d) and r['condition']=='P' and r['template']=='0':
                v=ph[(m,d,int(r['seed']))];v[0]+=int(r.get('latent_next_semantic_mismatch_k',0));v[1]+=int(r['current_correct_and_gold_next_correct_n'])
                if int(r['latent_next_failed_k'])>0:presence[(m,d)].add(int(r['seed']))
        for r in readcsv(base,'M_vs_S.csv'):
            if (r['model'],r['domain'])==(m,d) and r['source']=='U' and r['template']=='0' and r['cohort']=='fixed_fulltext_mask':deltas[(m,d,int(r['holdout_split']))].append((int(r['seed']),float(r['M_minus_S'])))
        for r in readcsv(base,'capability_regressions.csv'):
            if (r['model'],r['domain'])==(m,d) and r['shard']=='atomic_core':
                v=losses[(m,d,r['condition'])];v[0]+=int(r['old_success_lost']);v[1]+=int(r['old_failure_repaired'])
    affected=sorted({m+'/'+d for (m,d,s),(k,n) in ph.items() if k>0})
    reviewed=read(ROOT/'CONTINUATION_AGENT_REVIEW.json') if (ROOT/'CONTINUATION_AGENT_REVIEW.json').exists() else {'cases':[]}
    reviewed_domains=sorted({r['domain'] for r in reviewed['cases']})
    review_note=('固定案例审阅已确认BART的'+ '、'.join(reviewed_domains)+'三个seed发生当前正确、gold续步正确而latent续步表达破碎/不完整；这证明这些案例失败存在，不把全部未解析输出判成语义错误。') if reviewed_domains else ''
    a1=review_note+'另有可解析的下一步语义不匹配的模型/领域为'+('、'.join(affected) if affected else '暂无已完成证据')+'。未解析、仅语法或终止失败另列，逐seed计数见表。未准入组合'+('、'.join(failed) if failed else '暂无')+'未达到冻结的受控任务门槛；不能据此判定其全部合理释义能力。'+('仍待完成：'+ '、'.join(pending)+'。' if pending else '')
    if (ROOT/'T5_SPACE_CONTINUATION_AGENT_REVIEW.json').exists():a1+=' 原朝向空间另有三个T5Gemma seed的九个固定案例：当前与gold续步正确，latent下一步错误/缺失。该行为证据不依赖其旧留出解释，但旧朝向划分不能证明相对关系状态迁移，须与确认版分列。'
    if (ROOT/'T5_EMOTION_THREE_SEED_CONTINUATION_AGENT_REVIEW.json').exists():
        review=read(ROOT/'T5_EMOTION_THREE_SEED_CONTINUATION_AGENT_REVIEW.json')
        a1+=' 情感P三个seed的step2各有96条合格续步，严格成功分别为'+','.join(str(r['strict_success']) for r in review['counts'])+'；严格失败分别为'+','.join(str(r['strict_failed']) for r in review['counts'])+'，已解析槽位不匹配分别为'+','.join(str(r['parsed_slot_mismatch']) for r in review['counts'])+'。首个固定世界的九例确认越级/评价错误或必要内容缺失，包括目标正确但非目标丢失的案例；全部3条成功反例保留。此证据只需已完成的P轨迹，不把未完成的N/S/M当成完成。'
    elif (ROOT/'T5_EMOTION_S42_CONTINUATION_AGENT_REVIEW.json').exists():a1+=' 情感seed42首批证据为96条合格续步中95条严格失败、1条成功，64条为已解析槽位不匹配；固定案例确认评价越级或必要内容缺失。此单seed记录保留成功反例，其余seed另报，不冒充三seed结论。'
    if (ROOT/'T5_PERSON_THREE_SEED_CONTINUATION_AGENT_REVIEW.json').exists():
        review=read(ROOT/'T5_PERSON_THREE_SEED_CONTINUATION_AGENT_REVIEW.json')
        a1+=' T5Gemma人称三个seed的step2各96条合格续步、严格成功均0；首个固定世界的九例助手审阅确认未切换/切错Speaker语境、事件缺失，或新增改变参与者的事件。事件身份保持而语境错误的案例不标成人物绑定错误。'
        presence[('t5gemma','person')].update(r['seed'] for r in review['counts'] if r['strict_failed']>0)
    elif (ROOT/'T5_PERSON_S42_CONTINUATION_AGENT_REVIEW.md').exists():a1+=' T5Gemma人称另有seed42首个固定世界的三例助手审阅：gold续步正确，latent未切换/切错Speaker语境，或事件缺失。该记录仅涉及seed42；事件身份保持而语境错误的案例不标成人物绑定错误。'
    contrasts=[]
    for (m,d,h),vv in sorted(deltas.items()):
        values=[x for s,x in sorted(vv)];contrasts.append(f'{m}/{d}/H{h}：{len(values)}seed均值{statistics.mean(values)*100:+.2f}pp，范围[{min(values)*100:+.2f},{max(values)*100:+.2f}]pp')
    a2='留出状态×留出U、固定同全文/mask集合的M−S：'+('；'.join(contrasts) if contrasts else '尚无完成的对照')+'。正负方向和零效果均保留；只有同一领域两个划分和全部seed支持时才称稳定优势。空间主问题使用更正后的关系状态划分，原绝对朝向结果不作为未见关系状态证据。'
    directional=defaultdict(list)
    for r in readcsv(ROOT,'M_vs_S_by_operation.csv'):
        if r['domain']=='emotion' and r['source']=='U' and r['template']=='0' and r['cohort']=='fixed_fulltext_mask':
            directional[(r['model'],int(r['holdout_split']),r['operation'])].append(r)
    direction_notes=[]
    for (m,h,op),rr in sorted(directional.items()):
        values=[float(r['M_minus_S']) for r in rr];s=[int(r['S_k'])/int(r['n']) for r in rr];v=[int(r['M_k'])/int(r['n']) for r in rr]
        direction_notes.append(f"{m}/emotion/H{h}/{'提高' if op=='plus' else '降低'}：{len(rr)}seed，S均值{statistics.mean(s)*100:.2f}%、M均值{statistics.mean(v)*100:.2f}%，M−S均值{statistics.mean(values)*100:+.2f}pp[{min(values)*100:+.2f},{max(values)*100:+.2f}]")
    a2+=' 操作方向分项保存在M_vs_S_by_operation.csv，使用同一固定候选集按plus/minus分组，未改变评分或选集。'+('情感方向结果：'+'；'.join(direction_notes)+'；方向间不能相互代替。' if direction_notes else '')
    transfer=[];scope=[];source_state=[]
    for (m,d),base in primary().items():
        rr=readcsv(base,'summary_by_seed.csv')
        by=defaultdict(lambda:[0,0])
        for r in rr:
            if (r['model'],r['domain'])!=(m,d) or r['phase']!='formal' or r['condition']!='P':continue
            if r['kind']=='atomic' and r['template'] in ('0','1','2'):
                label='自然IID' if r['template'] in ('0','1') else '留出表达';by[label][0]+=int(r['success_k']);by[label][1]+=int(r['n'])
            if r['kind']=='atomic' and int(r['template'])>=3:
                label='结构挑战';by[label][0]+=int(r['success_k']);by[label][1]+=int(r['n'])
        if by.get('自然IID') and by.get('留出表达'):
            x,y=by['自然IID'],by['留出表达'];transfer.append(f'{m}/{d} P自然IID{x[0]}/{x[1]}，留出表达{y[0]}/{y[1]}')
        if by.get('结构挑战'):
            x=by['结构挑战'];scope.append(f'{m}/{d} P挑战{x[0]}/{x[1]}')
        factors=defaultdict(dict)
        for r in readcsv(ROOT,'transfer_quad.csv'):
            if (r['model'],r['domain'])==(m,d) and r['study']==base.name and r['condition']=='S_h0' and r['template']=='0' and r['source_bin']=='heldout_source' and r['cohort']=='fixed_normalized_fulltext_mask_depth':
                factors[r['state_bin']][int(r['seed'])]=float(r['success_rate'])
        if all(set(factors[k])=={42,43,44} for k in ('seen_edited_state','heldout_edited_state')):
            a,b=[list(factors[k].values()) for k in ('seen_edited_state','heldout_edited_state')]
            source_state.append(f'{m}/{d} S/H0在留出U的已补训状态均值{statistics.mean(a)*100:.2f}%[{min(a)*100:.2f},{max(a)*100:.2f}]，留出状态{statistics.mean(b)*100:.2f}%[{min(b)*100:.2f},{max(b)*100:.2f}]')
    a3='三类迁移使用独立轴和固定来源，不能互相替代。已完成的P原子能力：'+('；'.join(transfer) if transfer else '尚待结果')+'。来源/状态交叉按各seed及状态分别报告，不能用全候选覆盖变化冒充固定配对集改善；汇总计数不把多改写视为独立世界。'
    a3+=' 完成三seed的固定配对集来源/状态对照：'+('；'.join(source_state) if source_state else '尚待结果')+'；方括号是训练seed范围，不能作为置信区间。'
    a4='锚点/范围挑战的完整语义成功：'+('；'.join(scope) if scope else '尚待结果')+'。错误案例逐项区分绝对日期、历史原话、固定观察者、非目标评价、人物/所有者绑定；只错相对目标不自动证明选错锚点。未训练结构的单步失败不能归于latent组合。原空间朝向划分存在状态定义限制，确认版固定世界坐标并真正留出right/left当前关系。'
    foils=[]
    for r in readcsv(ROOT,'position_order_pairs.csv'):
        if '/P/test_atomic.jsonl' in r['artifact']:
            foils.append(f"{r['model']}/{r['domain']}/{r['artifact'].split('/')[-3]}/{r.get('pair_family','clause_order')}原顺序{r['original_order_success']}/{r['pairs']}、反顺序{r['reversed_order_success']}/{r['pairs']}、两者均对{r['both_success']}/{r['pairs']}")
    a4+=' 后正式位置诊断：'+('；'.join(foils) if foils else '尚待结果')+'。此扩展单独标记，不冒充最初预注册；目标首句的原挑战不能排除位置捷径。'
    reg=[f'{m}/{d}/{c}自然core原成功损失{k}、原失败修复{repair}' for (m,d,c),(k,repair) in sorted(losses.items()) if k]
    a5='旧自然能力出现损失的设置：'+('；'.join(reg) if reg else '已完成core对照暂无损失；来源/表达损失仍需单列检查')+'。此处跨两个划分汇总用于定位，逐seed、逐划分及旧来源的损失/修复数是主要证据，见capability_regressions。'
    if (ROOT/'T5_EMOTION_NATURAL_CONTROL_REGRESSION_AGENT_REVIEW.md').exists():a5+=' T5Gemma情感seed44/H1的自然补训N独有11个自然core退化：7个negative→strongly negative、4个保持negative，gold均为neutral；全部案例保持非目标评价及客观事实。该划分S/M自然core均512/512，说明不能把所有退化归因于编辑态补训。'
    if (ROOT/'T5_REPAIR_REGRESSION_AGENT_REVIEW.md').exists():a5+=' T5_REPAIR_REGRESSION_AGENT_REVIEW逐例核查同一checkpoint的修复与损失：人称seed42/M_h1、seed43/S_h0和M_h1、seed44/S_h0，以及情感seed44/N_h1。损失分别涉及语境、参与者绑定、评价等级或必要Listener信息；Listener缺失例的事件身份/事实仍正确，不能扩大为事件语义错误。'
    both=[d for d in DOMAINS if 'bart/'+d in completed and 't5gemma/'+d in completed]
    shared=[d for d in DOMAINS if all(presence[(m,d)]=={42,43,44} and (m+'/'+d in affected or m=='bart' and d in reviewed_domains) for m in MODELS)]
    a6='P的“当前正确、gold续步正确、latent下一步失败”在两模型均有三seed支持的领域为'+('、'.join(shared) if shared else '尚待三seed共同证据')+'。两模型全部三seed的正式N/S/M均完成并准入的领域为'+('、'.join(both) if both else '尚无全部完成的领域')+'；补训跨模型比较据此区分完整与部分结果。单模型准入失败与另一模型组合失败不能合并平均，T5Gemma实际是已核验2B IT而非270M IT，rank相同但编辑器参数量不同。'
    a7='最有证据的下一步是围绕已确认的“同当前文本、同mask/深度、下一步分歧”做受控兼容性和能力保护研究；分别验证来源、当前关系/角色状态和表达结构的覆盖。M覆盖更多状态但每状态监督减少；若稳定劣于S，需用匹配每状态监督及总监督的补充对照区分预算摊薄、状态梯度干扰和旧路径保护。这些是待检验解释，不是已发现机制。未准入领域优先解决固定接口的重构/原子能力。当前probe只支持可读性，不支持编辑器使用或因果机制；没有进行子空间干预。'
    return [a1,a2,a3,a4,a5,a6,a7]

if __name__=='__main__':
    text='\n\n'.join(f'{i}. {s}' for i,s in enumerate(research_answers(),1))
    (ROOT/'RESEARCH_ANSWERS.md').write_text('# 当前证据对七个研究问题的回答\n\n'+text+'\n');print(text)
