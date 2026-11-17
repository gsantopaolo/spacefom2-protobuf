// Tests for the generated Java bindings (run: mvn test, from samples/java).
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.protobuf.Descriptors.Descriptor;
import com.google.protobuf.Descriptors.FieldDescriptor;
import com.google.protobuf.Descriptors.FileDescriptor;
import com.google.protobuf.DynamicMessage;
import com.google.protobuf.Message;
import java.lang.reflect.Method;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.siso.spacefom.v1.DatatypesProto;
import org.siso.spacefom.v1.EntityProto;
import org.siso.spacefom.v1.EnvironmentProto;
import org.siso.spacefom.v1.ExecutionMode;
import org.siso.spacefom.v1.MTRMode;
import org.siso.spacefom.v1.ManagementProto;
import org.siso.spacefom.v1.ReferenceFrame;

class SamplesTest {
  private static final int EXPECTED_MESSAGES = 18;
  private static final List<FileDescriptor> FILES = List.of(
      DatatypesProto.getDescriptor(), EnvironmentProto.getDescriptor(),
      EntityProto.getDescriptor(), ManagementProto.getDescriptor());

  static Stream<Descriptor> allMessages() {
    return FILES.stream().flatMap(f -> f.getMessageTypes().stream());
  }

  /** The generated class for a descriptor, e.g. org.siso.spacefom.v1.ReferenceFrame. */
  private static Message.Builder newBuilder(Descriptor d) throws Exception {
    Class<?> cls = Class.forName(d.getFile().getOptions().getJavaPackage() + "." + d.getName());
    Method m = cls.getMethod("newBuilder");
    return (Message.Builder) m.invoke(null);
  }

  private static Object scalar(FieldDescriptor f) {
    switch (f.getJavaType()) {
      case DOUBLE: return 1.25;
      case LONG: return 7L;
      case STRING: return "x";
      case ENUM:
        var values = f.getEnumType().getValues();
        return values.get(values.size() - 1);
      default: throw new AssertionError("unexpected field " + f.getFullName());
    }
  }

  /** Sets every field (recursively) to a non-default value. */
  private static void fill(Message.Builder b) {
    for (FieldDescriptor f : b.getDescriptorForType().getFields()) {
      if (f.getJavaType() == FieldDescriptor.JavaType.MESSAGE) {
        Message.Builder child = b.newBuilderForField(f);
        fill(child);
        b.setField(f, child.build());
      } else if (f.isRepeated()) {
        for (int i = 0; i < 9; i++) b.addRepeatedField(f, scalar(f));
      } else {
        b.setField(f, scalar(f));
      }
    }
  }

  @Test
  void fixtureValues() throws Exception {
    assertEquals(5, Reader.verify(Path.of("..", "data")));
  }

  @Test
  void everyMessageTypeIsGenerated() {
    assertEquals(EXPECTED_MESSAGES, allMessages().count());
  }

  @ParameterizedTest(name = "{0}")
  @MethodSource("allMessages")
  void everyMessageRoundTripsWithAllFieldsSet(Descriptor d) throws Exception {
    Message.Builder builder = newBuilder(d);
    fill(builder);
    Message original = builder.build();
    assertEquals(d.getFields().size(), original.getAllFields().size());
    Message decoded = newBuilder(d).mergeFrom(original.toByteArray()).build();
    assertEquals(original, decoded);
    // The generated class and the descriptor agree on the wire format.
    assertEquals(original, newBuilder(d).mergeFrom(
        DynamicMessage.parseFrom(d, original.toByteArray()).toByteArray()).build());
  }

  @Test
  void enums() {
    List<Integer> exec = new ArrayList<>();
    for (var v : ExecutionMode.getDescriptor().getValues()) exec.add(v.getNumber());
    assertEquals(List.of(0, 1, 2, 3, 4), exec);
    assertEquals(0, MTRMode.MTR_MODE_UNSPECIFIED.getNumber());
    List<Integer> mtr = new ArrayList<>();
    for (var v : MTRMode.getDescriptor().getValues()) mtr.add(v.getNumber());
    assertEquals(List.of(0, 2, 3, 4), mtr);
  }

  @Test
  void optionalPresence() throws Exception {
    assertFalse(ReferenceFrame.newBuilder().build().hasParentName());
    ReferenceFrame frame = ReferenceFrame.newBuilder().setParentName("").build();
    assertTrue(ReferenceFrame.parseFrom(frame.toByteArray()).hasParentName());
  }
}
