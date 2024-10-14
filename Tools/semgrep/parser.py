import os,yaml,re
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
def message_lines(log_iterator):
    message_lines = []
    while True:
        next_line = next(log_iterator, '').strip()
        if not next_line:
            break
        message_lines.append(next_line)
    return ' '.join(message_lines)

def parse(filepath):
    data=get_log(filepath)
    
    
    
    log_iterator = iter(data.split('\n'))
    current_dir=os.path.dirname(os.path.abspath(__file__))
    vulfinding=get_yaml(os.path.join(current_dir, 'findings.yaml'))
    findings= []
    finding = {}
    for line in log_iterator:
        
        finding["classification"]=[]
        line = line.strip()

        # if line.startswith('/'):
        #     filename = line.split("/")
        #     filename = '/'.join(filename[-2:])
        #     finding = {'filename': filename}

        if re.search(r'solidity\.(performance|best-practice|security)\.', line):
            match = re.search(r'solidity\.(performance|best-practice|security)\.([^.]+)', line)
            category = match.group(1)
            name = match.group(2)
            vulinfo=vulfinding.get(name,'No')
            if not vulinfo=='No':
                classification=vulinfo.get('classification','No')
                if not classification=='No':
                    if "," in classification:
                        for i in classification.split(","):
                            finding["classification"].append(i)
                    else:
                        finding["classification"].append(classification)
            finding['name'] = name
            finding['category'] = category
            finding['message'] = message_lines(log_iterator)
            
        elif re.search(r'\d+┆', line):
            line_location = line.strip().split('┆', 1)
            if len(line_location) > 0:
                cline_number = int(line_location[0])
                finding['line'] = cline_number
        
            findings.append(finding.copy())

    if len(findings)==0:
        success=False
    else:
        success=True
    return success,findings