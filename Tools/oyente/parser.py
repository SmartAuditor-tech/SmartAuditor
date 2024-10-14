import re
import os
import yaml

def get_log(filepath):
    try:
        with open(filepath, 'r') as f:
            data = f.read()
    except Exception as e:
        print(f"Parse txt file failed as: {e}")
        return None
    return data

def get_yaml(filepath):
    try:
        with open(filepath, 'r') as f:
            vulfinding = yaml.safe_load(f)
    except Exception as e:
        print(f"open yaml failed as: {e}")
        return None
    return vulfinding

def parse(filepath: str):
    data = get_log(filepath).strip()
    findings = {}
    findings["vul"] = []
    findings["filename"] = os.path.split(filepath)[1].replace(".txt", ".sol")
    warnings = []
    success = False

    # 使用正则表达式来匹配 WARNING 信息
    warnings = re.findall(r"WARNING:root:\s+(.+)", data)
    # 查找结果开始的标记
    result_pattern = re.search(r"=+\s+Results\s+=+", data)
    if not result_pattern:
        findings["warnings"] = warnings
        return success, findings

    current_dir = os.path.dirname(os.path.abspath(__file__))
    vulfinding = get_yaml(os.path.join(current_dir, 'findings.yaml'))

    # 匹配 incomplete push instruction 错误
    incomplete_match = re.search(r"incomplete push instruction at (\d+)", data)
    if incomplete_match:
        findings["incomplete instruction"] = incomplete_match.group(1)

    # 查找所有的漏洞信息，处理 INFO:symExec 行
    vulnerabilities_true = re.findall(r"INFO:symExec:\s+(.*?):\s+True", data)
    for vul in vulnerabilities_true:
        vul_name = vul.split(":")[0]
        vulinfo = vulfinding.get(vul_name, {})
        classification = vulinfo.get('classification', 'No classification')
        findings["vul"].append(f"{vul_name}: {classification}")

    # 匹配 EVM 代码覆盖率
    percentage_match = re.search(r"EVM\s+Code\s+Coverage:\s+(\d+\.\d+%)", data)
    if percentage_match:
        findings["coverage"] = percentage_match.group(1)
    else:
        findings["coverage"] = ""

    # 检查分析是否完成

    if re.search(r"Analysis\s+Completed", data):
        success = True
    else:
        success = False

    findings["warnings"] = warnings
    return success, findings
