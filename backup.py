import docker
import sys
import pickle
import tarfile
from subprocess import call

c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.9',
                  timeout=10)

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

	tar = tarfile.open(name + ".tar", "w:gz")
	tar.add("metadata")
	for i, v in enumerate(volumes):
	    print  v, volumes[v]
	    tar.add(volumes[v],v)
	tar.close()

elif option == "restore":
	#third argument is the restored container name
	destname = sys.argv[3]
	
	print "Restoring"
	tar = tarfile.open(name + ".tar")
	metadatafile =  tar.extractfile("metadata")
	metadata =  pickle.load(metadatafile)

#	print metadata
	imagename = metadata["Config"]["Image"]
	volumes =  metadata['Volumes']
	vlist = []

	for i, v in enumerate(volumes):
       		print  v, volumes[v]
		vlist.append(v)

	restored_container = c.create_container(imagename,tty=True,volumes=vlist,name=destname)
	c.start(restored_container);
	runstring = "docker run --rm -ti --volumes-from " + restored_container['Id'] +" -v $(pwd):/backup2  ubuntu tar xvf /backup2/"+ name +".tar"
	print runstring
	call(runstring,shell=True)
	
elif option == "help":
	print "python backup.py [backup/restore] data-container-name [restore-contianer-name]"


