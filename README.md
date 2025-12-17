# 说明

项目是在 linux 下开发的，不知道 windows 下能不能跑通。下面所有内容都是在 linux 下完成的。

我没有添加任何镜像, 那样会导致很多乱七八糟的问题, 建议下载过程开梯子。

# 步骤

### 1. 安装nodejs 

- 可以直接用 `apt` 安装 ！

下面是手动安装的方法

- 在这里查看需要安装的版本: [可安装node版本查看](https://nodejs.org/dist/)

- 运行命令 `wget https://nodejs.org/dist/v18.20.3/node-v24.5.0-linux-x64.tar.xz`(我的版本是 v24.5.0)

- 进行解压 `tar -xvJf node-v24.5.0-linux-x64.tar.xz`

- 运行 `export NODE_HOME=~/node-v24.5.0-linux-x64` (这里 `NODE_HOME` 指向压缩包解压的位置)

- 运行 `export PATH=$NODE_HOME/bin:$PATH` 加入路径

- 运行 `node --version` 检查是否安装成功

- 可以将上述命令加入 `~/.bashrc` 中 (每次开启终端时会自动执行):
  ```bash
  sudo nano ~/.bashrc
  # 将下面两行加入文件中
  export NODE_HOME=~/node-v24.5.0-linux-x64
  export PATH=$NODE_HOME/bin:$PATH  
  ```
  
### 2. 安装 npm

- 可以直接用 apt 安装

### 3. 安装 pnpm

- `npm install pnpm -g`

### 4. 跑通前端

- 进入项目的 `/frontend` 目录下, 运行命令 `pnpm install` 或者 `pnpm -i`, 安装依赖

- 使用 `node app.js` 运行前端

### 5. 跑通后端

- 在**项目根目录**运行 `python3 -m venv .venv` 创建虚拟环境

- 使用 `source .venv/bin/activate` 激活虚拟环境, **进入后端目录**, 执行 `pip install -r requirements.txt` 下载 python 包, 再执行 `python3 main.py`
