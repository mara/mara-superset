
install-superset:
# https://superset.apache.org/docs/installation/installing-superset-from-scratch
	.venv/bin/superset db upgrade
	.venv/bin/superset superset fab create-admin
	.venv/bin/superset superset init

run-superset:
	.venv/bin/superset run -p 8088 --with-threads --reload --debugger
