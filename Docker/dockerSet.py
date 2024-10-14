import docker, os, shutil, tempfile, requests
from string import Template
#from Tools.tools import ToolsScope
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


def set_args(image,command,g4bdir):
    args={
        "image":image,
        "detach":True,
        "volumes":{g4bdir:{"bind":"/g4b","mode":"rw"}},
    }
    args["command"]=command
    return args
def execute(env_args,env,image,command,g4bdir):
    
    args=set_args(image,command,g4bdir)
    exit_code,logs,container = None,[],None
    try:
        container=client().containers.run(**args)
        try:
            result=container.wait(timeout=env_args.timeout)
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
        except Exception:
            pass
        try:
            if container is not None:
                container.remove()
        except Exception:
            pass
        

    return exit_code, logs,args


    
