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
    data=get_log(filepath)
    findings = []
    # 提取文件名
    file_path_pattern = r'^(.*\.sol)'
    match=re.search(file_path_pattern, data, re.MULTILINE)
    if match:
        file_name = os.path.split(match.group(1))[1]
        success=True
    else:
        success=False
    # 提取行号、列号、级别、消息和漏洞名
    issues_pattern = r'(\d+:\d+)\s+(error|warning)\s+(.+?)\s+([a-zA-Z-]+)\s*$'
    issues = re.findall(issues_pattern, data, re.MULTILINE)
    for issue in issues:
        line_col, level, message, vulnerability = issue
        if level=="error" and not message.startswith("Compiler"):
            success=False
        findings.append({
            "filename": file_name,
            "line": int(line_col.split(':')[0]),
            "column": int(line_col.split(':')[1]),
            "message": message,
            "level": level,
            "name": vulnerability
        })

    return success,findings