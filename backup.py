import docker
import sys
import pickle
import tarfile

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

	tar = tarfile.open("backup.tar.gz", "w:gz")
	tar.add("metadata")
	for i, v in enumerate(volumes):
	    print  v, volumes[v]
	    tar.add(volumes[v],v)
	tar.close()

elif option == "restore":
	print "Restoring"
	tar = tarfile.open("backup.tar.gz")
	metadatafile =  tar.extractfile("metadata")
	metadata =  pickle.load(metadatafile)

#	print metadata
	imagename = metadata["Config"]["Image"]
	volumes =  metadata['Volumes']
	vlist = []

	for i, v in enumerate(volumes):
       		print  v, volumes[v]
		vlist.append(v)

	restored_container =	c.create_container(imagename,tty=True,volumes=vlist)
	c.start(restored_container);
	
	


