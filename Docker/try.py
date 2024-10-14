import tempfile,shutil,docker,os,requests
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
    image_loaded.add(e)

def create_volume():
    g4bdir=tempfile.mkdtemp()

    return g4bdir
def set_args(image,g4bdir):
    args={
        "image":image,
        "detach":True,
        "volumes":{g4bdir:{"bind":"/g4b","mode":"rw"}},
    }
    shutil.rmtree(g4bdir)
    return args


image="mythril/myth"
if not is_loaded(image):
    load(image)
args=set_args(image,create_volume())
container=client().containers.run(**args)
