#include <stdio.h>

int main() {
    FILE *f = fopen("/tmp/vmlinux.symbols", "r");
    unsigned long long addr;
    unsigned char type;
    char name[1024];
    unsigned long long count = 0;

    while(fscanf(f, "%lx %c %s", &addr, &type, name) != EOF) {
        printf("/%s/ %lx - Type %c\n", name, addr, type);
        count++;
    }
    printf("Summary: read %d symbols\n", count);
    fclose(f);
  
    return 0;
}
