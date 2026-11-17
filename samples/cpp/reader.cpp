// Decode the shared sample data and check every value (see samples/README.md).
#include <iostream>

#include "checks.h"

int main(int argc, char** argv) {
  try {
    int count = samples::Verify(argc > 1 ? argv[1] : SPACEFOM_DATA_DIR);
    std::cout << "OK cpp: " << count << " messages checked\n";
    return 0;
  } catch (const samples::CheckError& e) {
    std::cerr << "FAIL cpp: " << e.what() << "\n";
    return 1;
  }
}
