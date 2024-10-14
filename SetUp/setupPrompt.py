import os
def get_contracts(env):
    print("Compiled contracts:")
    print(env.toCompile[:10])

    return env.toCompile[:10]
def get_framework(env,args):
    developer_instructions = "And the Readme file shows that the project can be set up using the following instructions: " + env.test_info + '.\n'  if env.test_info else ''
    return f'''
    The enviroment description is as follows:
    {env.getEnvironmentDescription()}
    what framework is used in this project? If there is a framework used, just answer the name of used framework, in a single line, do not be verbose. If not, anwser "No".
'''
def get_setup_session_init_prompt(env, args):
    library_dependencies_info = "The library versions requrired by the project in the package.json are: " + str(env.packageJson) + '.\n' if env.packageJson else "There is no value for the 'dependency' key in the package.json.\n "
    library_dependencies_info+="The content of foundry.toml in this project is: "+str(env.foundry_content) if env.foundry_content else ''
    developer_instructions = "And here are the setup instructions from project: " + env.test_info + '.\n'  if env.test_info else ''

    if developer_instructions == '':
        setup_session_init = f'''
    I need assistance in configuring the environment for a Solidity smart contract project. The task involves two steps:
    1. Setting the correct version of the Solidity compiler (solc-select). 
    2. Installing specific dependent libraries locally, ensuring compatibility with the selected solc version. 
    
    {library_dependencies_info}
    If there are libraries need installing and the content of foundry.toml is not null, try to use foundry and npm/pnpm to install the libraries needed.
    The compiling and test tasks will be processed latter.
    You need to make sure the version of all installed libraries are compatitable with the selected solc version.
    Please guide me through the setup process, providing one command and the command's working directory at a time.
    You should directly offering the working path of a command instead of using "cd" command to get into the folder.
    After executing each command, I will provide the output from the terminal, and you can then give the next command to execute (optional).The enviroment description is as follows:
    {env.getEnvironmentDescription()}
    Do not be verbose. Only answer two lines: the first line should be the command to be executed, and the second line should only contain the working directory to execute the command.
    Just command and working directory, don't mark which part you've given. And you should pick {env.dir} for global command.
    Do not include any explanations or any warning! Do not use any Markdown format.
        '''
    else:
        setup_session_init = f'''
    I need assistance in configuring the environment for a Solidity smart contract project. 
    {developer_instructions}
    For now, the task only involves two steps:
    1. Setting the correct version of the Solidity compiler (solc-select). 
    2. Installing specific dependent libraries locally, ensuring compatibility with the selected solc version.
    The compiling and test tasks will be processed latter.
    Please guide me through the setup process, just providing one command and the command's working directory at a time.
    You should directly offering the working path of a command instead of using "cd" command to get into the folder.
    After executing each command, I will provide the output from the terminal, and you can then give the next command to execute (optional).The enviroment description is as follows:
    {env.getEnvironmentDescription()}
    Do not be verbose. Only answer two lines: the first line should be the command to be executed, and the second line should only contain the working directory to execute the command.
    Just command and working directory, don't mark which part you've given. And you should pick {env.dir} for global command.
    Do not include any explanations or any warning! Do not use any Markdown format.'''
    return setup_session_init
def downloadsolCommand(env,args):
    #if not err==b'' and (b'error' in err or b'Error' in err):
    setup_download=f'''
    These are the solidity contracts(libraries) which are not installed yet but imported by the solidity contracts in my local project(not a git repository):{env.dependencies}.
    According to the provided information, I need you to figure out which repositories(libraries) these imported contracts belong to, and helped me to download these contracts through npm/homebrew package managers or git clone command.
    Besides, in the provided steps above, the paths of the imported contracts should also be considered(better download to the "lib" directory).
    Please guide me through the download process, providing all the commands at once.
    Do not be verbose. For each commands you offering, it should be comprised of only two lines:the first line should be the command to be executed, and the second line should only contain the working directory to execute the command.
    Do not include any explanations or any warning! Do not use any Markdown formatting like \''' sh this kind of format!
    '''
    return setup_download
def updateSetupCommand(command, result, err):
    if not err=='' and ('err' in err or 'ERR' in err or 'Err' in err):
        return f'''I have executed the last command you suggested, which is {command}. However, this error occurs: {err}." You need to provide a solution to this error.
When responding, please provide only the command in the first line and the working directory to execute the command in the second line.
Do not explain your answer. If you have successfully fininshed all the tasks, answer "No".
'''
    else:
        return f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result}. 
