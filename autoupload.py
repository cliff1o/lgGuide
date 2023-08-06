from watchdog.observers import Observer
from watchdog.events import *
import time
from git import Repo
import os
import subprocess

# Find the directory of the running script
script_dir = os.path.dirname(os.path.realpath(__file__))

dirfile = os.path.join(script_dir, 'monitor')

# Check if the directory exists, if not create it
if not os.path.exists(dirfile):
    os.makedirs(dirfile)

def pushgit(ccpath):
    # if(".git" in ccpath):
    #     print(1);
    # else:
        try:
            subprocess.check_output(['git', '-C', dirfile, 'add', '--all'])
            subprocess.check_output(['git', '-C', dirfile, 'commit', '-m', 'auto update'])
            try:
                output = subprocess.check_output(['git', '-C', dirfile, 'push'])
            except subprocess.CalledProcessError:
                # 如果 push 失败，尝试设置上游分支并再次 push
                subprocess.check_output(['git', '-C', dirfile, 'push', '--set-upstream', 'origin', 'master'])
            print("Successful push!")
        except subprocess.CalledProcessError as e:
            print("Error during push: " + str(e.output))
        

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        pushgit(event.src_path)
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        pushgit(event.src_path)
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        pushgit(event.src_path)
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        pushgit(event.src_path)
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))
    
          

if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, dirfile,True)
    # 需要检测的文件目录
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

