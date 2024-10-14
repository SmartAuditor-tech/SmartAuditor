import os
import re
from SetUp import setupPrompt
from Execution import executor
from Prompt.Chat import chat_with_gpt_multi_round
from Prompt.Chat import num_tokens_from_string
from collections import defaultdict

import json


class SetupInfo:
    
    def __init__(self, solc_command = None, compiled_contracts = None, dependencies = None):

        
        self.solc_command=[]
        self.solc_command.append(solc_command)
        self.compiled_contracts = compiled_contracts
        self.dependencies = dependencies
    def add_solc_command(self, solc_command):
        self.solc_command.append(solc_command)
    def set_compiled_contracts(self, compiled_contracts):
        self.compiled_contracts = compiled_contracts
    def set_dependencies(self, dependencies):
        self.dependencies = dependencies
    def get_setup_info(self):
        return f'''Solc command to compile the contracts: {self.solc_command},
Compiled contracts: {self.compiled_contracts},
Dependencies of the contracts: {self.dependencies},
'''
    
def modify_dependency_list(key,env):
    if not key.endswith(".sol"):
        key+=".sol"
    env.dependencies=[x for x in env.dependencies if not x.endswith(key)]
def get_compiled_contract(command):
    parts=command.split()
    for sol in parts:
        if sol.endswith(".sol"):
            return sol
    return "None"
def modify_compile_list(sol,err,setupinfo,env):
    print("Removed contract:"+sol)
    env.toCompile=[x for x in env.toCompile if x!=sol]
def get_all_folders(dir_path):
    # 获取目录下所有文件和文件夹
    all_items = os.listdir(dir_path)
    
    # 过滤出文件夹
    folders = [item for item in all_items if os.path.isdir(os.path.join(dir_path, item))]
    return folders

def extract_content_with_optional_markdown(text):
    # 正则表达式匹配包含 ``` 的行及其末尾的换行符
    pattern = r"^.*```.*\n?"
    
    cleaned_text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return cleaned_text
def init_build_folder(project):
    #创建build文件夹
    if 'build' not in os.listdir(project):
        os.mkdir(os.path.join(project, 'build'))
    return
           
def setUp(args, env):
    init_build_folder(args.project)
    prompt=setupPrompt.get_framework(env,args)
    env.askToken+=num_tokens_from_string(prompt)
    messages=[]
    success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
    env.anwserToken+=num_tokens_from_string(result)
    result=extract_content_with_optional_markdown(result)
    print("framework"+result)
    if not result=="No":
        env.framework=result

    prompt = setupPrompt.get_setup_session_init_prompt(env, args)
    env.askToken+=num_tokens_from_string(prompt)
    success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
    env.anwserToken+=num_tokens_from_string(result)
    #print("result before re:"+result)
    result=extract_content_with_optional_markdown(result)
    #print("result after re:"+result)
    commands = result.split('\n')[0]
    cwd = result.split('\n')[1]
    result, err = executor.executeCommands(commands=commands,cwd=cwd)
    setupinfo = SetupInfo()
    

    while True:
        if len(err) > 5000:
            err = err[:5000]
        prompt = setupPrompt.updateSetupCommand(command=commands, result=result, err = err)
        env.askToken+=num_tokens_from_string(prompt)
        success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
        env.anwserToken+=num_tokens_from_string(result)
        result=extract_content_with_optional_markdown(result)

        commands = result.split('\n')[0]
        if commands == "No":
            break
        cwd = result.split('\n')[1]
        result,err = executor.executeCommands(commands=commands,cwd=cwd)
    #这里需要更改一下，在初始化命令信息的时候提示gpt先统计用到的依赖都附属于哪些库，再用npm或者brew下载所需依赖，在下载好以后再重定位这些依赖的绝对地址
    while len(env.dependencies)>0:
        prompt = setupPrompt.get_dependency_absolute_path(env)
        env.askToken+=num_tokens_from_string(prompt)
        success, dep2path, messages = chat_with_gpt_multi_round(prompt, messages=messages)
        env.anwserToken+=num_tokens_from_string(dep2path)
        dep2path=extract_content_with_optional_markdown(dep2path)
        if dep2path !="No":
            try:
                dep2path = json.loads(dep2path)
                for k in dep2path.keys():
                    modify_dependency_list(k,env)
            except:
                print("The return value is not properly formatted", dep2path)
                break
            print("Dependency Paths:", dep2path)
            #改变合约中依赖的地址
            resolve_dependencies(env.scopes, dep2path,env.files)
            setupinfo.set_dependencies(dep2path)
        else:
            print("Resolving task finished")
            break





    #执行编译合约任务
    prompt = setupPrompt.get_compile_task(env=env, args=args,)
    env.askToken+=num_tokens_from_string(prompt)
    success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
    env.anwserToken+=num_tokens_from_string(result)
    result=extract_content_with_optional_markdown(result)
    print(result)
    command_cwd=result.split('\n')
    if len(command_cwd)>2 and command_cwd[2].strip()=="":
        r=3
    else:
        r=2
    setupinfo.add_solc_command(command_cwd[0] + '\n' + command_cwd[1])
    for i in range(0,len(command_cwd),r):
        
        if i+1<len(command_cwd):
            commands,cwd=command_cwd[i],command_cwd[i+1]
        else: 
            break 
        result, err = executor.executeCommands(commands=commands,cwd=cwd)
        sol=get_compiled_contract(commands)
        if not sol=="None":
            modify_compile_list(sol,err,setupinfo,env)

    print(f"{len(env.toCompile)} contracts left")


    while True:
        #setupinfo.add_solc_command(commands + '\n' + cwd)
        prompt = setupPrompt.keepOnCompileCommand(env,command=commands, result=result, err = err)
        env.askToken+=num_tokens_from_string(prompt)
        success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
        env.anwserToken+=num_tokens_from_string(result)
        result=extract_content_with_optional_markdown(result)
        print(result)
        command_cwd=result.split('\n')
        if len(command_cwd)>2 and command_cwd[2].strip()=="":
            r=3
        else:
            r=2
        for i in range(0,len(command_cwd),r):
            #setupinfo.add_solc_command(commands + '\n' + cwd)
            if i+1<len(command_cwd):
                commands,cwd=command_cwd[i],command_cwd[i+1]
                if not os.path.exists(cwd):
                    commands="Error"
                    break
            else:
                commands="Error"
                break
            sol=get_compiled_contract(commands)
            if sol in env.toCompile:
                result, err = executor.executeCommands(commands=commands,cwd=cwd)
            
            if not sol=="None":
                modify_compile_list(sol,err,setupinfo,env)
        print(f"{len(env.toCompile)} contracts left")
        if commands== "Error" or len(env.toCompile)==0:
            break

    success = False
    base_name=[os.path.split(x)[1][:-4] for x in env.toAnalyze]
    setupinfo.compiled_contracts=has_compiled(args.project,base_name)
    

    if len(setupinfo.compiled_contracts)> 0:
        success = True
        
    else:
        success = False
        
    
    return setupinfo, success
    
