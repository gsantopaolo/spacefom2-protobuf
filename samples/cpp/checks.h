// Checks every value in the shared sample data (see samples/README.md).
#pragma once

#include <stdexcept>
#include <string>

namespace samples {

// Throws CheckError naming the first value that does not match.
struct CheckError : std::runtime_error {
  using std::runtime_error::runtime_error;
};

// Returns the number of messages checked.
int Verify(const std::string& data_dir);

}  // namespace samples
