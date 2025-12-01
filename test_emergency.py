from backend.ai.reasoning_agent import get_emergency_info
import json

print("Testing Emergency Info for Sydney, Australia...")
info = get_emergency_info("Sydney", "Australia")
print(json.dumps(info, indent=2))

print("\nTesting Emergency Info for Mumbai, India...")
info_mumbai = get_emergency_info("Mumbai", "India")
print(json.dumps(info_mumbai, indent=2))
