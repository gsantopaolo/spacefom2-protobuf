package main

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/reflect/protoregistry"

	pb "github.com/gsantopaolo/spacefom2-protobuf/samples/generated/go/siso/spacefom/v1"
)

const expectedMessages = 18

var files = []protoreflect.FileDescriptor{
	pb.File_siso_spacefom_v1_datatypes_proto,
	pb.File_siso_spacefom_v1_environment_proto,
	pb.File_siso_spacefom_v1_entity_proto,
	pb.File_siso_spacefom_v1_management_proto,
}

func allMessages() []protoreflect.MessageDescriptor {
	var out []protoreflect.MessageDescriptor
	for _, f := range files {
		for i := 0; i < f.Messages().Len(); i++ {
			out = append(out, f.Messages().Get(i))
		}
	}
	return out
}

func scalar(t *testing.T, fd protoreflect.FieldDescriptor) protoreflect.Value {
	switch fd.Kind() {
	case protoreflect.DoubleKind:
		return protoreflect.ValueOfFloat64(1.25)
	case protoreflect.Int64Kind:
		return protoreflect.ValueOfInt64(7)
	case protoreflect.StringKind:
		return protoreflect.ValueOfString("x")
	case protoreflect.EnumKind:
		values := fd.Enum().Values()
		return protoreflect.ValueOfEnum(values.Get(values.Len() - 1).Number())
	}
	t.Fatalf("unexpected kind %v in %s", fd.Kind(), fd.FullName())
	return protoreflect.Value{}
}

// fill sets every field of m (recursively) to a non-default value.
func fill(t *testing.T, m protoreflect.Message) {
	fields := m.Descriptor().Fields()
	for i := 0; i < fields.Len(); i++ {
		fd := fields.Get(i)
		switch {
		case fd.Kind() == protoreflect.MessageKind:
			fill(t, m.Mutable(fd).Message())
		case fd.IsList():
			list := m.Mutable(fd).List()
			for j := 0; j < 9; j++ {
				list.Append(scalar(t, fd))
			}
		default:
			m.Set(fd, scalar(t, fd))
		}
	}
}

func countSet(m protoreflect.Message) int {
	n := 0
	m.Range(func(protoreflect.FieldDescriptor, protoreflect.Value) bool { n++; return true })
	return n
}

func TestFixtureValues(t *testing.T) {
	count, err := verify()
	if err != nil || count != 5 {
		t.Fatalf("verify() = %d, %v", count, err)
	}
}

func TestEveryMessageTypeIsGenerated(t *testing.T) {
	if n := len(allMessages()); n != expectedMessages {
		t.Fatalf("got %d message types, want %d", n, expectedMessages)
	}
}

func TestEveryMessageRoundTripsWithAllFieldsSet(t *testing.T) {
	for _, md := range allMessages() {
		t.Run(string(md.Name()), func(t *testing.T) {
			// The generated Go type, looked up by name.
			mt, err := protoregistry.GlobalTypes.FindMessageByName(md.FullName())
			if err != nil {
				t.Fatal(err)
			}
			original := mt.New()
			fill(t, original)
			if got := countSet(original); got != md.Fields().Len() {
				t.Fatalf("set %d of %d fields", got, md.Fields().Len())
			}
			b, err := proto.Marshal(original.Interface())
			if err != nil {
				t.Fatal(err)
			}
			decoded := mt.New().Interface()
			if err := proto.Unmarshal(b, decoded); err != nil {
				t.Fatal(err)
			}
			if !proto.Equal(decoded, original.Interface()) {
				t.Fatal("decoded message differs")
			}
		})
	}
}

func TestEnums(t *testing.T) {
	exec := pb.ExecutionMode(0).Descriptor().Values()
	for i := 0; i < exec.Len(); i++ {
		if int(exec.Get(i).Number()) != i {
			t.Fatalf("ExecutionMode value %d = %d", i, exec.Get(i).Number())
		}
	}
	if pb.MTRMode_MTR_MODE_UNSPECIFIED != 0 {
		t.Fatal("MTR_MODE_UNSPECIFIED != 0")
	}
	want := []protoreflect.EnumNumber{0, 2, 3, 4}
	mtr := pb.MTRMode(0).Descriptor().Values()
	for i, n := range want {
		if mtr.Get(i).Number() != n {
			t.Fatalf("MTRMode value %d = %d, want %d", i, mtr.Get(i).Number(), n)
		}
	}
}

func TestOptionalPresence(t *testing.T) {
	frame := &pb.ReferenceFrame{}
	if frame.ParentName != nil {
		t.Fatal("parent_name set on a new message")
	}
	frame.ParentName = proto.String("")
	b, _ := proto.Marshal(frame)
	decoded := &pb.ReferenceFrame{}
	if err := proto.Unmarshal(b, decoded); err != nil || decoded.ParentName == nil {
		t.Fatal("empty parent_name lost its presence")
	}
}
