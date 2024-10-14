import os,shutil,tempfile,docker,requests

_client=None
def client():
    global _client
    if not _client:
        try:
            _client=docker.from_env()
            _client.info()
        except Exception as e:
            print("set docker fail:"+e)
    return _client
image_loaded=set()

def is_loaded(image):
    if image in image_loaded:
        return True
    try:
        image_list=client().images.list(image)
    except Exception as e:
        print(f"Docker: checking for image {image} failed.\n{e}")
    if image_list:
        image_loaded.add(image)
        return True
    return False

def load(image):
    try:
        client().images.pull(image)
    except Exception as e:
        print(f"Docker:Loading image {image} failed.\n{e}")
    image_loaded.add(image)
def execute(image,args):
    exit_code,logs,container = None,[],None
    if not is_loaded(image):
        print(f"Loading docker image {image}...")
        load(image)
    try:
        container=client().containers.run(**args)
        try:
            result=container.wait(timeout=600)
            exit_code=result["StatusCode"]
        except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
            try:
                if container.status=='running':
                    container.stop(timeout=10)
            except docker.errors.APIError:
                pass
        logs=container.logs().decode("utf8").splitlines()

    except Exception as e:
        print(f"Running docker problem:{e}")
        if container is None:
            try:
                all_containers=client().containers.list(all=True)
                recent_container=sorted(all_containers,key=lambda x:x.attrs['Created'],reverse=True)[0]
                if recent_container.status=='running':
                    recent_container.kill()
                recent_container.remove()
            except Exception as e:
                print(f"removing exception container {e}")
    finally:
        try:
            if container is not None and container.status=='running':
                container.kill()
                print(f"kill container")
        except Exception as e:
            print(f"kill wrong {e}")
        try:
            if container is not None:
                container.remove()
                print(f"remove container")
        except Exception as e:
            print(f"remove wrong {e}")
        

    return exit_code, logs,args
project="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-03-taiko/"
g4bdir=tempfile.mkdtemp()

g4bdir_contracts=os.path.join(g4bdir,"contracts")
g4bdir_build=os.path.join(g4bdir,"build")
if not os.path.exists(g4bdir_contracts):
    os.makedirs(g4bdir_contracts)
if not os.path.exists(g4bdir_build):
    os.makedirs(g4bdir_build)
#exam_contract="/Users/tanzezhong/Desktop/tzz/Research/smartbugs/samples/BecToken.sol"
#exam="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-03-taiko/"
exam_contract="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-01-curves/contracts/Curves.sol"
exam_abi="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-03-taiko/build/TaikoErrors.abi"
exam_bin="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-03-taiko/build/TaikoErrors.bin"
exam_run="/Users/tanzezhong/Desktop/tzz/Research/GPT4Bugs-main/Examples/2024-03-taiko/build/TaikoErrors.bin-runtime"
def write_logs(logs):
    file_path='/Users/tanzezhong/Desktop/logs.txt'
    with open(file_path,'w',encoding='utf-8') as f:
        for log in logs:
            f.write(log+"\n")
# if os.path.exists(g4bdir):
#         shutil.rmtree(g4bdir)
#shutil.copytree(exam,g4bdir)
shutil.copy(exam_contract,g4bdir_contracts)
# shutil.copy(exam_abi,g4bdir_build)
# shutil.copy(exam_bin,g4bdir_build)
# shutil.copy(exam_run,g4bdir_build)
shutil.move(g4bdir,"/Users/tanzezhong/Desktop/")
# exam_contract="/g4b/contracts/"+os.path.split(exam_contract)[1]
# exam_abi="/g4b/build/"+os.path.split(exam_abi)[1]
# exam_bin="/g4b/build/"+os.path.split(exam_bin)[1]
exam_run="/g4b/build/"+os.path.split(exam_run)[1]
args1={
        "image":"chainsecurity/securify",
        "detach":True,
        "volumes":{g4bdir:{"bind":"/g4b","mode":"rw"}},
    }
args1["command"]=""
#args1["command"]=" help"
args2={
        "image":"troublor/securify2:latest",
        "detach":True,
        "volumes":{g4bdir:{"bind":"/g4b","mode":"rw"}},
    }
#args2["command"]="-fs /g4b/contracts/BecToken.sol --output /g4b/results.json   "
args2["command"]=""
try:
    exit_code,logs,container=execute("chainsecurity/securify",args1)
    print(logs)
    # exit_code,logs,container=execute("smartbugs/securify:usolc",args2)
    # print(logs)
    write_logs(logs)
    # shutil.copy(os.path.join(g4bdir,"live.json"),"/Users/tanzezhong/Desktop")
    # shutil.copy(os.path.join(g4bdir,"results.json"),"/Users/tanzezhong/Desktop")
finally:
    #shutil.rmtree(g4bdir)
    pass