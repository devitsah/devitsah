import numpy as np, json, random

d = np.load('/home/claude/work/gen/dots_full.npy')       # 1 = dark/ink pixel
mask = np.load('/home/claude/work/gen/mask_subject.npy') # subject region

light_dots = (d == 1)                 # light mode: draw the dark parts of the photo
dark_dots  = (d == 0) & mask          # dark mode: draw the lit subject only (no negative)

def to_runs(bitmap):
    """row-wise run-length encode into (row, start, length) runs."""
    runs = []
    h, w = bitmap.shape
    for y in range(h):
        row = bitmap[y]
        x = 0
        while x < w:
            if row[x]:
                x0 = x
                while x < w and row[x]:
                    x += 1
                runs.append((y, x0, x - x0))
            else:
                x += 1
    return runs

light_runs = to_runs(light_dots)
dark_runs  = to_runs(dark_dots)
print("light runs", len(light_runs), "dark runs", len(dark_runs))

# assign interleaved intro-fade groups: scattered across whole portrait, not by region
random.seed(42)
NGROUPS = 60
def assign_groups(runs):
    idx = list(range(len(runs)))
    random.shuffle(idx)
    grouped = [[] for _ in range(NGROUPS)]
    for i, ridx in enumerate(idx):
        grouped[i % NGROUPS].append(runs[ridx])
    return grouped

light_groups = assign_groups(light_runs)
dark_groups  = assign_groups(dark_runs)

json.dump({"light": light_groups, "dark": dark_groups}, open('/home/claude/work/gen/groups.json','w'))
print("done")
