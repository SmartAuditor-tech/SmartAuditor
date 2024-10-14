import os, shutil, tempfile, requests
from Analyzer.Tools import ToolInfo
from Analyzer.AnalyzePrompt import *
from Prompt.Chat import chat_with_gpt_multi_round
from Prompt.Chat import num_tokens_from_string
from Execution import executor
from Docker.dockerSet import *
import re
from openai import OpenAI
import importlib,json
g4b_original=[]
original=[]
compiled=[]
directory=set()
def init_result_folder(project, tool_name):
    if 'result' not in os.listdir(project):
        os.mkdir(os.path.join(project, 'result'))
    if tool_name not in  os.listdir(os.path.join(project, 'result')):
        os.mkdir(os.path.join(project, 'result', tool_name))

    return
def get_subdirectories(dir):
    return [os.path.join(dir,f) for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))]
def get_file(command:str):
    for x in command.split():
        if x.endswith((".sol",".abi",".bin",".bin-runtime")):
            return x
def move_compile_result(env,setupInfo):
    g4bdir=tempfile.mkdtemp()
    g4bdir_build=os.path.join(g4bdir,"build")
    g4bdir_contracts=os.path.join(g4bdir,"contracts")
    # if not os.path.exists(g4bdir_build):
    #     os.makedirs(g4bdir_build)
    # if not os.path.exists(g4bdir_contracts):
    #     os.makedirs(g4bdir_contracts)
    # shutil.copytree(env.dir+"./build",g4bdir_build)

    if os.path.exists(g4bdir):
        shutil.rmtree(g4bdir)
    shutil.copytree(env.dir,g4bdir,symlinks=True)
    global directory
    directory=set(get_subdirectories(g4bdir))
    for file in env.toAnalyze:
        # shutil.copy(file,g4bdir_contracts)
        # original.append("/g4b/contracts/"+os.path.split(file)[1])
        original.append(file)
        g4b_original.append(file.replace(env.dir,"/g4b/"))

    for file in setupInfo.compiled_contracts:
        compiled.append(os.path.split(file)[1])

    return g4bdir

def remove_code_block_markers(text):
    pattern = r'```.*?\n(.*?)\n```'
    cleaned_text = re.sub(pattern, r'\1', text, flags=re.DOTALL)
    pattern = r"^`(.*?)`$"
    cleaned_text = re.sub(pattern, r'\1', cleaned_text)
    return cleaned_text

def exists_json(g4bdir,filename):
    if os.path.exists(os.path.join(g4bdir,filename)):
        return True
    return False
def move_json(g4bdir,commands,project,tool_name):
    file=os.path.split(get_file(commands))[1]
    file_name=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
    file_name+=".json"
    file_path=os.path.join(project,'result',tool_name,file_name)
    source_json=os.path.join(g4bdir,"results.json")
    print(f"move {source_json} to {file_path}")
    shutil.move(os.path.join(g4bdir,"results.json"),file_path)
def move_json_env(commands,project,tool_name):
    file=os.path.split(get_file(commands))[1]
    file_name=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
    file_name+=".json"
    file_path=os.path.join(project,'result',tool_name,file_name)
    source_json=os.path.join(project,"output.json")
    print(f"move {source_json} to {file_path}")
    shutil.move(os.path.join(project,"output.json"),file_path)
    return file_path

