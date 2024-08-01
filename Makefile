include .env

start:
	docker compose up

# Checking .env settings are OK
check_settings:
	make command script=check_settings 

# Commands
command:
	docker exec -it gitreviewlens_server python /src/presentation/commands/$(script).py

clone_repositories:
	cp -r ~/.ssh ./git
	make command script=clone_repositories
	docker exec -it gitreviewlens_server /Dockerfile.sh

dump_db:
	make command script=dump_database

init_db_from_json_files:
	make setup_db
	docker exec -it gitreviewlens_server python /src/presentation/commands/init_database.py --no-drop_db --load_features --load_pull_requests
	
setup_db:
	docker exec -it gitreviewlens_server python /src/presentation/commands/init_database.py --drop_db --no-load_features --no-load_pull_requests
	docker exec -it -e PGPASSWORD=${DATABASE_USER_PASSWORD} gitreviewlens_postgresql psql -h ${DATABASE_HOST} -U ${DATABASE_USER} -d ${DATABASE_NAME} -f ./indicators.sql

load:
	make command script=load

transcode_into_database:
	make command script=transcode_developers_into_database
	make command script=transcode_pull_requests_into_database

# Bash
bash:
	docker exec -it gitreviewlens_server /bin/bash

install_requirements:
	docker exec gitreviewlens_server pip install -r ./requirements.txt

# CI
run_test_database:
	docker rm -f postgres_test
	docker run -d \
	--name postgres_test \
	-p 6432:5432 \
	-e POSTGRES_DB=test \
	-e POSTGRES_USER=test \
	-e POSTGRES_PASSWORD=test \
	-e POSTGRES_HOST_AUTH_METHOD=trust \
	-v ./postgres/indicators.sql:/indicators.sql \
	postgres:latest

lint:
	python -m isort ./src
	python -m black ./src

checks:
	flake8 ./src
	mypy --namespace-packages --explicit-package-bases --check-untyped-defs ./src

tests:
	pytest ./src

# Demo
create_demo_dataset:
	make command script=create_demo_dataset

load_demo_dataset:
	make setup_db
	cp ./postgres/demo/.env ./.env
	docker exec -it gitreviewlens_server python /src/presentation/commands/init_database.py --path /demo --no-drop_db --load_features --load_pull_requests --env /demo/.env

