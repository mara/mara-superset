# run Apache Superset locally


setup-superset: .copy-mara-superset-scripts


run-superset:
	.venv/bin/superset run -p 8088 --with-threads --reload --debugger

install-superset:
# https://superset.apache.org/docs/installation/installing-superset-from-scratch
	.venv/bin/superset db upgrade
	.venv/bin/superset superset fab create-admin
	.venv/bin/superset superset init


# copy scripts from mara-superset package to project code
.copy-mara-superset-scripts:
	rsync --archive --recursive --itemize-changes  --delete packages/mara-superset/.scripts/ .scripts/mara-superset/
