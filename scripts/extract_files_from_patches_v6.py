import os
import glob
import re

def extract_new_files_from_patch(patch_path):
    with open(patch_path, "r", encoding="utf-8") as f:
        patch_text = f.read()

    chunks = re.split(r"(?=diff --git )", patch_text)
    extracted = {}

    for chunk in chunks:
        if not chunk.strip():
            continue
        lines = chunk.split("\n")
        header = lines[0]
        m = re.match(r"diff --git a/(.*?) b/(.*?)$", header)
        if not m:
            continue
        target_file = m.group(2)
        
        is_new = any("new file mode" in l for l in lines[:5])
        
        if is_new or target_file.startswith("tests/") or (not os.path.exists(target_file) and not target_file.endswith(".patch")):
            content_lines = []
            in_hunk = False
            for line in lines:
                if line.startswith("@@"):
                    in_hunk = True
                    continue
                if in_hunk:
                    if line.startswith("+"):
                        content_lines.append(line[1:])
                    elif line.startswith(" "):
                        content_lines.append(line[1:])
            extracted[target_file] = "\n".join(content_lines)
            
    return extracted

def main():
    patch_files = glob.glob(".jules/patches_v6/*.patch")
    print(f"Processing {len(patch_files)} patches in .jules/patches_v6/...")
    
    total_written = 0
    for p in patch_files:
        task_name = os.path.basename(p).replace(".patch", "")
        new_files = extract_new_files_from_patch(p)
        print(f"\n[{task_name}]")
        for fpath, content in new_files.items():
            if fpath.endswith(".patch") or fpath.startswith("test_env") or fpath.startswith("run_"):
                continue
            if not fpath.endswith("__init__.py") and not fpath.endswith("prompts.py") and not fpath.endswith("models.py") and len(content.strip()) > 0:
                os.makedirs(os.path.dirname(os.path.abspath(fpath)), exist_ok=True)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"   -> Wrote {fpath} ({len(content)} chars)")
                total_written += 1
            else:
                print(f"   -> SKIPPED shared/empty file: {fpath}")

    print(f"\nTotal new files written: {total_written}")

if __name__ == "__main__":
    main()
