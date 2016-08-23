DIRS = demangle xed elf/addr2line

all: $(DIRS)

$(DIRS):
	@echo "=== Building "$@" ==="
	$(MAKE) -C $@
	@echo ""

tests: $(foreach dir, $(DIRS), $(dir)-tests)

$(foreach dir, $(DIRS), $(dir)-tests):
	@echo "=== Testing "$(subst -tests,,$@)" ==="
	$(MAKE) -C $(subst -tests,,$@) tests
	@echo ""

clean: $(foreach dir, $(DIRS), $(dir)-clean)

$(foreach dir, $(DIRS), $(dir)-clean):
	@echo "=== Cleaning "$(subst -clean,,$@)" ==="
	$(MAKE) -C $(subst -clean,,$@) clean
	@echo ""

.PHONY: $(DIRS) clean all tests $(foreach dir, $(DIRS), $(dir)-clean)

