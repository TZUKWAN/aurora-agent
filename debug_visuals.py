import os
import sys

os.environ["AURORA_API_KEY"] = "a683b3076098052127efb398131f91a6.P0ra5oXeAo0U8ZVZ"
os.environ["AURORA_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"
os.environ["AURORA_MODEL"] = "glm-4.7-flash"

sys.path.insert(0, "/d/SophiaAgentWork/aurora-agent")

from aurora.visuals.designer import VisualDesigner

vd = VisualDesigner()
html = vd.generate_html({"name": "Test", "track": "Tech"}, "product_service")
print("HTML OUPUT:")
print(html)
