import sys
sys.path.insert(0, "/d/SophiaAgentWork/aurora-agent")
from aurora.business_plan.secret_outline import get_core_outline

text = get_core_outline()
print(text[:1000])  # Print first 1000 chars to understand formatting
