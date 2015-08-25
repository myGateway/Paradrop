"""
This is intended to have the functions related to creating and provisioning a paradrop router.
Things here will probably end up elsewhere some split between the client and server.
"""

import os, gzip, shutil, subprocess

def zipImage(path):
    print('gzipping img...')
    with open(path, 'rb') as f_in, gzip.open(path + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print('Done gzipping img...')


def unzipImage(path, name):
    print('gunzipping img...')
    with open(name, 'wb') as f_out, gzip.open(path, 'rb') as f_in:
        shutil.copyfileobj(f_in, f_out)
    print('Done gunzipping img...')


def mountImage(name, partition):
    """
    Mount the snappy image so we can alter it. 
    return True on success False on failure
    """
    imgPath = '/home/hyatt/Paradrop/snappy-vm.img'
    excPath = '/home/hyatt/mount.sh'
    mountPath = '/home/hyatt/tmp-router-storage/' + name
    if os.path.exists(mountPath):
        print('Error: path for mounting router already exists')
        return False
    try:
        print ('Creating directory ' + mountPath + '...')
        os.mkdir(mountPath)
    except Exception as e:
        print(e)
        return False
    cmd = [excPath, imgPath, str(partition), mountPath]
    try:
        print ('Running  mount script...')
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        for line in proc.stdout:
            print("mount.sh: {}\n".format(line.strip()))
        for line in proc.stderr:
            print("mount.sh: {}\n".format(line.strip()))
        proc.wait()
        if proc.returncode == 0:
            return True
        else:
            try:
                os.rmdir(mountPath)
            except OSError as e:
                print(e)
            return False
    except OSError as e:
        print('Command "{}" failed\n'.format(" ".join(cmd)))
        try:
            os.rmdir(mountPath)
        except OSError as e:
            print(e)
        return False

def unmountImage(name):
    """
    Unmount the snappy image after we alter it. 
    return True on success False on failure
    """
    mountPath = '/home/hyatt/tmp-router-storage/' + name
    if not os.path.exists(mountPath):
        print('Error: path for unmounting router doesn\'t exist')
        return False
    print ('Unmounting image at ' + mountPath + '...')
    cmd = ['umount', mountPath]
    try:
        print ('Unmounting image...')
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        for line in proc.stdout:
            print("umount: {}\n".format(line.strip()))
        for line in proc.stderr:
            print("umount: {}\n".format(line.strip()))
        proc.wait()
        if proc.returncode == 0:
            try:
                os.rmdir(mountPath)
            except OSError as e:
                print('Failed to rm directory umount may not have worked')
                print(e)
                return False
            return True
        else:
            print('umount failed to unmount the image :(')
            return False
    except OSError as e:
        print('Command "{}" failed\n'.format(" ".join(cmd)))
        print('umount failed to unmount the image :(')
        return False

def placeKeys(ca, pub, mountPath):
    """
    Place the keys in the proper place in the snappy mount.
    return true on success false on failure.
    """
    keyPath = '/system-data/root/apps/paradrop/0.1.0/keys'
    dirs = keyPath.split('/')
    for loc in dirs:
        mountPath += '/' + loc
        if not os.path.exists(mountPath):
            try:
                print ('Creating directory ' + mountPath + '...')
                os.mkdir(mountPath)
            except Exception as e:
                print(e)
                return False
    try:
        with open(mountPath + '/ca', 'wb') as f:
            f.write(ca)
        with open(mountPath + '/pub', 'wb') as f:
            f.write(pub)
    except Exception as e:
        print(e)
        return False 
    return True

def chrootImage(path, pw):
    try:
        os.chroot(path)
    except OSError as e:
        print(e)
        return False
    cmd = ['passwd ubuntu']
    try:
        print ('Unmounting image...')
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        for line in proc.stdout:
            print("umount: {}\n".format(line.strip()))
        for line in proc.stderr:
            print("umount: {}\n".format(line.strip()))
        proc.wait()
        if proc.returncode == 0:
            try:
                os.rmdir(mountPath)
            except OSError as e:
                print('Failed to rm directory umount may not have worked')
                print(e)
                return False
            return True
        else:
            print('umount failed to unmount the image :(')
            return False
    except OSError as e:
        print('Command "{}" failed\n'.format(" ".join(cmd)))
        print('umount failed to unmount the image :(')
        return False
    
    
#zipImage('/home/hyatt/.paradrop/routers/vanilla-snappy.img')
#unzipImage('/home/hyatt/.paradrop/routers/vanilla-snappy.img.gz', '/home/hyatt/.paradrop/routers/snappy.img')
mountImage('pd.nick.test', 5)
with open('/home/hyatt/keys/ca', 'rb') as f:
    ca = f.read()
with open('/home/hyatt/keys/pub', 'rb') as f:
    pub = f.read()
#placeKeys(ca, pub, '/home/hyatt/tmp-router-storage/pd.nick.test')
#unmountImage('pd.nick.test')

'''
from urllib import urlretrieve
import subprocess
import hashlib
#Keeping this around just in case. For now switching to S3 storage model
def getSnappy(cache=False):
    """
    Grab the snappy image and save it locally.
    If cache is true use the allready existing snappy image.
    """
    target = os.path.expanduser("~") + "/.paradrop/routers/vanilla-snappy.img"
    if not cache:
        dirs = ["/.paradrop", "/routers"]
        path = os.path.expanduser("~")
        for loc in dirs:
            path += loc
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except OSError as e:
                    print "Error creating " + path + " directory"
        path += "/vanilla-snappy.img.xz"
        print "Downloading Snappy image..."
        filename, header = urlretrieve("http://releases.ubuntu.com/15.04/ubuntu-15.04-snappy-amd64-generic.img.xz", path)
        cmd = ["unxz", path]
        #TODO: Find a pythonic way to decompress a .xz file that is cross platform
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            for line in proc.stdout:
                print("unxz: {}\n".format(line.strip()))
            for line in proc.stderr:
                print("unxz: {}\n".format(line.strip()))
        except OSError as e:
            print('Command "{}" failed\n'.format(" ".join(cmd)))
            raise e
    else:
        if not os.path.exists(target):
            print "Error the path " + path + " doesn't exist"
            return

def getChecksum(path):
    """
    Given a path to the file get the checksum for that file.
    """

def hashfile(afile, hasher, blocksize=65536):
    """
    returns the hex hash of afile using the given algorithm and blocksize
    """
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest() 
'''
