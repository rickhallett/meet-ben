# Troubleshooting

## Issues During Initial Deployment

If you encounter any errors during the initial deployment, especially related to database connections or missing tables, it's recommended to remove all containers and volumes to start with a clean slate. This ensures that you're working with a fresh environment without any conflicting data from previous attempts.

Follow these steps to clean up your Docker environment:

1. Stop all running containers:

```bash
docker compose down
```

2. Remove all containers related to the project:

```bash
docker rm $(docker ps -a -q --filter name=launchpad_*)
```

3. Remove all volumes related to the project:

```bash
docker volume rm $(docker volume ls -q --filter name=launchpad_*)
```

4. Optionally, you can remove all unused volumes (be cautious if you have other projects using Docker):

```bash
docker volume prune
```

5. Rebuild and start the containers:

```bash
cd docker
./start.sh
```

6. Re-run the migration scripts:
 
```bash
cd ../app
./makemigration.sh
./migrate.sh
```

After performing these steps, you should have a clean environment to work with. If you continue to experience issues, please check the logs for more detailed error messages:

```bash
cd docker
./logs.sh
```

If problems persist, ensure that all environment variables are correctly set in your `.env` files and that there are no conflicts with other services running on your machine.
