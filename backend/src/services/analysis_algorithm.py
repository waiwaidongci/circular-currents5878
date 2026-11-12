from src.services.circular_algorithm import summarize
from src.services.energy_algorithm import compare
from src.services.daily_algorithm import daily_map,pair_days,compare_paired
from src.utils.fingerprint import fingerprint
def analyze_records(a,b,config):
    result={'method':'record','a':summarize([r['bearing'] for r in a]),'b':summarize([r['bearing'] for r in b]),'energy':compare([r['bearing'] for r in a],[r['bearing'] for r in b],config['permutations'],config['seed'])}
    result['input_snapshot']={'a':a,'b':b,'config':config}
    result['fingerprint']=fingerprint({'algorithm':'circular-energy-v1','a':a,'b':b,'config':config});result['interpretation']='两组单位圆分布差异；小p不代表差异大小、成因或航行风险。交换性要求观测独立；同浮标连续时间自相关可能破坏置换前提。'
    return result
def analyze_daily(a,b,config):
    days_a=daily_map(a);days_b=daily_map(b)
    included,excluded=pair_days(days_a,days_b)
    if len(included)<2:raise ValueError('按日配对后共同有效日期不足2天，拒绝计算')
    means_a=[d['a_mean'] for d in included];means_b=[d['b_mean'] for d in included]
    result={'method':'daily','a':summarize(means_a),'b':summarize(means_b),'energy':compare_paired(means_a,means_b,config['permutations'],config['seed']),'daily':{'timezone':'UTC','paired_days':len(included),'included':included,'excluded':excluded}}
    result['input_snapshot']={'a':a,'b':b,'config':config}
    result['fingerprint']=fingerprint({'algorithm':'circular-energy-daily-v1','a':a,'b':b,'config':config});result['interpretation']='按UTC日期配对的日均值比较：每天等权，置换只在同一UTC日内交换浮标标签；未纳入日期已列出原因。日均值掩盖日内分布与自相关，小p不代表差异大小、成因或航行风险。'
    return result
def analyze(rows_a,rows_b,config):
    a=sorted(rows_a,key=lambda r:r['code']);b=sorted(rows_b,key=lambda r:r['code'])
    if config.get('method','record')=='daily':return analyze_daily(a,b,config)
    return analyze_records(a,b,config)
