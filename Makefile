.PHONY: env env-update env-clean

# CC=gcc forces the plain host compiler instead of conda's own cross
# toolchain -- see the comment in environment.yml for why that's required
# to build pynput's evdev dependency.
env:
	CC=gcc conda env create -f environment.yml

env-update:
	CC=gcc conda env update -f environment.yml --prune

env-clean:
	conda env remove -n cat
