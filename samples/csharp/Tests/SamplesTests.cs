// Tests for the generated C# bindings (run: dotnet test Tests, from samples/csharp).
using Google.Protobuf;
using Google.Protobuf.Reflection;
using Siso.Spacefom.V1;
using Xunit;

public class SamplesTests
{
    const int ExpectedMessages = 18;

    static readonly FileDescriptor[] Files =
    {
        DatatypesReflection.Descriptor, EnvironmentReflection.Descriptor,
        EntityReflection.Descriptor, ManagementReflection.Descriptor,
    };

    static IEnumerable<MessageDescriptor> AllMessages() => Files.SelectMany(f => f.MessageTypes);

    public static TheoryData<string> MessageNames() => new(AllMessages().Select(m => m.Name));

    static object Scalar(FieldDescriptor f) => f.FieldType switch
    {
        FieldType.Double => 1.25,
        FieldType.Int64 => 7L,
        FieldType.String => "x",
        FieldType.Enum => f.EnumType.Values[^1].Number,
        _ => throw new InvalidOperationException($"unexpected field {f.FullName}"),
    };

    // Sets every field (recursively) to a non-default value.
    static void Fill(IMessage message)
    {
        foreach (var f in message.Descriptor.Fields.InDeclarationOrder())
        {
            if (f.FieldType == FieldType.Message)
            {
                var child = f.MessageType.Parser.ParseFrom(ByteString.Empty);
                Fill(child);
                f.Accessor.SetValue(message, child);
            }
            else if (f.IsRepeated)
            {
                var list = (System.Collections.IList)f.Accessor.GetValue(message);
                for (var i = 0; i < 9; i++) list.Add(Scalar(f));
            }
            else
            {
                f.Accessor.SetValue(message, Scalar(f));
            }
        }
    }

    static int CountSet(IMessage message) =>
        message.Descriptor.Fields.InDeclarationOrder().Count(f =>
            f.IsRepeated ? ((System.Collections.IList)f.Accessor.GetValue(message)).Count > 0
            : f.HasPresence ? f.Accessor.HasValue(message)
            : !Equals(f.Accessor.GetValue(message), f.Accessor.GetValue(f.ContainingType.Parser.ParseFrom(ByteString.Empty))));

    [Fact]
    public void FixtureValues() =>
        Assert.Equal(5, Reader.Verify(Path.Combine(AppContext.BaseDirectory, "../../../../../data")));

    [Fact]
    public void EveryMessageTypeIsGenerated() => Assert.Equal(ExpectedMessages, AllMessages().Count());

    [Theory]
    [MemberData(nameof(MessageNames))]
    public void EveryMessageRoundTripsWithAllFieldsSet(string name)
    {
        var d = AllMessages().Single(m => m.Name == name);
        Assert.Equal("Siso.Spacefom.V1." + name, d.ClrType.FullName);
        var original = d.Parser.ParseFrom(ByteString.Empty);
        Fill(original);
        Assert.Equal(d.Fields.InDeclarationOrder().Count, CountSet(original));
        var decoded = d.Parser.ParseFrom(original.ToByteArray());
        Assert.Equal(original, decoded);
    }

    [Fact]
    public void Enums()
    {
        Assert.Equal(new[] { 0, 1, 2, 3, 4 }, Enum.GetValues<ExecutionMode>().Select(v => (int)v));
        Assert.Equal(0, (int)MTRMode.Unspecified);
        Assert.Equal(new[] { 0, 2, 3, 4 }, Enum.GetValues<MTRMode>().Select(v => (int)v));
    }

    [Fact]
    public void OptionalPresence()
    {
        Assert.False(new ReferenceFrame().HasParentName);
        var frame = new ReferenceFrame { ParentName = "" };
        Assert.True(ReferenceFrame.Parser.ParseFrom(frame.ToByteArray()).HasParentName);
    }
}
