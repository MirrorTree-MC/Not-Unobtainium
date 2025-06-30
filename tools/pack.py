import json
import os
import zipfile

# 获取当前工作目录
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pack_mcmeta_path = os.path.join(root, "pack.mcmeta")
assets_path = os.path.join(root, "assets")
pack_png_path = os.path.join(root, "pack.png")

# 读取 pack.mcmeta 获取 version
with open(pack_mcmeta_path, "r", encoding="utf-8") as f:
    meta = json.load(f)
version = meta.get("metadata", {}).get(
    "version", meta.get("pack", {}).get("version", "unknown")
)

zip_name = f"并非矿透 {version}.zip"
zip_path = os.path.join(root, zip_name)

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    # 添加 pack.mcmeta
    zipf.write(pack_mcmeta_path, "pack.mcmeta")
    # 添加 pack.png
    if os.path.exists(pack_png_path):
        zipf.write(pack_png_path, "pack.png")
    # 递归添加 assets 目录
    for foldername, subfolders, filenames in os.walk(assets_path):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, root)
            zipf.write(file_path, arcname)

print(f"已生成压缩包：{zip_name}")
