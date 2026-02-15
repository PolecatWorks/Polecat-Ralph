BASE_DIR:=../
cli_apps:=ralph

$(foreach app,$(cli_apps),$(app)-venv/bin/activate):%-venv/bin/activate:%-container/pyproject.toml
	@echo Creating venv for $*
	python3 -m venv $*-venv
	$*-venv/bin/pip install --upgrade pip
	$*-venv/bin/pip install poetry
	cd $*-container && \
	${BASE_DIR}$*-venv/bin/poetry install --with dev && \
	${BASE_DIR}$*-venv/bin/pip install -e .[dev]

$(foreach app,$(cli_apps),$(app)-build):%-build:%-venv/bin/activate
	@echo Building $*
	cd $*-container && \
	${BASE_DIR}$*-venv/bin/ralph --help
