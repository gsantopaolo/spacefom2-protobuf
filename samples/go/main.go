// Command reader decodes the shared sample data and checks every value
// (see samples/README.md).
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"google.golang.org/protobuf/proto"

	pb "github.com/gsantopaolo/spacefom2-protobuf/samples/generated/go/siso/spacefom/v1"
)

func dataDir() string {
	_, file, _, _ := runtime.Caller(0)
	return filepath.Join(filepath.Dir(file), "..", "data")
}

type checkError string

func (e checkError) Error() string { return string(e) }

func load(name string, m proto.Message) {
	b, err := os.ReadFile(filepath.Join(dataDir(), name+".binpb"))
	if err != nil {
		panic(checkError(err.Error()))
	}
	if err := proto.Unmarshal(b, m); err != nil {
		panic(checkError(err.Error()))
	}
}

func check(ok bool, what string) {
	if !ok {
		panic(checkError(what))
	}
}

// verify checks every value in the shared data and returns the number of
// messages checked.
func verify() (count int, err error) {
	defer func() {
		if r := recover(); r != nil {
			if ce, ok := r.(checkError); ok {
				err = ce
				return
			}
			panic(r)
		}
	}()
	root := &pb.ReferenceFrame{}
	load("reference_frame_root", root)
	check(root.GetName() == "RootFrame", "root frame name")
	check(root.ParentName != nil && root.GetParentName() == "", "root parent_name present and empty")

	child := &pb.ReferenceFrame{}
	load("reference_frame_child", child)
	check(child.GetParentName() == "RootFrame", "child parent_name")
	check(child.GetState().GetTranslationalState().GetPosition().GetX() == 1.4959787e11, "child position.x")
	check(child.GetState().GetRotationalState().GetAngularVelocity().GetZ() == 7.2921159e-5, "child angular_velocity.z")

	entity := &pb.DynamicalEntity{}
	load("dynamical_entity", entity)
	check(entity.GetName() == "Lander1", "entity name")
	check(entity.GetMass() == 15000.0, "entity mass")
	check(len(entity.GetInertia()) == 9 && entity.GetInertia()[4] == 2000.0, "entity inertia")
	check(entity.GetState().GetTime() == 1.5, "entity state.time")
	check(entity.Force != nil && entity.GetForce().GetX() == 100.5, "entity force")
	check(entity.Torque == nil, "entity torque absent")

	config := &pb.ExecutionConfiguration{}
	load("execution_configuration", config)
	check(config.GetCurrentExecutionMode() == pb.ExecutionMode_EXEC_MODE_RUNNING, "current_execution_mode")
	check(config.GetNextExecutionMode() == pb.ExecutionMode_EXEC_MODE_FREEZE, "next_execution_mode")
	check(config.GetLeastCommonTimeStep() == 250000, "least_common_time_step")

	mtr := &pb.ModeTransitionRequest{}
	load("mode_transition_request", mtr)
	check(mtr.GetExecutionMode() == pb.MTRMode_MTR_GOTO_FREEZE, "MTR execution_mode")

	b, err := proto.Marshal(entity)
	check(err == nil, "marshal")
	again := &pb.DynamicalEntity{}
	check(proto.Unmarshal(b, again) == nil && proto.Equal(again, entity), "round trip")
	return 5, nil
}

func main() {
	count, err := verify()
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL go:", err)
		os.Exit(1)
	}
	fmt.Printf("OK go: %d messages checked\n", count)
}
