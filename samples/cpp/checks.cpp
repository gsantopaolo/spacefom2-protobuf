#include "checks.h"

#include <fstream>
#include <sstream>

#include "siso/spacefom/v1/entity.pb.h"
#include "siso/spacefom/v1/environment.pb.h"
#include "siso/spacefom/v1/management.pb.h"

namespace sf = siso::spacefom::v1;

namespace samples {
namespace {

void Check(bool ok, const std::string& what) {
  if (!ok) throw CheckError(what);
}

template <typename T>
T Load(const std::string& data_dir, const std::string& name) {
  std::ifstream in(data_dir + "/" + name + ".binpb", std::ios::binary);
  std::stringstream bytes;
  bytes << in.rdbuf();
  T message;
  Check(in && message.ParseFromString(bytes.str()), "cannot read " + name);
  return message;
}

}  // namespace

int Verify(const std::string& data_dir) {
  auto root = Load<sf::ReferenceFrame>(data_dir, "reference_frame_root");
  Check(root.name() == "RootFrame", "root frame name");
  Check(root.has_parent_name() && root.parent_name().empty(), "root parent_name present and empty");

  auto child = Load<sf::ReferenceFrame>(data_dir, "reference_frame_child");
  Check(child.parent_name() == "RootFrame", "child parent_name");
  Check(child.state().translational_state().position().x() == 1.4959787e11, "child position.x");
  Check(child.state().rotational_state().angular_velocity().z() == 7.2921159e-5,
        "child angular_velocity.z");

  auto entity = Load<sf::DynamicalEntity>(data_dir, "dynamical_entity");
  Check(entity.name() == "Lander1", "entity name");
  Check(entity.mass() == 15000.0, "entity mass");
  Check(entity.inertia_size() == 9 && entity.inertia(4) == 2000.0, "entity inertia");
  Check(entity.state().time() == 1.5, "entity state.time");
  Check(entity.has_force() && entity.force().x() == 100.5, "entity force");
  Check(!entity.has_torque(), "entity torque absent");

  auto config = Load<sf::ExecutionConfiguration>(data_dir, "execution_configuration");
  Check(config.current_execution_mode() == sf::EXEC_MODE_RUNNING, "current_execution_mode");
  Check(config.next_execution_mode() == sf::EXEC_MODE_FREEZE, "next_execution_mode");
  Check(config.least_common_time_step() == 250000, "least_common_time_step");

  auto mtr = Load<sf::ModeTransitionRequest>(data_dir, "mode_transition_request");
  Check(mtr.execution_mode() == sf::MTR_GOTO_FREEZE, "MTR execution_mode");

  sf::DynamicalEntity again;
  Check(again.ParseFromString(entity.SerializeAsString()) &&
            again.SerializeAsString() == entity.SerializeAsString(),
        "round trip");

  return 5;
}

}  // namespace samples