def has_compiled(project,base_name):
    if 'build' in os.listdir(project) and len(os.listdir(os.path.join(project,'build')))>=1:
        return [x for x in os.listdir(os.path.join(project,'build')) if (x.endswith('.bin') or x.endswith('.bin-runtime') or x.endswith('.abi')) and x.split('.')[0] in base_name]
    else:
        return []

def resolve_dependencies(file_paths, dep2path,files):
    for file_path in file_paths:
        
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace import statements for external libraries starting with '@'
        def replace_import(match):
            dep = match.group(2)
            if dep.startswith('.'):  # Skip if the library is already a relative path
                return match.group()
            if os.path.exists(dep):
                return match.group()
            imported_file=os.path.split(dep)[1]
            for key in dep2path.keys():
                relative_path=" "
                file_name=os.path.split(dep2path[key])[1]
                if imported_file==file_name or imported_file.startswith(key):
                    if not os.path.exists(dep2path[key]):
                        print(file_name+"'s path is wrong")
                        for x in files:
                            if x['filename']==file_name:
                                print("real path:"+x['path'])
                                relative_path = os.path.relpath(x['path'], os.path.dirname(file_path))
                                break
                        if relative_path==" ":
                            relative_path = os.path.relpath(dep2path[key], os.path.dirname(file_path))
                                
                    else:
                        # Calculate the relative path from the current file to the dependency
                        relative_path = os.path.relpath(dep2path[key], os.path.dirname(file_path))
                    # Replace the dependency in the import statement with the relative path
                    print(file_path)
                    print( f'resolving import from {match.group()} to {match.group().replace(dep,relative_path)} ')

                    return f'import {match.group(1) or ""}"{relative_path}";'
            return match.group()

        # Modify the regular expression to match both styles of import statements
        content = re.sub(r'import(\s+\{[^}]+\}\s+from\s+)?\s*["\']([^"\']+)["\'];', replace_import, content)

        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(content)

    return
    

def parse_imports(file_content):
    imports = re.findall(r'import\s+["\'](.+?)["\']', file_content)
    return imports

def analyze_dependencies(file_paths):
    dependencies = defaultdict(set)  # key为合约绝对地址，value为依赖该合约的合约绝对地址集合

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_content = f.read()
            imported_contracts = parse_imports(file_content)
            for imp_contract in imported_contracts:
                dependencies[imp_contract].add(file_path)

    # 找到入度为0的合约（即没有被任何合约import的合约）
    independent_contracts = [contract for contract in file_paths if contract not in dependencies]

    return independent_contracts