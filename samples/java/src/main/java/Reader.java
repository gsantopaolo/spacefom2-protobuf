// Decode the shared sample data and check every value (see samples/README.md).
import com.google.protobuf.Message;
import com.google.protobuf.Parser;
import java.nio.file.Files;
import java.nio.file.Path;
import org.siso.spacefom.v1.DynamicalEntity;
import org.siso.spacefom.v1.ExecutionConfiguration;
import org.siso.spacefom.v1.ExecutionMode;
import org.siso.spacefom.v1.MTRMode;
import org.siso.spacefom.v1.ModeTransitionRequest;
import org.siso.spacefom.v1.ReferenceFrame;

public final class Reader {
  private static <T extends Message> T load(Path data, Parser<T> parser, String name)
      throws Exception {
    return parser.parseFrom(Files.readAllBytes(data.resolve(name + ".binpb")));
  }

  private static void check(boolean ok, String what) {
    if (!ok) {
      throw new AssertionError(what);
    }
  }

  public static void main(String[] args) throws Exception {
    try {
      int count = verify(Path.of(args.length > 0 ? args[0] : "../data"));
      System.out.println("OK java: " + count + " messages checked");
    } catch (AssertionError e) {
      System.err.println("FAIL java: " + e.getMessage());
      System.exit(1);
    }
  }

  /** Checks every value in the shared data; returns the number of messages checked. */
  public static int verify(Path data) throws Exception {

    ReferenceFrame root = load(data, ReferenceFrame.parser(), "reference_frame_root");
    check(root.getName().equals("RootFrame"), "root frame name");
    check(root.hasParentName() && root.getParentName().isEmpty(), "root parent_name present and empty");

    ReferenceFrame child = load(data, ReferenceFrame.parser(), "reference_frame_child");
    check(child.getParentName().equals("RootFrame"), "child parent_name");
    check(child.getState().getTranslationalState().getPosition().getX() == 1.4959787e11, "child position.x");
    check(child.getState().getRotationalState().getAngularVelocity().getZ() == 7.2921159e-5,
        "child angular_velocity.z");

    DynamicalEntity entity = load(data, DynamicalEntity.parser(), "dynamical_entity");
    check(entity.getName().equals("Lander1"), "entity name");
    check(entity.getMass() == 15000.0, "entity mass");
    check(entity.getInertiaCount() == 9 && entity.getInertia(4) == 2000.0, "entity inertia");
    check(entity.getState().getTime() == 1.5, "entity state.time");
    check(entity.hasForce() && entity.getForce().getX() == 100.5, "entity force");
    check(!entity.hasTorque(), "entity torque absent");

    ExecutionConfiguration config = load(data, ExecutionConfiguration.parser(), "execution_configuration");
    check(config.getCurrentExecutionMode() == ExecutionMode.EXEC_MODE_RUNNING, "current_execution_mode");
    check(config.getNextExecutionMode() == ExecutionMode.EXEC_MODE_FREEZE, "next_execution_mode");
    check(config.getLeastCommonTimeStep() == 250000L, "least_common_time_step");

    ModeTransitionRequest mtr = load(data, ModeTransitionRequest.parser(), "mode_transition_request");
    check(mtr.getExecutionMode() == MTRMode.MTR_GOTO_FREEZE, "MTR execution_mode");

    DynamicalEntity again = DynamicalEntity.parseFrom(entity.toByteArray());
    check(again.equals(entity), "round trip");
    return 5;
  }
}
