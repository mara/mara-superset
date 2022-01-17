# run Apache Superset locally

#superset-metadata-db ?= superset_metadata
superset-config-path ?= app/superset_config.py


setup-superset: .copy-mara-superset-scripts


run-superset:
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset run -p 8088 --with-threads --reload --debugger


install-superset:
# https://superset.apache.org/docs/installation/installing-superset-from-scratch
	echo export SUPERSET_CONFIG_PATH=$(superset-config-path) >> .venv/bin/activate
	mkdir -p .superset
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset db upgrade
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset fab create-admin --username admin --firstname "Superset" --lastname "Admin" --email admin@superset.com --password admin
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset init


# copy scripts from mara-superset package to project code
.copy-mara-superset-scripts:
	rsync --archive --recursive --itemize-changes  --delete packages/mara-superset/.scripts/ .scripts/mara-superset/