What is the following command?
Do not be verbose. Only answer two lines. The first line is a pure string containing the command. The second line is the working directory to execute the command. Do not explain your answer. Do not use Markdown style.
If you have successfully fininshed all the tasks, answer "No".
'''

def updateCompileCommand(env,command, result, err):
    if not err=='':
        if len(err)> 4000:
            err=err[:4000]
        return f'''I have executed the last command you suggested, which is {command}. However, these errors occur: {err}."
Try to solve these errors and compile it one more time. If some of these erros cannot be solved, you can skip the contracts containing the error and compile the rest of the contracts. 
When responding, please provide only the command in the first line and the working directory to execute the command in the second line.
Do not explain your answer. Do not use Markdown style.
'''
    else:
        return f'''I have executed the last command you suggested, which is {command}. Here is the command line output: {result}. 
Help me to compile the rest of the contracts.
Do not be verbose. Only answer two lines. The first line is a pure string containing the command. The second line is the working directory to execute the command. 
Do not explain your answer. Do not use Markdown style.
'''
def keepOnCompileCommand(env,command,result,err):
    return f'''
    I have finished compiling the contracts via the commands offered, here are the output :{result}.{err}. Is there anything you can do to improve it?  And I need you to use the above compiler to compile the left contracts: {get_contracts(env)}. .
    Keep on using above compiler to compile these contracts. 
    If using solc to compile, store all result files in the {env.dir + '/build'}. Otherwise, if other framework is used to compile, store all result in its default directory. 
    Do not be verbose. Do not explain your answer. Do not use Markdown style. Make sure every command and working directory is complete, if the length of the last command is out of token limit, cut it off and do not give token limit warnings.
'''
def get_dependency_absolute_path(env):
    return f'''This project depends on the following installed contracts: {env.dependencies[:60]}.
And this is the tree structure in the folder where the project's dependencies are stored: {env.get_solidity_path_tree} 

In the provided steps above, what is the absolute path where these imported contracts were locally installed?
1.Note that I want to locate the contracts not the libraries they belong to. For example, if the import path of a given contracts is "solmate/tokens/ERC20.sol", what I want is the absolute path of this "ERC20.sol" but not the absolute path of the "solmate" library. 
2.Note that the imported contracts may not exist in the {env.dir} directory but its subordinate folders, you need to take into account where the absolute paths of the previously downloaded libraries are located. If a contract exits in "node_modules", the absolute path of "node_modules" is {env.node_module_path}, don't be confused with the project path {env.dir}.
3.Don't confuse the difference between contracts with similar names. For example, if an imported contract is named "A_ERC20_B" and another imported contract is named "ERC20", you need to find the absolute paths of both contracts but not just "ERC20"'s path. 
Please reply with a python dict dumpted as json, where the key is the name of the imported contracts and the value is the absolute path where this imported contract is installed on the local machine.
Your answer should try to include as much as installed contracts: {env.dependencies[:80]} within the token limit.
Make sure every key-value pair is complete in the dict, if the length of the last key-value pair is out of token limit, just cut it off and do not give token limit warnings.
If the imported contract is not installed, answer "No".
Avoid using Markdown format and return a plain string containing the dict.
'''


def get_compile_task(env, args):
    test_info="Here are the instructions for setup and compilation "+ env.test_info + ", and the framework of this project is "+env.framework+ ", if there is any assistance for compiling, I need you to use it to compile this project.\n"  if env.test_info else ''
    return f'''{test_info} Otherwise, if there is no assistance for compiling, you should use solc to compile the following contracts: {get_contracts(env)}. 
    When using solc, obtain the contracts's abi (.abi), runtime bytecode (.bin-runtime), and create bytecode (.bin). And make the allow-path of 'solc' to be {env.dir}. And use "--overwrite" argument in case that different solidity files using the same lib.
    I need you to reply me with as much as lines within the GPT token limit, where every two lines, the first line is a pure string containing the solc command to compile a single contract in the list, the second line is the working directory to execute the command.
    And I will ask you for the left contracts compiling tasks later.
    Store all result files in the {env.dir + '/build'}. 
Do not be verbose. Do not explain your answer. Do not use Markdown style.  Make sure every command and working directory is complete, if the length of the last command is out of token limit, cut it off and do not give token limit warnings. 
'''