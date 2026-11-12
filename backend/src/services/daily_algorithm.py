import numpy as np
from datetime import datetime,timezone
from src.services.energy_algorithm import chord_matrix,statistic
EPS=1e-8
def parse_instant(raw,code):
    if not isinstance(raw,str) or not raw.strip():raise ValueError(f'采样{code}时刻为空；按日配对研究拒绝计算')
    try:moment=datetime.fromisoformat(raw.strip())
    except ValueError:raise ValueError(f'采样{code}时刻无效：{raw!r}；按日配对研究要求ISO 8601带时区时刻，拒绝计算')
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:raise ValueError(f'采样{code}时刻缺少时区：{raw!r}；按日配对研究要求带时区时刻，拒绝计算')
    return moment.astimezone(timezone.utc)
def daily_map(rows):
    days={}
    for r in rows:days.setdefault(parse_instant(r['observed_at'],r['code']).date().isoformat(),[]).append(r['bearing'])
    return days
def circular_mean(values):
    theta=np.deg2rad(np.asarray(values,dtype=float));c=float(np.cos(theta).mean());s=float(np.sin(theta).mean());r=float(np.clip(np.hypot(c,s),0,1))
    mean=None if r<EPS else float(np.rad2deg(np.arctan2(s,c))%360)
    if mean is not None and (mean<1e-10 or 360-mean<1e-10):mean=0.0
    return {'n':len(values),'mean':mean,'resultant':r}
def pair_days(days_a,days_b):
    included=[];excluded=[]
    for day in sorted(set(days_a)|set(days_b)):
        a=days_a.get(day);b=days_b.get(day)
        if a is None:excluded.append({'date':day,'reason':'missing_a','a_n':0,'b_n':len(b)});continue
        if b is None:excluded.append({'date':day,'reason':'missing_b','a_n':len(a),'b_n':0});continue
        ma=circular_mean(a);mb=circular_mean(b);reasons=[]
        if ma['mean'] is None:reasons.append('mean_undefined_a')
        if mb['mean'] is None:reasons.append('mean_undefined_b')
        if reasons:excluded.append({'date':day,'reason':'+'.join(reasons),'a_n':ma['n'],'b_n':mb['n']});continue
        included.append({'date':day,'a_mean':ma['mean'],'b_mean':mb['mean'],'a_n':ma['n'],'b_n':mb['n'],'a_resultant':ma['resultant'],'b_resultant':mb['resultant']})
    return included,excluded
def compare_paired(a_means,b_means,repetitions,seed):
    a=np.asarray(a_means,float);b=np.asarray(b_means,float);n=len(a)
    if n<2 or n>250:raise ValueError('按日配对研究须2–250个共同有效日期')
    if not 1<=repetitions<=999:raise ValueError('置换次数无效')
    d=chord_matrix(a,b);order=np.arange(2*n);left=order[:n];right=order[n:];observed=statistic(d,left,right);rng=np.random.default_rng(seed);null=[]
    for _ in range(repetitions):
        swap=rng.random(n)<.5;null.append(statistic(d,np.where(swap,right,left),np.where(swap,left,right)))
    extreme=sum(x>=observed-1e-12 for x in null)
    return {'statistic':observed,'p_value':(extreme+1)/(repetitions+1),'extreme':extreme,'permutations':repetitions,'seed':seed,'null_statistics':null,'null_quantiles':np.quantile(null,[.025,.5,.975]).tolist(),'definition':'V-energy on UTC daily circular means (one per buoy per included day, equal weight); permutations swap buoy labels only within the same UTC day; upper-tail with +1 correction'}
