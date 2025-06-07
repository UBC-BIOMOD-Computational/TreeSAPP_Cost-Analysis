
# Run TreeSAPP locally instructions

## download docker
TODO

## download TreeSAPP image
```
docker pull quay.io/hallamlab/treesapp
docker run -itd quay.io/hallamlab/treesapp:latest
> returns the id
```

Run `docker image` to check if `quay.io/hallamlab/treesapp:latest` shows up

## run docker with mounted folder
``` 
                            bind folder     source folder          dest folder (in container)                image
docker run -t -i -d --mount type=bind,source="{your_local_folder}",destination=/mounted_folder quay.io/hallamlab/treesapp:latest
```

Run `docker ps` to check if container has spun up with the image.
Should look like:
> `>`  

Take a note of your `container_id` which should look like `adjective_noun` such as `laughing_williamson`

## Execute TreeSAPP commands on your running container

> `docker exec {container_id} sh -c "cd mounted_folder && ls"`
This command should show the contents of {your_local_folder}

> `docker exec {container_id} treesapp create --fastx_input /mounted_folder{your_fasta_file} --output {your_output_filefolder} --refpkg_name ca2 --molecule prot`
note that `--output {your_output_filefolder}` shows you where TreeSAPP will put the files, we want it to be in our mounted folder
