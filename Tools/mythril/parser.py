import json,os
import re,yaml

def get_log(filepath):
    try:
        with open(filepath,'r') as f:
            data=f.read()
    except Exception as e:
        print(f"Parse txt file failed as: {e}")
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
    data=get_log(filepath).strip()
    findings=[]
    success=True
    if data.startswith("mythril") or data=="":
        success=False
        return success,findings  
    if data.startswith("The analysis was completed successfully. No issues were detected."):
        success=True
        return success,findings
    filename=os.path.split(filepath)[1].replace(".txt",".sol")
    
    big_sections = re.split(r'====.*?====', data)

    for section in big_sections:
        if not section.strip():
            continue
        finding={}
        finding["filaname"]=filename
        # Step 2: 分割小段落
        small_sections = re.split(r'---+', section)

        useful_info = ""
        in_file_info = ""

        for small_section in small_sections:
            small_section = small_section.strip()

            # Step 3: 提取以 SWC 开头的小段落
            if small_section.startswith("SWC"):
                useful_info = small_section
            for line in useful_info.split("\n"):
                if ':' in line:
                    info=line.split(":")
                    finding[info[0]]=info[1]
                else:
                    finding["description"]=line
            # Step 4: 提取以 In file 开头的行
            in_file_match = re.search(r'In file:.*', small_section)
            if in_file_match:
                in_file_info = in_file_match.group()
                finding["line"]=in_file_info.split(':')[-1]

            # Step 5: 忽略以 Initial State 开头的小段落
            if small_section.startswith("Initial State"):
                continue
        findings.append(finding.copy())
    return True,findings
          