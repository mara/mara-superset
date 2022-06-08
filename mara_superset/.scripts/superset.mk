# run Apache Superset locally

#superset-metadata-db ?= superset_metadata
superset-config-path ?= app/superset_config.py
superset-package-name ?= "apache-superset[postgres]>=1.3.2"


setup-superset: .copy-mara-superset-scripts


run-superset:
	SUPERSET_CONFIG_PATH=$(superset-config-path) .superset/bin/gunicorn --bind "$${SUPERSET_BIND_ADDRESS:-0.0.0.0}:$${SUPERSET_PORT:-8088}" --workers $${SERVER_WORKER_AMOUNT:-1} --worker-class $${SERVER_WORKER_CLASS:-gthread} --threads $${SERVER_THREADS_AMOUNT:-20} --timeout $${GUNICORN_TIMEOUT:-60} --limit-request-line $${SERVER_LIMIT_REQUEST_LINE:-0} --limit-request-field_size $${SERVER_LIMIT_REQUEST_FIELD_SIZE:-0} "superset.app:create_app()" 2>&1

# install apache superset locally for dev. purposes
install-local-superset:
	mkdir -p .superset
	.venv/bin/python -m venv .superset
	.superset/bin/pip install --upgrade pip wheel
	.superset/bin/pip install $(superset-package-name)
	ln -s ../../.superset/bin/superset .venv/bin/superset

# install required dependencies for SQL Server
install-local-superset-mssql:
	.superset/bin/pip install pyodbc

install-superset:
# https://superset.apache.org/docs/installation/installing-superset-from-scratch
	echo export SUPERSET_CONFIG_PATH=$(superset-config-path) >> .venv/bin/activate
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset db upgrade
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset fab create-admin --username admin --firstname "Superset" --lastname "Admin" --email admin@superset.com --password admin
	SUPERSET_CONFIG_PATH=$(superset-config-path) .venv/bin/superset init

# copy scripts from mara-superset package to project code
.copy-mara-superset-scripts: MODULE_LOCATION != .venv/bin/python -m pip show mara-superset | sed -n -e 's/Location: //p'
.copy-mara-superset-scripts:
	rsync --archive --recursive --itemize-changes  --delete $(MODULE_LOCATION)/mara_superset/.scripts/ .scripts/mara-superset/

# remove virtual env for superset
.cleanup-superset:
	rm -rf .superset
	rm -f .venv/bin/superset