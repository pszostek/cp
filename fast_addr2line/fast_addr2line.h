extern "C" {
#include "xed-interface.h"
#include "xed-immdis.h"
#include "xed-portability.h"
#include "xed-examples-util.h"
#include "xed-types.h"
}
#include <string>

void initialize_line_numbers(char* input_file_name);
int find_line_number(uint64_t addr, std::string& file,  xed_uint32_t& line);