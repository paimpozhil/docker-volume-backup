import docker
import sys
import tarfile

c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.9',
                  timeout=10)


container = c.inspect_container(sys.argv[1])
container_name =  container['Name']

volumes =  container['Volumes']


tar = tarfile.open("backup.tar.gz", "w:gz")
for i, v in enumerate(volumes):
    print  v, volumes[v]
    tar.add(volumes[v],v)

tar.close()