def load_parser(tool_name):
    parser_path = os.path.join("./Tools", tool_name, "parser.py")
    # 检查文件是否存在
    if not os.path.exists(parser_path):
        raise FileNotFoundError(f"No parser found for tool: {tool_name}")
    
    # 导入指定路径的模块
    spec = importlib.util.spec_from_file_location(f"{tool_name}_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # 假设每个 parser.py 都有一个名为 parse 的函数
    return module.parse

def parse_json(file_path,tool_name):
    parser_function=load_parser(tool_name)
    success,findings=parser_function(file_path)
    if isinstance(findings,dict):
        data_to_write={
            'success':success,
            'findings':findings
        }
    else:
        data_to_write={
        'success':success,
        'finding_length':len(findings),
        'findings':findings
    }
    try:
        with open(file_path, 'w') as file:
            json.dump(data_to_write, file,indent=4)
    except Exception as e:
        print(f"write parsed json faile as: {e}")
def parse_txt(file_path,tool_name):
    parser_function=load_parser(tool_name)
    success,findings=parser_function(file_path)
    if isinstance(findings,dict):
        data_to_write={
            'success':success,
            'findings':findings
        }
    else:
        data_to_write={
        'success':success,
        'finding_length':len(findings),
        'findings':findings
    }
    file_path=file_path.replace(".txt",".json")
    try:
        with open(file_path, 'w') as file:
            json.dump(data_to_write, file,indent=4)
    except Exception as e:
        print(f"write parsed json faile as: {e}")
def write_logs(command,project,tool_name,logs):
    file=os.path.split(get_file(command))[1]
    print(f"{file} completed analyzing!")
    file_name=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
    file_name+=".txt"
    file_path=os.path.join(project,'result',tool_name,file_name)
    with open(file_path,'w',encoding='utf-8') as f:
        for log in logs:
            f.write(log+"\n")
    return file_path
def write_result(command,project,tool_name,result):
    file=os.path.split(get_file(command))[1]
    print(f"{file} completed analyzing!")
    file_name=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
    file_name+=".txt"
    file_path=os.path.join(project,'result',tool_name,file_name)
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(result)
    return file_path
def change_name_manticore(g4bdir,filename):
    new_dirs=set(get_subdirectories(g4bdir))-directory
    print("directory:"+str(directory))
    print("new_dirs:"+str(new_dirs))
    if new_dirs:
        new_dir=new_dirs.pop()
        os.rename(os.path.join(g4bdir,new_dir),os.path.join(g4bdir,filename))
def move_manticore(env,g4bdir,filename):
    change_name_manticore(g4bdir,filename)
    if os.path.exists(os.path.join(env.dir,"result/manticore_contracts/",filename)):
        shutil.rmtree(os.path.join(env.dir,"result/manticore_contracts/",filename))
    shutil.copytree(os.path.join(g4bdir,filename),os.path.join(env.dir,"result/manticore_contracts/",filename))
    global directory
    directory=set(get_subdirectories(g4bdir))
def analyze(args, env, setupInfo,success_build):
    try:
        g4bdir=move_compile_result(env,setupInfo)
        for tool in ToolInfo:
            if (not success_build) and (not tool['type']=='contracts'):
                continue
            if tool['docker']=='No':
                contracts=original[:]
                build=compiled[:]
            else:
                contracts=g4b_original[:]
                build=compiled[:]
                if not is_loaded(tool['image']):
                    print(f"Loading docker image {tool['image']}...")
                    load(tool['image'])
            init_result_folder(env.dir, tool['name']+"_"+tool['type'])
            prompt = getAnalyzeTaskPrompt(args, env,contracts,compiled,tool, setupInfo) if tool['docker']=='No' else getAnalyzeTaskPromptForDocker(args, contracts,compiled,tool, setupInfo)
           
            messages = []
            env.askToken+=num_tokens_from_string(prompt)
            success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
            env.anwserToken+=num_tokens_from_string(result)
            result = remove_code_block_markers(result)
            commands = result.split('\n')[0]

            #cwd = result.split('\n')[1]
            print(f"GPT Command: {commands}")
            if tool['docker']=='No':
                result, err = executor.executeCommands(commands=commands,cwd=env.dir)
                if exists_json(env.dir,"output.json"):
                    new_file_path=move_json_env(commands,env.dir,tool['name']+"_"+tool['type'])
                    parse_json(new_file_path,tool['name'])
                
                elif not tool['name']=="slither":
                    new_file_path=write_result(commands,env.dir,tool['name']+"_"+tool['type'],result+err)
                    parse_txt(new_file_path,tool['name'])
            else:
                exit_code,logs,container=execute(args,env,tool['image'],commands,g4bdir)
                print(logs)
                if tool['name']=='manticore':
                        file=os.path.split(get_file(commands)[:-4])[1]
                        move_manticore(env,g4bdir,file)
                else:
                    if exists_json(g4bdir,"result.json"):
                        move_json(g4bdir,commands,env.dir,tool['name']+"_"+tool['type'])
                    #写入结果
                    else:
                        new_file_path=write_logs(commands,env.dir,tool['name']+"_"+tool['type'],logs)
                        parse_txt(new_file_path,tool['name'])
            #只获取分析的文件名
            file=os.path.split(get_file(commands))[1]

            if file.endswith(".sol"):
                contracts=[x for x in contracts if file not in x]
            else:
                #移除编译文件里基础名的所有文件(.abi .bin .bin-runtime)
                file=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
                build=[x for x in build if file not in x]
            #result, err = executor.executeCommands(commands=commands,cwd=cwd)

            while True:
                #prompt = updateAnalyzeCommand(command=commands,result=result,err=err)
                #!!!!startswith!
                prompt=updateAnalyzeCommand(tool,commands,result,err) if tool['docker']=='No' else updateAnalyzeCommandForDocker(tool,commands,logs)
                env.askToken+=num_tokens_from_string(prompt)
                success, result, messages = chat_with_gpt_multi_round(prompt, messages=messages)
                env.anwserToken+=num_tokens_from_string(result)
                result = remove_code_block_markers(result)
                print(f"GPT Command: {result}")
                if result.split('\n')[0]=="No":
                    break
                commands = result.split('\n')[0]
                
                #cwd = result.split('\n')[1]
                #result, err = executor.executeCommands(commands=commands,cwd=cwd)
                if tool['docker']=='No':
                    result, err = executor.executeCommands(commands=commands,cwd=env.dir)
                    if exists_json(env.dir,"output.json"):
                        new_file_path=move_json_env(commands,env.dir,tool['name']+"_"+tool['type'])
                        parse_json(new_file_path,tool['name'])
                    elif tool['name']=='slither':
                        continue
                    else:
                        new_file_path=write_result(commands,env.dir,tool['name']+"_"+tool['type'],result+err)
                        parse_txt(new_file_path,tool['name'])
                else:
                    exit_code,logs,container=execute(args,env,tool['image'],commands,g4bdir)
                    if tool['name']=='manticore':
                        file=os.path.split(get_file(commands)[:-4])[1]
                        move_manticore(env,g4bdir,file)
                    else:
                        if exists_json(g4bdir,"result.json"):
                            new_file_path=move_json(commands,env.dir,tool['name']+"_"+tool['type'])
                            
                        #写入结果
                        else:
                            new_file_path=write_logs(commands,env.dir,tool['name']+"_"+tool['type'],logs)
                            parse_txt(new_file_path,tool['name'])
            while True:
                file=os.path.split(get_file(commands))[1]
                if file is None:
                    break
                if file.endswith(".sol"):
                    contracts=[x for x in contracts if file not in x]
                    if len(contracts)==0:
                        break
                    
                    commands=commands.replace(get_file(commands),contracts[0])
                else:
                    file=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
                    build=[x for x in build if file not in x]
                    if len(build)==0:
                        break
                    replace_file=build[0][:-12] if build[0].endswith(".bin-runtime") else build[0][:-4]
                    commands=commands.replace(file,replace_file)
                if success_build and (len(contracts)==0 or len(build))==0:
                    break
                if (not success_build) and len(contracts)==0:
                    break
                print(f"Command: {commands}")
                if tool['docker']=='No':
                    result, err = executor.executeCommands(commands=commands,cwd=env.dir)
                    if exists_json(env.dir,"output.json"):
                        new_file_path=move_json_env(commands,env.dir,tool['name']+"_"+tool['type'])
                        parse_json(new_file_path,tool['name'])
                    elif tool['name']=='slither':
                        continue
                    else:
                        new_file_path=write_result(commands,env.dir,tool['name']+"_"+tool['type'],result+err)
                        parse_txt(new_file_path,tool['name'])

                else:
                    exit_code,logs,container=execute(args,env,tool['image'],commands,g4bdir)
                    if tool['name']=='manticore':
                        file=os.path.split(get_file(commands)[:-4])[1]
                        move_manticore(env,g4bdir,file)
                    else:
                        if exists_json(g4bdir,"result.json"):
                            new_file_path=move_json(commands,env.dir,tool['name']+"_"+tool['type'])
                            
                        #写入结果
                        else:
                            new_file_path=write_logs(commands,env.dir,tool['name']+"_"+tool['type'],logs)
                            parse_txt(new_file_path,tool['name'])
                
    finally:
        shutil.rmtree(g4bdir)
    return True

