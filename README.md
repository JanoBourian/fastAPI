# fastAPI
The FastAPI course with AWS

## Information about Docker Container for PostgreSQL

From the Docker documentation we have the next code:

```cmd
docker run -d \
	--name postresfastapi \
	-e POSTGRES_PASSWORD=mysecretpassword \
	-e POSTGRES_USER=myusername \
	-e PGDATA=/var/lib/postgresql/data/pgdata \
	-p 5432:5432 \
	-v C:\\Users\\super\\Documents\\databases\\FastAPI:/var/lib/postgresql/data \
	-d postgres
```

We have other alternative

```cmd
docker run -d --name postresfastapi -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=myusername -e PGDATA=/var/lib/postgresql/data/pgdata -p 5432:5432 -v C:\\Users\\super\\Documents\\databases\\FastAPI:/var/lib/postgresql/data -d postgres
```
