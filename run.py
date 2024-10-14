import argparse
import logging
from codeExtractor import codeExtractor
import re
import pickle
import subprocess
import json
import os
from SetUp import setup
from Scopes.curves import AuditScopes
from Analyzer import analyzer
from collections import defaultdict



class Environment:
    def __init__(self, args, node_module_path,files,remappings,foundry_content,dependencies, solc, scopes, to_compile,test_info ,packageJson=None,exist_dependencies=None):
        self.platform = args.platform
        self.dir = args.project
        
        self.nodejs = args.nodejsv
        self.npm = args.npmv
        self.requiredSolc = solc
        self.localSolc = args.solcv
        #返回目标文件下的文件树，并忽略掉部分文件类型
        self.pathTree = getPathTree(self.platform,self.dir)
        self.solidityPathTree = getSolidityPathTree(self.platform,self.dir)
        self.node_module_path=node_module_path
        self.files=files
        self.remappings=remappings
        self.foundry_content=foundry_content
        self.dependencies = dependencies
        self.askToken=0
        self.anwserToken=0
        self.scopes=scopes
        self.toCompile = to_compile
        self.toAnalyze=to_compile
        self.test_info=test_info
        self.packageJson = packageJson
        self.exist_dependencies=exist_dependencies
        self.buildPath=""
        self.framework=""
    def get_path_tree(self):
        self.pathTree = getPathTree(self.platform,self.dir)
        return self.pathTree
    def get_solidity_path_tree(self):
        self.solidityPathTree = getSolidityPathTree(self.platform,self.dir)
        return self.solidityPathTree
    def getEnvironmentDescription(self):
        return f'''Operating System: {self.platform}
Project Absolute Path: {self.dir}
Node.js Version: {self.nodejs}
npm version: {self.npm}
Required Solc Version for Contracts: {self.requiredSolc}
Current Local Solc Version: {self.localSolc}
Library Dependencies: {self.dependencies}
Solc-select Installation: solc-select has been installed and added to the PATH. You can directly use it in the command line.
Project Layout: {self.pathTree}
Contracts in Scope: {self.scopes if len(self.scopes)<30 else "All the contracts in the project"}'''

