import os
from os import walk
import re

def get_source_code_from_foler(folder,remappings:dict):
    results = []
    node_module_path=""
    def replace_import(match):
        import_path = match.group(2)  # 获取匹配到的路径部分
        matched_alias = None
    
        # 遍历 remappings 找到匹配的别名
        for alias in remappings:
            if import_path.startswith(alias):
                matched_alias = alias
                break
    
        # 如果找到了匹配的别名，替换为相对路径
        if matched_alias:
            r_folder = remappings[matched_alias]
            r_path = import_path[len(matched_alias):]  # 移除别名部分
            abs_path = os.path.join(folder,r_folder, r_path)
            rel_path = os.path.relpath(abs_path, dirpath)

            return f'import {match.group(1) or ""}"{rel_path}";'
    
        return match.group(0)  # 如果没有找到匹配的别名，就返回原始的 import 语句
    for (dirpath, dirnames, filenames) in walk(folder):
        #print(dirnames)
        
        if 'test' in dirnames:
            dirnames.remove('test')
        if 'node_modules' in dirnames:
            node_module_path=os.path.join(dirpath,"node_modules")
            
            dirnames.remove('node_modules')

        for f in filenames:
            
            if not f.lower().endswith('.sol'):
                continue
           
            path = os.path.join(dirpath,f)
            content = ''
            with open(path, 'r') as fr:
                content = fr.read()
            content = re.sub(r'import(\s+\{[^}]+\}\s+from\s+)?\s*["\']([^"\']+)["\'];', replace_import, content)
    
            #重写remappings
            # if remappings is not None:
            #     for alias,r_path in remappings.items():
            #         abs_path=os.path.join(folder,r_path)
            #         rel_path=os.path.relpath(abs_path,dirpath)
            #         pattern=re.compile(rf'import\s+["\']{alias}(.+?)["\'];')
            #         replacement = rf'import "{rel_path}\1";'
            #         content = pattern.sub(replacement, content)
            with open(path,'w') as file:
                file.write(content)

            #文件路径、每个文件的文件名、文件代码
            #result包含所有文件
            results.append({'dirpath': dirpath,'path': path, 'filename':f})
    return results,node_module_path
