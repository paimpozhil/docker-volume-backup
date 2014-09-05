docker-volume-backup
====================

a python script to backup/restore the docker data containers / volumes.

this script is particularly suitable for volume only contianers thought it should work with any container that has volumes. 

####Requires Python && Docker-py python package.

```
apt-get install python-pip 
pip install docker-py
```


##How to use
```
python backup.py backup [yourcontainername]
```

will output a tar file with name of your container that you can move around

```
python backup.py restore [yourcontainername] [destinationname]
```

will restore the tar backup as a new data container

```
python backup.py help me  
```

will out put the help message .. which is indeed not very helpful at the moment

## Example usage:

start your docker container which has volumes.. 
Note I use my generic paimpozhil/data container which i use for my Whatpanel which is my own cPanel replacement.

more info here : https://github.com/paimpozhil/WhatPanel

```
root@dockerhost# docker run -td --name mydata  paimpozhil/data
eba7a4aef3e3007d41b81a45e914196c3a74d0e69adaa4f781c2decb83730619

## data container created

root@dockerhost# docker ps
CONTAINER ID        IMAGE                    COMMAND             CREATED              STATUS              PORTS               NAMES
eba7a4aef3e3        paimpozhil/data:latest   /bin/sh             About a minute ago   Up About a minute                       mydata

## Now you see it created now use the volumes in your any other containers

root@dockerhost# docker run -ti --volumes-from mydata ubuntu /bin/bash

root@c2b83b3971c3:/# ls
backup  bin  boot  data  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
root@c2b83b3971c3:/# cd /data

## create a BIG 100M file
root@c2b83b3971c3:/data# dd if=/dev/urandom of=bigfile bs=1024 count=102400

## exit and try to run another container to ensure the data is there .

root@a09fe3caf955:/data# ls -alth bigfile
-rw-r--r-- 1 root root 100M Jun 19 22:00 bigfile

### exit now and back to the host

root@dockerhost# python backup.py backup mydata

##creates mydata.tar -rw-r--r-- 1 root root 101M Jun 19 22:03 mydata.tar

### now copy it around to any host or just restore here in any other name.

root@dockerhost# python backup.py restore mydata myotherdata
Restoring
/backup /var/lib/docker/vfs/dir/de537270e1d2365f6c3d32116549e54ef480a32e96b4caf51964a949ec875201
/var/lib/mysql /var/lib/docker/vfs/dir/56a88d289ddb8d641fea0c16e972f507c70e34dc81c1460499634e4c900c94ca
/data /var/lib/docker/vfs/dir/5bc67e4aaab669719b7cc24ab709a417a549e03d4eb550108355323895723740
/var/www /var/lib/docker/vfs/dir/de95abd703a13365c5cffecbc05eff533b3ced2fb3fc79f3fdd99e13cc1d299b
docker run --rm -ti --volumes-from e0ff233216f35cc151c081a55fa8943fabfbf86bed0234c801f44a7ecbbdfbd2 -v $(pwd):/backup2  ubuntu tar xvf /backup2/mydata.tar
metadata
backup/
var/lib/mysql/
data/
data/bigfile
var/www/

### now check if you have the correct data

root@dockerhost# docker run -ti --volumes-from myotherdata ubuntu /bin/bash
root@ac5671887ea0:/# cd /data
root@ac5671887ea0:/data# ls
bigfile

## make some changes to the new copy

root@ac5671887ea0:/data# touch this is my other data
root@ac5671887ea0:/data# ls
bigfile  data  is  my  other  this
root@ac5671887ea0:/data#

## Ensure your actual data is intact  :p 

root@dockerhost# docker run -ti --volumes-from mydata ubuntu /bin/bash
root@3acae1260562:/# ls
backup  bin  boot  data  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
root@3acae1260562:/# cd /data
root@3acae1260562:/data# ls
bigfile
root@3acae1260562:/data#

```

## Run as a container
First, you need to build it :
```
docker build --rm --no-cache -t docker-volume-backup .
```

Once done, can can backup using :
```
docker run -t -i --rm \
  -v /var/lib/docker/vfs:/var/lib/docker/vfs \
  -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/backup docker-volume-backup \
  backup <container>
```
The .tar backups will be stored in /backup ... which you can bind to any dir on your docker host (above on /tmp not a good idea ;) )


```
 docker run -t -i --rm \
  -v /var/lib/docker/vfs:/var/lib/docker/vfs \
  -v /var/run/docker.sock:/var/run/docker.sock \
  restore <backupedcontainer> <newcontainer> <tar storage absolute path on host>
```
The .tar backups will be Fetched in "tar storage absolute path on host" ...



## Credits & references : 
http://docs.docker.com/userguide/dockervolumes/#creating-and-mounting-a-data-volume-container

## Need support?

#### http://dockerteam.com