def find_top_level_package_json(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        for file in files:
            if file.lower() == 'package.json':
                return os.path.join(root, file)
    return None

def parse_package_json(file):
    with open(file, 'r') as file:
        package_data = json.load(file)
    dependencies = package_data.get('dependencies', {})
    dev_dependencies = package_data.get('devDependencies', {})
    #合并依赖项
    res = {**dependencies, **dev_dependencies}
    return res

def init_package_json(project):
    command = ['npm', 'init', '-y']
    try:
        result = subprocess.run(command, cwd = project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return os.path.join(project, "package.json")
    except subprocess.CalledProcessError as e:
        logging.error(e)
        return ''

def update_package_json(filename, dependency_dict):
    with open(filename, 'r') as file:
        package_data = json.load(file)
    package_data.pop('dependencies', None)
    package_data.pop('devDependencies', None)

    package_data['dependencies'] = dependency_dict
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(package_data, file, indent=2, ensure_ascii=False)


def find_readme_with_contracts(folder_path):
    readme_paths = []
    for root, dirs, files in os.walk(folder_path):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')

        has_contract = False
        for dirpath, dirnames, filenames in os.walk(root):
            if any(file.endswith('.sol') for file in filenames):
                has_contract = True
                break

        if has_contract:
            readme_path = os.path.join(root, 'README.md')
            if os.path.exists(readme_path):
                readme_paths.append(os.path.abspath(readme_path))

    return list(set(readme_paths))  

# def find_test_info(filename):
#     with open(filename, 'r', encoding='utf-8') as f:
#         content = f.read()

#     in_code_block = False
#     current_section = None
#     current_level = None
#     section_content = {'test': '', 'install': ''}
#     lines = content.split('\n')

#     for line in lines:
#         # Check for code block toggling
#         if line.strip().startswith('```'):
#             in_code_block = not in_code_block
#             if line.strip().endswith('```') and line.strip()!='```':
#                 in_code_block = not in_code_block
#             if current_section:
#                 section_content[current_section] += line + '\n'
#             continue

#         # Match titles containing 'test' or 'install'
#         if not in_code_block:
#             match_test = re.search(r"(?i)^(#+)\s*.*\btest\w*\b.*", line)
#             match_install = re.search(r"(?i)^(#+)\s*.*\binstall\w*\b.*", line)

#             if match_test:
#                 current_section = 'test'
#                 current_level = len(match_test.group(1))
#                 section_content[current_section] += line + '\n'
#                 continue
#             elif match_install:
#                 current_section = 'install'
#                 current_level = len(match_install.group(1))
#                 section_content[current_section] += line + '\n'
#                 continue

#             if current_section:
#                 # Check if it's a new title of the same or higher level
#                 match_new_title = re.match(r"^(#+)\s", line)
#                 if match_new_title and len(match_new_title.group(1)) <= current_level:
#                     current_section = None
#                 else:
#                     section_content[current_section] += line + '\n'
#         else:
#             if current_section:
#                 section_content[current_section] += line + '\n'

#     result = section_content['install'] + '\n' + section_content['test']
#     if result.strip():
#         return result.strip()
#     else:
#         return "No content found under 'test' or 'install' section"

import re

def find_test_info(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    in_code_block = False
    current_section = None
    current_level = None
    section_content = {'test': '', 'install': '', 'compile': ''}
    lines = content.split('\n')

    for line in lines:
        # Toggle code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if current_section:
                section_content[current_section] += line + '\n'
            continue

        # Process non-code block lines
        if not in_code_block:
            match_test = re.search(r"(?i)^(#+)\s*.*\btest\w*\b.*", line)
            match_install = re.search(r"(?i)^(#+)\s*.*\binstall\w*\b.*", line)
            match_compile = re.search(r"(?i)^(#+)\s*.*\bcompile\w*\b.*", line)

            if match_test:
                current_section = 'test'
                current_level = len(match_test.group(1))
                section_content[current_section] += line + '\n'
                continue
            elif match_install:
                current_section = 'install'
                current_level = len(match_install.group(1))
                section_content[current_section] += line + '\n'
                continue
            elif match_compile:
                current_section = 'compile'
                current_level = len(match_compile.group(1))
                section_content[current_section] += line + '\n'
                continue

            if current_section:
                match_new_title = re.match(r"^(#+)\s", line)
                if match_new_title and len(match_new_title.group(1)) <= current_level:
                    current_section = None  # Reset section if a new title of same/higher level is found
                else:
                    section_content[current_section] += line + '\n'
        else:
            if current_section:
                section_content[current_section] += line + '\n'

    # Combine install, test, and compile sections for output
    result = section_content['install'] + '\n' + section_content['test'] + '\n' + section_content['compile']
    return result.strip() if result.strip() else "No content found under 'test', 'install', or 'compile' section"

def find_solidity_imports(folder_path):
    libraries = set()
    exist_dependencies=set()
    for root, dirs, files in os.walk(folder_path):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # Skip the node_modules directory
        for file in files:
            if file.endswith('.sol'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    # Modify the regular expression to match both styles of import statements
                    #import {lib} from {.sol}
                    imports = re.findall(r'import(\s+\{[^}]+\}\s+from\s+)?\s*["\']([^"\']+)["\']', content)
                    for imp in imports:
                        imp_path = imp[1]  # Extract the actual path from the match tuple
                        imp_path = os.path.join(root, imp_path)
                        # Check if the imported file exists
                        #！！！需要修改这里，找到不存在的.sol文件
                        if not os.path.exists(imp_path):
                            libraries.add(imp[1])
                        else:
                            exist_dependencies.add(imp[1])
    #library用于存储系统中不存在的模块
    return [ x for x in list(libraries)],[x for x in list(exist_dependencies)]

def find_solc_versions(folder_path):
    solidity_versions = set()
    for file in folder_path:
        with open(file,'r',encoding='utf-8') as sol_file:
            content = sol_file.read()
            matches = re.findall(r'pragma solidity (\S+);', content)
            solidity_versions.update(matches)
    return list(solidity_versions)

def getPathTree(platform, dir):
    if platform == 'linux':
        command = ['tree', dir, '-I', 'node_modules|interfaces|build|test|artifacts|mock|*.js|*.ts']
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if len(result.stdout) > 10000:
            command = ['tree', dir, '-P', '*.sol|*.json|*.bin|*.bin-runtime', '-I', 'node_modules', '-L', '4']
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if len(result.stdout)> 10000:
                return ''
        return '\n'.join(result.stdout.split('\n')[:-2])
    return 'Error'+platform

def getSolidityPathTree(platform, dir):
    if platform=='linux':
        command = ['tree', dir, '-P', '*.sol', '-I', 'node_modules|interfaces|build|test|artifacts|mock|*.js|*.ts']
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if len(result.stdout)>50000:
            return ''
        return '\n'.join(result.stdout.split('\n')[:-2])
    
    return ''

def find_contract_names(solidity_code):
    # 正则表达式匹配模式，用于找到合约名称，忽略继承部分
    pattern = r'contract\s+([A-Za-z0-9_]+)(?:\s+is\s+[A-Za-z0-9_,\s]*)?\s*{'
    # 使用正则表达式找到所有匹配项
    matches = re.findall(pattern, solidity_code)

    return matches

def parse_imports(file_content, current_file_path):
    imports = re.findall(r'import\s+["\'](.+?)["\']', file_content)
    absolute_imports = []
    for imp in imports:
        if os.path.isabs(imp):
            absolute_imports.append(imp)
        else:
            # 将相对路径转换为绝对路径
            base_dir = os.path.dirname(current_file_path)
            absolute_path = os.path.normpath(os.path.join(base_dir, imp))
            absolute_imports.append(absolute_path)
    return absolute_imports

def analyze_dependencies(file_paths):
    # 分析依赖关系，返回入度为0的合约的绝对地址列表
    dependencies = defaultdict(set)  # key为合约绝对地址，value为依赖该合约的合约绝对地址集合

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_content = f.read()
            imported_contracts = parse_imports(file_content, file_path)
            for imp_contract in imported_contracts:
                dependencies[imp_contract].add(file_path)

    # 找到入度为0的合约（即没有被任何合约import的合约）
    independent_contracts = [contract for contract in file_paths if contract not in dependencies]

    return independent_contracts

def has_compiled(project,base_name):
    if 'build' in os.listdir(project) and len(os.listdir(os.path.join(project,'build')))>=1:
        return [x for x in os.listdir(os.path.join(project,'build')) if (x.endswith('.bin') or x.endswith('.bin-runtime') or x.endswith('.abi')) and x.split('.')[0] in base_name]
    else:
        return []


def get_all_folders(dir_path):
    # 获取目录下所有文件和文件夹
    all_items = os.listdir(dir_path)
    
    # 过滤出文件夹
    folders = [item for item in all_items if os.path.isdir(os.path.join(dir_path, item))]
    return folders

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bot for Code4Rena")

    parser.add_argument("--project", type=str, help="the folder (the whole project) to analyze", default='None')
    
    parser.add_argument("--platform", type=str, help="the local os", default='linux')
    
    parser.add_argument("--solcv", type=str, help="local solc version", default='0.8.4')

    parser.add_argument("--nodejsv", type=str, help="local nodejs version", default='20.11.0')

    parser.add_argument("--npmv", type=str, help="local npm version", default='10.2.4')

    parser.add_argument("--timeout", type=str, help="timeout (in seconds) for each analysis task (per tool, per contract)", default=600)
    
    parser.add_argument("--setup_cache", type=str, help="the folder to cache the setup & compile result", default=None)
    
    parser.add_argument("--setup_message", type=str, help="developer's instructions about setup", default=None)

    parser.add_argument("--lib",type=str,help="the direction of the dependencies ",default=None)

    parser.add_argument("--process",type=int,help="the number of docker processes",default=2)

    parser.add_argument("--request",type=str,help="user request for bot",default=None)
    args = parser.parse_args()
    
    if args.setup_cache is None:
        if 'setup_cache' not in os.listdir(args.project):
            os.mkdir(os.path.join(args.project, 'setup_cache'))
        args.setup_cache =  os.path.join(args.project, 'setup_cache')
    

    return args


def load_setup_info(cache_folder, project):
    
    f = cache_folder + "/setup.txt"
    with open(f, 'rb') as fr:
        return pickle.loads(fr.read())

def store_setup_info(cache_folder, project, content):
    f = cache_folder + "/setup.txt"
    with open(f, 'wb+') as fo:
        s = pickle.dumps(content)
        fo.write(s)
    return
def read_remappings(remappings_file):
    remappings = {}
    with open(remappings_file, 'r') as f:
        for line in f:
            if '=' in line:
                alias, path = line.strip().split('=')
                remappings[alias] = os.path.normpath(path)
    return remappings
def read_foundry(foundry_file):
    content=''
    with open(foundry_file,'r') as f:
        content=f.read()
    return content
def auditProject():
    args = parse_arguments()
    Readme=args.setup_message
    test_info=''
    if Readme:
        test_info=find_test_info(Readme)
        #print("test_info"+str(test_info))
    
    remappings={}
    if os.path.exists(os.path.join(args.project,"remappings.txt")):
        remappings_file=os.path.join(args.project,"remappings.txt")
        remappings=read_remappings(remappings_file)
        #print("remappings.txt:"+str(remappings))
    foundry_content=''
    if os.path.exists(os.path.join(args.project,"foundry.toml")):
        foundry_content=read_foundry(os.path.join(args.project,"foundry.toml"))
    files,node_module_path = codeExtractor.get_source_code_from_foler(args.project,remappings)
    file2Codes = {}
    newScope = []
    
    #files内包含扫描文件夹下所有文件的路径、文件夹路径和文件代码
    for x in files:
        # if 'mock' not in x['path'].lower() and 'node_modules' not in x['path']:
        if 'node_modules' not in x['path']:    
            newScope.append(x['path'])
    Scopes = newScope
    for f in Scopes:
        try:
            fo = open(f['path'],'r')
            file2Codes[f['path']] = fo.readlines()
            fo.close()
        except:
            continue
    to_compiled_contracts  = []
    for x in Scopes:
        for y in AuditScopes:
            #将包含在auditscope中的待编译合约添加到数组中
            if y.lower() ==os.path.split(x.lower())[1]:
                to_compiled_contracts.append(x)
                
    print(f"{len(to_compiled_contracts)} Files in the audit scope: ", to_compiled_contracts)
    #找到packatge.json文件路径
    package_json = find_top_level_package_json(args.project)
    package2version = {}
    if package_json:
        #找到项目依赖并简化版本号
        package2version = parse_package_json(package_json)
    else:
        package_json = init_package_json(args.project)
        package2version = parse_package_json(package_json)
    #dependency中存放solidity文件中import了但不存在的文件,exist_dependencies存放能找到的
    dependencies,exist_dependencies = find_solidity_imports(args.project)
    #print("package2version:",package2version)
    #print("env.dependency:",dependencies)
    # print("External Dependencies of the project:", dependencies)
    #package2version保留不存在的依赖项
    for k in list(package2version.keys()):
        for d in exist_dependencies:
            if k in d:
                package2version.pop(k,None)
    #将系统中不存在的依赖项写入package.json
    if package_json:
        update_package_json(package_json, package2version)

    #找到所有的solc version
    solc_versions = find_solc_versions(to_compiled_contracts)
    
    env = Environment(args, node_module_path,files,remappings,foundry_content,dependencies, solc_versions, Scopes, to_compile=to_compiled_contracts,test_info=test_info, packageJson=package2version,exist_dependencies=exist_dependencies)
    #如果已经编译过了，则调用cache
    #old_dir=get_all_folders(env.dir)
    base_name=[os.path.split(x)[1][:-4] for x in env.toAnalyze]
    if len(has_compiled(args.project,base_name)) > 0:
        print(f"Already successfully compiled {len(has_compiled(args.project,base_name))//3} files, skip compiling {args.project}")
        setupInfo, success = load_setup_info(args.setup_cache, args.project), True
    else: 
        setupInfo, success = setup.setUp(args, env=env)
        if len(has_compiled(args.project,base_name)) > 0:
            setupInfo.set_compiled_contracts(has_compiled(args.project,base_name))
            print(f"Successfully compiled {len(has_compiled(args.project,base_name))//3} files, {setupInfo.get_setup_info()}")
        else:
            print(f'Compilation Fails')
    # new_dirs=get_all_folders(env.dir)
    # new_added_dirs = list(set(new_dirs)-set(old_dir))
    # if len(new_added_dirs)>1:
    #     new_added_dirs=[x for x in new_added_dirs if not os.path.split(x)[1]=='build']
    
    #env.buildPath=new_added_dirs[0]
    if success:
    
        #setupInfo.set_compiled_contracts(has_compiled(args.project))
        store_setup_info(args.setup_cache, args.project, setupInfo)
    success = analyzer.analyze(args, env, setupInfo,success)
    print(f'''Ask Token:{env.askToken}\nAnwser Token:{env.anwserToken}''')
    return


if __name__ == "__main__":
    auditProject()
    
    

