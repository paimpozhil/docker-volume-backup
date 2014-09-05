import docker
import sys
import pickle
import tarfile
import os
from subprocess import call

c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.9',
                  timeout=10)
#Prints Help Message
def usage():
	print "Running normally :"
	print "	python backup.py [backup/restore] data-container-name [restore-container-name]"
	print "Running withing as a docker image (named docker-volume-backup) :"
	print " docker run -t -i --rm \ "
	print "  -v /var/lib/docker/vfs:/var/lib/docker/vfs \ "
	print "  -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/backup docker-volume-backup \ "
	print "  backup <container>"
	print "docker run -t -i --rm \ "
	print "  -v /var/lib/docker/vfs:/var/lib/docker/vfs \ "
	print "  -v /var/run/docker.sock:/var/run/docker.sock \ "
	print "  restore <backupedcontainer> <newcontainer> <tar storage absolute path on host>"
#Determines if we run within a docker container
#Might not be truly cleany as a way to check but it works ;)
def dockerized():
	if 'docker' in open('/proc/1/cgroup').read():
		return True

#first argument is the option backup/restore
if len(sys.argv) < 3:
	print "Not enough arguments !!"
	usage()
	sys.exit(1)

#Location of the tar files (for a container running)
datadir = "/backup"

#first argument is the option backup/restore
option = sys.argv[1]
name = sys.argv[2]


if option == "backup":
	# second argument is the container name
	container = c.inspect_container(name)
	container_name =  container['Name']
	print "Backing up : " + container_name
	volumes =  container['Volumes']
	
	print "writing meta data to file "
	pickle.dump ( container , open ("metadata","wb") )


	if dockerized():
		tar = tarfile.open(datadir + "/" + name + ".tar", "w:gz")
	else:
		tar = tarfile.open(name + ".tar", "w:gz")
	tar.add("metadata")
	for i, v in enumerate(volumes):
	    print  v, volumes[v]
	    tar.add(volumes[v],v)
	tar.close()

elif option == "restore":
	#third argument is the restored container name
	destname = sys.argv[3]
	if dockerized() and len(sys.argv) < 5:
		print "Restore Storage is missing !"
		usage()
		sys.exit(1)
	
	print "Restoring"
	if dockerized():
		tar = tarfile.open(datadir + "/" + name + ".tar")
	else:
		tar = tarfile.open(name + ".tar")
	metadatafile =  tar.extractfile("metadata")
	metadata =  pickle.load(metadatafile)

	imagename = metadata["Config"]["Image"]
        volumes =  metadata['Volumes']
	vlist = []
	for i, v in enumerate(volumes):
       		print  v, volumes[v]
		vlist.append(v)

	#Start the restored container
	restored_container = c.create_container(imagename,tty=True,volumes=vlist,name=destname)
	c.start(restored_container);

	#Recreate volumes_from (as it does not work when binds+volumes_from are used together
	infodest = c.inspect_container(restored_container)
	volumes = infodest['Volumes']
	vlist = []
	binds = {}
	for i, v in enumerate(volumes):
		vlist.append(v)
		binding = { volumes[v]:{'bind':v} }
		binds.update(binding)

	#Add tar storage to bindings list
	if dockerized():
		datadir = sys.argv[4]
	        binds.update({str(datadir): {'bind': '/backup2'} })
	else:
	        binds.update({ str(os.path.dirname(os.path.realpath(__file__))): {'bind': '/backup2'} })

	#Start the restorer container
	restorer_container = c.create_container('ubuntu',detach=False, tty=True, command="tar xvf /backup2/"+ name +".tar",volumes=vlist)
	c.start(restorer_container,binds=binds)	
	c.wait(restorer_container)
	print c.logs(restorer_container['Id'])
	c.remove_container(restorer_container)
	
else:
	usage()

