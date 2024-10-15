#!/bin/bash

# 获取项目根目录（即脚本所在目录）
PROJECT_ROOT=$(pwd)

# 打印项目根目录
echo "Project root directory: $PROJECT_ROOT"

# 查找所有的 .git 文件夹，排除根目录下的 .git 文件夹
find . -type d -name ".git" | while read gitdir; do
    # 检查 .git 文件夹是否位于项目根目录
    if [[ "$gitdir" != "./.git" ]]; then
        echo "Removing $gitdir"
        rm -rf "$gitdir"
    else
        echo "Skipping project root .git folder: $gitdir"
    fi
done

echo "Cleanup complete."
