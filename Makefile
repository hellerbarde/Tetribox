# Installation-dependent settings. You can overwrite these in a file called config.mk in the same directory as this makefile. See readme.creole.
INKSCAPE := inkscape
PYTHON := python2
ASYMPTOTE := asy

GENERATED_DIR := generated

# Settings affecting the compiled results. You can overwrite these in a file called settings.mk in the same directory as this makefile. See readme.creole.
DXF_FLATNESS := 0.1

# Non-file goals.
.PHONY: all clean generated asy pdf svg

# Remove targets whose command failed.
.DELETE_ON_ERROR:

# Do not print commands as they are executed. They do not show the actual invocation of the respective tools anyways but just the Python wrappers.
.SILENT:

# Set the default goal. Prevents it from being overwritten accidentially from config.mk or settings.mk.
.DEFAULT_GOAL := all

# Include the configuration files.
-include config.mk settings.mk

# Command to run the Python scripts.
PYTHON_CMD := PYTHONPATH="support" $(PYTHON)
INKSCAPE_CMD := INKSCAPE=$(INKSCAPE) DXF_FLATNESS=$(DXF_FLATNESS) $(PYTHON_CMD) -m inkscape  
ASYMPTOTE_CMD := ASYMPTOTE=$(ASYMPTOTE) $(PYTHON_CMD) -m asymptote

# Function with arguments (ext, subst_ext, names).
# Takes a list of file names and returns all elements whose basename do not start with a `_' and which have extension ext. The returned names will have their extension replaced by subst_ext.
filter_compiled = $(foreach i,$(patsubst %$1,%$2,$(filter %$1,$3)),$(if $(filter-out _%,$(notdir $i)),$i))

# All considered source and target files currently existing.
EXISTING_FILES := $(shell mkdir -p $(GENERATED_DIR) && find src $(GENERATED_DIR) -not \( \( -name '.*' -or -name '* *' \) -prune \) -type f)

# Run generate_sources.py to get the names of all files that should be generated using that same script.
GENERATED_FILES := $(shell ./generate_sources.py list --dir $(GENERATED_DIR))

# All visible files in the src directory that either exist or can be generated. Ignore files whose names contain spaces.
SRC_FILES := $(sort $(GENERATED_FILES) $(EXISTING_FILES))

# PDF files which can be generated from Asymptote files. We exclude SVG_ASY_FILES because they don't contain any drawing primitives and thus won't produce a PDF.
ASY_PDF_FILES := $(call filter_compiled,.asy,.pdf,$(filter-out $(SVG_ASY_FILES),$(SRC_FILES)))

# SVG files which can be generated from Asymptote files. We exclude SVG_ASY_FILES because they don't contain any drawing primitives and thus won't produce a PDF.
ASY_SVG_FILES := $(call filter_compiled,.asy,.svg,$(filter-out $(SVG_ASY_FILES),$(SRC_FILES)))

# Makefiles which are generated while compiling to record dependencies.
DEPENDENCY_FILES := $(patsubst %,.%.d,$(ASY_PDF_FILES))

# Files that may be used from Asymptote files.
ASY_DEPS := $(filter %.asy,$(SRC_FILES)) $(SVG_ASY_FILES)

# Dependencies which may affect the result of all build products.
GLOBAL_DEPS := Makefile $(wildcard config.mk settings.mk)

# All existing target files.
EXISTING_TARGETS := $(filter $(ASY_PDF_FILES) $(ASY_SVG_FILES) $(GENERATED_FILES) $(DEPENDENCY_FILES),$(EXISTING_FILES))

# Goal to build Everything. Also generates files which aren't compiled to anything else. Deined here to make it the default goal.
all: generated svg pdf
#$(ASY_SVG_FILES) 

# Everything^-1.
clean:
	echo [clean] $(EXISTING_TARGETS)
	rm -rf $(EXISTING_TARGETS)

# Goals to build the project up to a specific step.
generated: $(GENERATED_FILES)
asy: $(SVG_ASY_FILES)
pdf: $(ASY_PDF_FILES)
svg: $(ASY_SVG_FILES)

# Rule to compile an Asymptote file to a PDF file.
$(ASY_PDF_FILES): %.pdf: %.asy $(GLOBAL_DEPS) | $(ASY_DEPS)
	echo [asymptote PDF] $@
	$(ASYMPTOTE_CMD) $< $@ ./src

# Rule to compile an Asymptote file to a SVG file.
$(ASY_SVG_FILES): %.svg: %.asy $(GLOBAL_DEPS) | $(ASY_DEPS)
	echo [asymptote SVG] $@
	$(ASYMPTOTE_CMD) $< $@ ./src

# Rule for automaticaly generated Asymptote files.
$(GENERATED_FILES): generate_sources.sh $(GLOBAL_DEPS)
	echo [generate] $@
	./generate_sources.py generate $@

# Include dependency files produced by an earlier build.
-include $(DEPENDENCY_FILES)
