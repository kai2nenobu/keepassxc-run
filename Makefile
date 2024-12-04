# Inspired by https://postd.cc/auto-documented-makefile/
MAKEFLAGS += --warn-undefined-variables
SHELL = /bin/bash
.SHELLFLAGS = -e -o pipefail -c
.DEFAULT_GOAL = help

# Use UTF-8 as Python default encoding
export PYTHONUTF8 = 1

# If SHLVL is undefined, use bash in "Git for Windows"
ifndef SHLVL
    SHELL = C:\Program Files\Git\bin\bash.exe
endif

# Make all targets PHONY other than targets including . in its name
.PHONY: $(shell grep -oE ^[a-zA-Z0-9%_-]+: $(MAKEFILE_LIST) | sed 's/://')

# Variables
PROJECT := keepassxc-run
UV ?= uv
RUFF ?= $(UV) run ruff
PYINSTALLER ?= $(UV) run pyinstaller
PYINSTALLER_FLAGS ?= --onefile

# OS detection
ifeq ($(OS),Windows_NT)
    detected_os := Windows
else
	# Linux or Darwin or others
    detected_os := $(shell uname -s)
endif

# architecture detection
detected_arch := $(shell uname -m)

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = make":.*?## "} /^[a-zA-Z0-9%_-]+:.*?## / {printf "    \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Configure a local dev environment. Execute once after cloning this repository
	$(UV) sync

lint: ## Lint all files
	$(RUFF) check .

format: ## Format all files
	$(RUFF) format .

build: ## Build a package
	$(UV) build


# Tasks for executables
executable_name := $(PROJECT)
archive_extension := tar.gz
ifeq ($(detected_os),Windows)
    executable_name := $(PROJECT).exe
    archive_extension := zip
else
    PYINSTALLER_FLAGS += --strip
endif
archive_file := $(PROJECT)_$(detected_os)_$(detected_arch).$(archive_extension)

build-exe: ## Build a single executable by pyinstaller
	$(PYINSTALLER) $(PYINSTALLER_FLAGS) ./bin/$(PROJECT).py

archive-exe: ## Archive a single executable
ifeq ($(detected_os),Windows)
	mkdir -p archive && cd dist && pwsh -NoProfile -Command \
		"Compress-Archive -DestinationPath ../archive/$(archive_file) -LiteralPath $(executable_name)"
else
	mkdir -p archive && cd dist && tar cf "../archive/$(archive_file)" "$(executable_name)"
endif

upload-archive: ## Upload an archive per platform to GitHub release assets
	gh release upload $(TAG_NAME) archive/$(archive_file)

clean: ## Clean up generated files
	@$(RM) -r build/ dist/ archive/
