from watchdog.observers import Observer
from watchdog.events import *
import time
from git import Repo
import os
import subprocess
import shutil
import sched



# Find the directory of the running script
script_dir = os.path.dirname(os.path.realpath(__file__))

dirfile = os.path.join(script_dir, 'monitor')

# Check if the directory exists, if not create it
if not os.path.exists(dirfile):
    os.makedirs(dirfile)

# Command init 
# git init      
# git config --global user.name "upload"   
# git config --global user.email "your.email@example.com"    
# git remote add lgGuide https://github.com/cliff1o/lgGuide.git
def is_git_repository(directory):
    try:
        # 尝试在指定目录下运行 git status 命令
        subprocess.check_output(['git', '-C', directory, 'status'])
        # 如果命令成功，那么这是一个 Git 仓库
        return True
    except subprocess.CalledProcessError:
        # 如果命令失败，那么这不是一个 Git 仓库
        return False
def pushgit(ccpath):

    # 检查目录是否为空或只包含 .git 目录
    if not os.listdir(dirfile) or set(os.listdir(dirfile)) == {'.git'}:
        print("Directory is empty, nothing to commit.")
        return

    # 检查 .git/index.lock 文件是否存在。如果存在，等待一段时间，然后再尝试提交
    if os.path.exists(os.path.join(dirfile, '.git', 'index.lock')):
        print("Git is busy, waiting...")
        time.sleep(10)

    try:
        subprocess.check_output(['git', '-C', dirfile, 'add', '--all'])
        try:
            subprocess.check_output(['git', '-C', dirfile, 'commit', '-m', 'auto update'])
        except subprocess.CalledProcessError:
            # 如果 commit 失败（可能是因为没有任何改变），尝试设置上游分支并再次 push
            subprocess.check_output(['git', '-C', dirfile, 'push', '--set-upstream', 'lgGuide', 'master'])
        print("Successful push!")
    except subprocess.CalledProcessError as e:
        print("Error during push: " + str(e.output))
        

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if ".git" not in event.src_path:
            pushgit(event.src_path)
            if event.is_directory:
                print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
            else:
                print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        if ".git" not in event.src_path:
            pushgit(event.src_path)
            if event.is_directory:
                print("directory created:{0}".format(event.src_path))
            else:
                print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if ".git" not in event.src_path:
            pushgit(event.src_path)
            if event.is_directory:
                print("directory deleted:{0}".format(event.src_path))
            else:
                print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if ".git" not in event.src_path:
            pushgit(event.src_path)
            if event.is_directory:
                print("directory modified:{0}".format(event.src_path))
            else:
                print("file modified:{0}".format(event.src_path))          
# 源文件夹和目标文件夹
src_folders = ['E:\\cs16_boss\\Half-Life\\cstrike\\addons\\amxmodx\\logs']


# 创建一个调度器对象
s = sched.scheduler(time.time, time.sleep)

def copy_files(sc):
    for src_folder in src_folders:
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            target_file = os.path.join(dirfile, filename)

            # 检查文件的修改时间，如果文件的修改时间大于一天，就跳过
            if os.path.exists(target_file) and time.time() - os.path.getmtime(src_file) > 24*60*60:
                continue

            # 复制文件
            shutil.copy2(src_file, target_file)

    # 调度下一次复制操作，30分钟后
    s.enter(30*60, 1, copy_files, (sc,))



if __name__ == "__main__":
    # 调用函数，初始化 Git

    if not os.path.isdir(os.path.join(script_dir, 'monitor/.git')):
        # 如果不存在，运行 git init 命令
        subprocess.run(['git', '-C', dirfile, 'init'])
        subprocess.run(['git', '-C', dirfile, 'remote', 'add', 'lgGuide', 'https://gitee.com/clifflo/publicitem.git'])
        subprocess.run(['git', '-C', dirfile, 'config', '--global', 'user.name', 'Pybot Upload'])
        subprocess.run(['git', '-C', dirfile, 'config', '--global', 'user.email', 'example@example.com'])
        subprocess.run(['git', '-C', dirfile, 'pull', 'lgGuide', 'master'])
               
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, dirfile,True)
    # 需要检测的文件目录
    observer.start()
    # 调度第一次复制操作，立即执行
    s.enter(0, 1, copy_files, (s,))
    s.run()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

