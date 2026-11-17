// Tests for the generated C++ bindings (run: ctest, from samples/cpp/build).
#include <string>
#include <vector>

#include <gtest/gtest.h>

#include "checks.h"
#include "google/protobuf/descriptor.h"
#include "google/protobuf/message.h"
#include "siso/spacefom/v1/datatypes.pb.h"
#include "siso/spacefom/v1/entity.pb.h"
#include "siso/spacefom/v1/environment.pb.h"
#include "siso/spacefom/v1/management.pb.h"

namespace sf = siso::spacefom::v1;
using google::protobuf::Descriptor;
using google::protobuf::FieldDescriptor;
using google::protobuf::FileDescriptor;
using google::protobuf::Message;
using google::protobuf::MessageFactory;
using google::protobuf::Reflection;

namespace {

constexpr int kExpectedMessages = 18;

std::vector<const Descriptor*> AllMessages() {
  const FileDescriptor* files[] = {
      sf::PositionVector::descriptor()->file(), sf::ReferenceFrame::descriptor()->file(),
      sf::PhysicalEntity::descriptor()->file(), sf::ExecutionConfiguration::descriptor()->file()};
  std::vector<const Descriptor*> out;
  for (const FileDescriptor* f : files) {
    for (int i = 0; i < f->message_type_count(); ++i) out.push_back(f->message_type(i));
  }
  return out;
}

// Sets every field (recursively) to a non-default value.
void Fill(Message* m) {
  const Reflection* r = m->GetReflection();
  const Descriptor* d = m->GetDescriptor();
  for (int i = 0; i < d->field_count(); ++i) {
    const FieldDescriptor* f = d->field(i);
    switch (f->cpp_type()) {
      case FieldDescriptor::CPPTYPE_MESSAGE:
        Fill(r->MutableMessage(m, f));
        break;
      case FieldDescriptor::CPPTYPE_DOUBLE:
        if (f->is_repeated()) {
          for (int j = 0; j < 9; ++j) r->AddDouble(m, f, 1.25);
        } else {
          r->SetDouble(m, f, 1.25);
        }
        break;
      case FieldDescriptor::CPPTYPE_INT64:
        r->SetInt64(m, f, 7);
        break;
      case FieldDescriptor::CPPTYPE_STRING:
        r->SetString(m, f, "x");
        break;
      case FieldDescriptor::CPPTYPE_ENUM:
        r->SetEnum(m, f, f->enum_type()->value(f->enum_type()->value_count() - 1));
        break;
      default:
        FAIL() << "unexpected field " << f->full_name();
    }
  }
}

}  // namespace

TEST(Samples, FixtureValues) { EXPECT_EQ(samples::Verify(SPACEFOM_DATA_DIR), 5); }

TEST(Samples, EveryMessageTypeIsGenerated) {
  EXPECT_EQ(static_cast<int>(AllMessages().size()), kExpectedMessages);
}

TEST(Samples, EveryMessageRoundTripsWithAllFieldsSet) {
  for (const Descriptor* d : AllMessages()) {
    SCOPED_TRACE(std::string(d->name()));
    // The generated class, through the generated message factory.
    const Message* prototype = MessageFactory::generated_factory()->GetPrototype(d);
    ASSERT_NE(prototype, nullptr);
    std::unique_ptr<Message> original(prototype->New());
    Fill(original.get());
    std::vector<const FieldDescriptor*> set;
    original->GetReflection()->ListFields(*original, &set);
    EXPECT_EQ(static_cast<int>(set.size()), d->field_count());
    std::unique_ptr<Message> decoded(prototype->New());
    ASSERT_TRUE(decoded->ParseFromString(original->SerializeAsString()));
    EXPECT_EQ(decoded->SerializeAsString(), original->SerializeAsString());
    EXPECT_EQ(decoded->DebugString(), original->DebugString());
  }
}

TEST(Samples, Enums) {
  const auto* exec = sf::ExecutionMode_descriptor();
  ASSERT_EQ(exec->value_count(), 5);
  for (int i = 0; i < 5; ++i) EXPECT_EQ(exec->value(i)->number(), i);
  EXPECT_EQ(sf::MTR_MODE_UNSPECIFIED, 0);
  const auto* mtr = sf::MTRMode_descriptor();
  std::vector<int> numbers;
  for (int i = 0; i < mtr->value_count(); ++i) numbers.push_back(mtr->value(i)->number());
  EXPECT_EQ(numbers, (std::vector<int>{0, 2, 3, 4}));
}

TEST(Samples, OptionalPresence) {
  sf::ReferenceFrame frame;
  EXPECT_FALSE(frame.has_parent_name());
  frame.set_parent_name("");
  sf::ReferenceFrame decoded;
  ASSERT_TRUE(decoded.ParseFromString(frame.SerializeAsString()));
  EXPECT_TRUE(decoded.has_parent_name());
}
