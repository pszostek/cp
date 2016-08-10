DIRS = demangle xed elf/addr2line

all: $(DIRS)

$(DIRS):
	@echo "=== Building "$@" ==="
	$(MAKE) -C $@
	@echo ""

clean: $(foreach dir, $(DIRS), $(dir)-clean)

$(foreach dir, $(DIRS), $(dir)-clean):
	@echo "=== Cleaning "$(subst -clean,,$@)" ==="
	$(MAKE) -C $(subst -clean,,$@) clean
	@echo ""

.PHONY: $(DIRS) clean all

