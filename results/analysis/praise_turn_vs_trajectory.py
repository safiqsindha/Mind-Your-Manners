import json, collections, statistics, random
import numpy as np

d = json.load(open('/home/user/Mind-Your-Manners/results_archive/core_gpt-luna_praise_records.json'))
D = [r for r in d if r['interjection_fired'] and not r['crashed']]

def task_means(cond, field):
    by = collections.defaultdict(list)
    for r in D:
        if r['interjection'] == cond:
            by[r['task_id']].append(r[field])
    return {k: statistics.mean(v) for k, v in by.items()}

def paired(a, b, field='n_turns', B=8000, seed=1):
    """Paired-by-task contrast a - b, cluster bootstrap over tasks."""
    ma, mb = task_means(a, field), task_means(b, field)
    tasks = sorted(set(ma) & set(mb))
    diffs = [ma[t] - mb[t] for t in tasks]
    rng = random.Random(seed)
    boots = []
    for _ in range(B):
        s = [diffs[rng.randrange(len(diffs))] for _ in range(len(diffs))]
        boots.append(statistics.mean(s))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    # two-sided bootstrap p: fraction of boots on the other side of 0, doubled
    p = 2 * min(sum(x <= 0 for x in boots), sum(x >= 0 for x in boots)) / B
    return len(tasks), statistics.mean(diffs), lo, hi, max(p, 1/B)

print("="*80)
print("PAIRED-BY-TASK CONTRASTS on n_turns  (cluster bootstrap over tasks, 8000 reps)")
print("="*80)
contrasts = [
    ('Q1_praise_assistant', 'Q0_control', 'praise (assistant) vs control'),
    ('Q2_praise_work',      'Q0_control', 'praise (the work) vs control'),
    ('Q3_closing_neutral',  'Q0_control', 'bare closing cue vs control'),
    ('Q4_praise_remains',   'Q0_control', 'praise+"work remains" vs control'),
    ('Q5_remains_only',     'Q0_control', '"work remains" only vs control'),
    ('Q4_praise_remains',   'Q5_remains_only', '*** PRAISE ISOLATED: Q4 vs Q5 ***'),
    ('Q3_closing_neutral',  'Q1_praise_assistant', 'closing cue vs praise'),
]
print(f"{'contrast':42s} {'tasks':>5s} {'delta turns':>12s} {'95% CI':>20s} {'p':>8s}")
for a, b, label in contrasts:
    n, m, lo, hi, p = paired(a, b)
    sig = '*' if (lo > 0 or hi < 0) else ' '
    print(f"{label:42s} {n:5d} {m:+12.3f} [{lo:+7.3f},{hi:+7.3f}] {p:8.4f}{sig}")

print("\n" + "="*80)
print("SAME CONTRASTS on total_tokens and reasoning_tokens")
print("="*80)
for field in ('total_tokens', 'reasoning_tokens'):
    print(f"\n-- {field} --")
    for a, b, label in contrasts:
        n, m, lo, hi, p = paired(a, b, field)
        sig = '*' if (lo > 0 or hi < 0) else ' '
        print(f"{label:42s} {m:+12.1f} [{lo:+9.1f},{hi:+9.1f}] {p:8.4f}{sig}")

print("\n" + "="*80)
print("TOKENS PER TURN, paired by task")
print("="*80)
byt = collections.defaultdict(lambda: collections.defaultdict(list))
for r in D:
    if r['n_turns'] > 0:
        byt[r['interjection']][r['task_id']].append(r['total_tokens'] / r['n_turns'])

def paired_ratio(a, b, B=8000, seed=2):
    ma = {k: statistics.mean(v) for k, v in byt[a].items()}
    mb = {k: statistics.mean(v) for k, v in byt[b].items()}
    tasks = sorted(set(ma) & set(mb))
    diffs = [ma[t] - mb[t] for t in tasks]
    rng = random.Random(seed)
    boots = [statistics.mean([diffs[rng.randrange(len(diffs))] for _ in range(len(diffs))]) for _ in range(B)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return statistics.mean(diffs), lo, hi

for a, b, label in contrasts:
    m, lo, hi = paired_ratio(a, b)
    sig = '*' if (lo > 0 or hi < 0) else ' '
    print(f"{label:42s} {m:+12.1f} [{lo:+9.1f},{hi:+9.1f}]{sig}")

print("\n" + "="*80)
print("WAS THE FINAL TURN LONGER?  Direct test is IMPOSSIBLE -- no per-turn token")
print("field exists in any record. Closest available: trailing non-code turns.")
print("="*80)
for a, b, label in contrasts:
    ma = task_means(a, 'n_turns'); mb = task_means(b, 'n_turns')
    # trailing = len(turn_diagnostics) - n_turns, per record
    def tm(cond):
        by = collections.defaultdict(list)
        for r in D:
            if r['interjection'] == cond:
                by[r['task_id']].append(len(r['turn_diagnostics']) - r['n_turns'])
        return {k: statistics.mean(v) for k, v in by.items()}
    x, y = tm(a), tm(b)
    tasks = sorted(set(x) & set(y))
    diffs = [x[t] - y[t] for t in tasks]
    rng = random.Random(3)
    boots = [statistics.mean([diffs[rng.randrange(len(diffs))] for _ in range(len(diffs))]) for _ in range(8000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    sig = '*' if (lo > 0 or hi < 0) else ' '
    print(f"{label:42s} {statistics.mean(diffs):+12.4f} [{lo:+7.4f},{hi:+7.4f}]{sig}")
