def get_file(command:str):
    for x in command.split():
        if x.endswith((".sol",".abi",".bin",".bin-runtime")):
            return x
def get_original(original):
    print(f"Analyzing contract: {original[0]}")
    return original[0]
def get_compiled(compiled):
    file=compiled[0]
    file=file=file[:-12] if file.endswith(".bin-runtime") else file[:-4]
    file_list=[f"{file}.bin",f"{file}.abi",f"{file}.bin-runtime"]
    return file_list
def getAnalyzeTaskPrompt(args, env,original,compiled, tool, setupInfo):
    #The external dependencies of these contracts are installed at: {setupInfo.dependencies}.
    #Store the analysis result in the folder: {env.dir + 'result/'+tool['name']}.
    if tool['type']=='contracts':
        prompt= f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
Some of these contracts have already been compiled to .abi .bin and .bin-runtime files by executing the command: {setupInfo.solc_command}, and the results are stored in the "{env.dir}/build" folder as :{compiled}.
You can use terminal command: {tool['command']} to access {tool['name']}, for example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.
'''
    else:
        prompt=f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
You may require bytecode and ABI information, some of these contracts have already been compiled to .abi .bin and .bin-runtime files by executing the command: {setupInfo.solc_command}, and the results are stored in the "{env.dir}/build" folder as :{compiled}.
You can use terminal command: {tool['command']} to access {tool['name']}, for example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract(or bytecode file) with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract(or bytecode file) according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.

'''
    return prompt

def getAnalyzeTaskPromptForDocker(args,original,compiled, tool, setupInfo):
    #The external dependencies of these contracts are installed at: {setupInfo.dependencies}.
    #Store the analysis result in the folder: {env.dir + 'result/'+tool['name']}.
    if tool['type']=="contracts":
        if tool['command']=='No':
            prompt=f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
No need to use "{tool['name']}" in the command to access {tool['name']}, because I have already set "{tool['name']}" in the start of the command, just give me the arguments. For example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.

'''
        else:
            prompt=f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
Some of these contracts have already been compiled to .abi .bin and .bin-runtime files by executing the command: {setupInfo.solc_command}, and the results are stored in the "/g4b/build" folder as :{compiled}.
You can use terminal command: {tool['command']} to access {tool['name']}, for example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.

'''
    else:
        if tool['command']=='No':
            prompt=f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
You may require bytecode and ABI information, some of these contracts have already been compiled to .abi .bin and .bin-runtime files by executing the command: {setupInfo.solc_command}, and the results are stored in the "/g4b/build" folder as :{compiled}.
No need to use "{tool['name']}" in the command to access {tool['name']}, because I have already set "{tool['name']}" in the start of the command, just give me the arguments. For example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract(or bytecode file) with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract(or bytecode file) according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.

'''
        else:
            prompt=f'''
Suppose you are an expert in smart contract security. You need to use the analysis tool '{tool['name']}' to analyze the following smart contracts: {original}.
You may require bytecode and ABI information, some of these contracts have already been compiled to .abi .bin and .bin-runtime files by executing the command: {setupInfo.solc_command}, and the results are stored in the "/g4b/build" folder as :{compiled}.
You can use terminal command: {tool['command']} to access {tool['name']}, for example, you can use the command "{tool['example']}" to analyze an example contract.
Just analyze one contract(or bytecode file) with the timeout to be {args.timeout} seconds, and I'll generate my own commands for the rest of the contract(or bytecode file) according to the command you gave me.

After executing this command, I will give you the result of the execution of '{tool['name']}'. You need to find out where the arguments in this command are misused and fix it.
To assist you in using the correct options, here is the usage of '{tool['name']}': {tool['usage']}
Do not be verbose. Only answer one line: the command to be executed, do not consider the working directory of the command.
Do not include any explanations. Do NOT use any Markdown formatting. No '' in command.

'''
    return prompt
def updateAnalyzeCommandForDocker(tool,command, result):
    if tool['type']=="contracts":
        prompt=f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result[:50]}. If the output shows the usage of {tool['name']}, it means there is mistake in the command offered.
Is there any misuse of the arguments of the command:{command}? If yes, try to fix it and give me another line of fixed command. 
If nothing wrong with the command:{command},answer "No".
Do not be verbose. Only answer one line: "No" or the command to be executed, do not consider the working directory of the command. No '' in command.
'''
    else:
        prompt=f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result[:50]}.  If the output shows the usage of {tool['name']}, it means there is mistake in the command offered.
Notice {tool['name']} may not support all kinds of .abi .bin .bin-runtime files. Is there any misuse of the arguments of the command:{command}? If yes, try to fix it and give me another line of fixed command. 
If nothing wrong with the command:{command},answer "No".
Do not be verbose. Only answer one line: "No" or the command to be executed, do not consider the working directory of the command. No '' in command.
'''
    return prompt
def updateAnalyzeCommand(tool,command, result, err):
    if tool['type']=="contracts":
        prompt=f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result[:50]+err[:500]}. If the output shows the usage of {tool['name']}, it means there is mistake in the command offered.
Is there any misuse of the arguments of the command:{command}? If yes, try to fix it and give me another line of fixed command. 
If nothing wrong with the command:{command},answer "No".
Do not be verbose. Only answer one line: "No" or the command to be executed, do not consider the working directory of the command. No '' in command.
'''
    else:
        prompt=f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result[:50]+err[:500]}.  If the output shows the usage of {tool['name']}, it means there is mistake in the command offered.
Notice {tool['name']} may not support all kinds of .abi .bin .bin-runtime files. Is there any misuse of the arguments of the command:{command}? If yes, try to fix it and give me another line of fixed command. 
If nothing wrong with the command:{command},answer "No".
Do not be verbose. Only answer one line: "No" or the command to be executed, do not consider the working directory of the command. No '' in command.
'''
    return prompt