import sys
import docx
import json
import re

sys.path.insert(0, "/d/SophiaAgentWork/aurora-agent")

def extract_prompts_from_docx():
    docx_path = "/d/SophiaAgentWork/aurora-agent/商业计划书大纲2026.docx"
    doc = docx.Document(docx_path)
    
    sections = {}
    current_title = None
    current_content = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Very simple heuristic: short lines usually are section titles in the document
        if len(text) < 15 and not text.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')):
            # Save previous
            if current_title:
                sections[current_title] = "\n".join(current_content)
                current_content = []
            current_title = text
        else:
            if current_title:
                current_content.append(text)
                
    if current_title:
        sections[current_title] = "\n".join(current_content)
        
    return sections

try:
    sections = extract_prompts_from_docx()
    with open("parsed_prompts.json", "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    print("Parsed successfully into parsed_prompts.json")
except Exception as e:
    import traceback
    traceback.print_exc()
