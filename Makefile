.PHONY: env env-update env-clean

# CC=gcc forces the plain host compiler instead of conda's own cross
# toolchain -- see the comment in enviroment.yml for why that's required
# to build pynput's evdev dependency.
env:
	CC=gcc conda env create -f enviroment.yml

env-update:
	CC=gcc conda env update -f enviroment.yml --prune

env-clean:
	conda env remove -n cat
