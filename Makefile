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
UV ?= uv
RUFF ?= $(UV) run ruff
PYINSTALLER ?= $(UV) run pyinstaller
PYINSTALLER_FLAGS ?= --onefile

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

UNAME := $(shell uname -s)
ifeq ($(UNAME), Linux)
	PYINSTALLER_FLAGS += --strip
endif
build-exe: ## Build a single executable by pyinstaller
	$(PYINSTALLER) $(PYINSTALLER_FLAGS) ./bin/keepassxc-run.py
