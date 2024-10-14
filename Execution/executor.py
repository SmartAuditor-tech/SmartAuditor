import subprocess
RED = "\033[31m"  # 红色
GREEN = "\033[32m" # 绿色
YELLOW = "\033[33m" # 黄色
RESET = "\033[0m"  # 重置颜色
def executeCommands(commands, cwd):
    

    print(YELLOW + f"command: {commands}, cwd: {cwd}" + RESET)
    executionResult = subprocess.run(commands, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
    if "Error" in executionResult.stderr or "error" in executionResult.stderr:
        print(GREEN + f"output: {executionResult.stdout}" + RESET, RED + F"err: {executionResult.stderr}" + RESET)
    else:
        print(GREEN + f"output: {executionResult.stdout}" + RESET, GREEN + F"err: {executionResult.stderr}" + RESET)
    return executionResult.stdout, executionResult.stderr

def printlog(logs):
    if "Error" in logs or "error" in logs:
        print(GREEN + f"output: {logs}" + RESET, RED + F"err: {logs}" + RESET)
    else:
        print(GREEN + f"output: {logs}" + RESET, GREEN + F"err: {logs}" + RESET)