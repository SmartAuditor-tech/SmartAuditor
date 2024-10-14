import json,os
import re,yaml
pattern = r'#(\d+(-\d+)?)'
def get_json(filepath):
    try:
        with open(filepath,'r') as f:
            data=json.load(f)
    except Exception as e:
        print(f"Parse json file failed as: {e}")
        return None
    return data
def get_yaml(filepath):
    try:
        with open(filepath,'r') as f:
            vulfinding=yaml.safe_load(f)
    except Exception as e:
        print(f"open yaml failed as: {e}")
        return None
    return vulfinding
def parse(filepath):
    data=get_json(filepath)
    findings=[]
    success=True
    if not data['success']:
        success=False
        
        return success,findings
    
    issues=data['results'].get('detectors',None)
    if not issues:
        return success,findings
    current_dir=os.path.dirname(os.path.abspath(__file__))
    vulfinding=get_yaml(os.path.join(current_dir, 'findings.yaml'))
    for issue in issues:
        finding={}
        for i,f in ( ("check", "name"), ("impact", "impact" ),
            ("confidence", "confidence"), ("description", "message")):
            finding[f]=issue[i]
        finding["filename"]=os.path.split(filepath)[1].replace(".json",".sol")
        elements=issue.get("elements",[])
        finding["classification"]=[]
        for element in elements:
            if element.get("type")=="function":
                finding["function"]=element["name"]
                parent = element.get("type_specific_fields", {}).get("parent")
                if parent and parent.get("type") == "contract":
                    finding["contract"] = parent.get("name", "")
                else:
                    finding["contract"] = ""

            break
        matches=re.findall(pattern,issue["description"])
        lines=matches[-1][0]
        if "-" in lines:
            start,end=lines.split("-")
            finding["line"]=int(start)
            finding["line_end"]=int(end)
        else:
            finding["line"]=int(lines)
        
        try:
            vulinfo=vulfinding[issue["check"]]
            classification=vulinfo.get('classification','No')
            if not classification=='No':
                if "," in classification:
                    for i in classification.split(","):
                        finding["classification"].append(i)
                else:
                    finding["classification"].append(classification)
        except Exception as e:
            print(issue['check'])
            print(f"Classify failed as: {e}")
        
        findings.append(finding.copy())
    return success,findings
    