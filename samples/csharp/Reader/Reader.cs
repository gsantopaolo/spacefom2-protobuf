// Decode the shared sample data and check every value (see samples/README.md).
using Google.Protobuf;
using Siso.Spacefom.V1;

public static class Reader
{
    static T Load<T>(string data, MessageParser<T> parser, string name) where T : IMessage<T> =>
        parser.ParseFrom(File.ReadAllBytes(Path.Combine(data, name + ".binpb")));

    static void Check(bool ok, string what)
    {
        if (!ok) throw new InvalidDataException(what);
    }

    static int Main(string[] args)
    {
        try
        {
            var count = Verify(args.Length > 0 ? args[0] : "../data");  // run from samples/csharp
            Console.WriteLine($"OK csharp: {count} messages checked");
            return 0;
        }
        catch (InvalidDataException e)
        {
            Console.Error.WriteLine($"FAIL csharp: {e.Message}");
            return 1;
        }
    }

    /// <summary>Checks every value in the shared data; returns the number of messages checked.</summary>
    public static int Verify(string data)
    {
        var root = Load(data, ReferenceFrame.Parser, "reference_frame_root");
        Check(root.Name == "RootFrame", "root frame name");
        Check(root.HasParentName && root.ParentName == "", "root parent_name present and empty");

        var child = Load(data, ReferenceFrame.Parser, "reference_frame_child");
        Check(child.ParentName == "RootFrame", "child parent_name");
        Check(child.State.TranslationalState.Position.X == 1.4959787e11, "child position.x");
        Check(child.State.RotationalState.AngularVelocity.Z == 7.2921159e-5, "child angular_velocity.z");

        var entity = Load(data, DynamicalEntity.Parser, "dynamical_entity");
        Check(entity.Name == "Lander1", "entity name");
        Check(entity.Mass == 15000.0, "entity mass");
        Check(entity.Inertia.Count == 9 && entity.Inertia[4] == 2000.0, "entity inertia");
        Check(entity.State.Time == 1.5, "entity state.time");
        Check(entity.Force != null && entity.Force.X == 100.5, "entity force");
        Check(entity.Torque == null, "entity torque absent");

        var config = Load(data, ExecutionConfiguration.Parser, "execution_configuration");
        Check(config.CurrentExecutionMode == ExecutionMode.ExecModeRunning, "current_execution_mode");
        Check(config.NextExecutionMode == ExecutionMode.ExecModeFreeze, "next_execution_mode");
        Check(config.LeastCommonTimeStep == 250000L, "least_common_time_step");

        var mtr = Load(data, ModeTransitionRequest.Parser, "mode_transition_request");
        Check(mtr.ExecutionMode == MTRMode.MtrGotoFreeze, "MTR execution_mode");

        var again = DynamicalEntity.Parser.ParseFrom(entity.ToByteArray());
        Check(again.Equals(entity), "round trip");
        return 5;
    }
}
