import os
import glob

patch_files = glob.glob(".jules/patches/*.patch")
print(f"Found {len(patch_files)} patch files:\n")

for p in patch_files:
    task_name = os.path.basename(p).replace(".patch", "")
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    
    files = []
    for line in content.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" ")
            if len(parts) >= 4:
                files.append(parts[3][2:]) # strip b/
    print(f"[{task_name}]")
    for f in files:
        print(f"   -> {f}")
    print()
