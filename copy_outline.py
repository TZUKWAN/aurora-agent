
import shutil
import os

src_path = r"D:\计划书AI\outline_with_prompts.json"
dst_path = r"d:\LATEXTEST\aurora-agent\outline_with_prompts.json"

if os.path.exists(src_path):
    shutil.copy(src_path, dst_path)
    print(f"成功复制大纲文件到: {dst_path}")
else:
    print(f"源文件不存在: {src_path}")
