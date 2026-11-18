# Time in SpaceFOM data

SpaceFOM data is only meaningful at the instant it describes, so the bridge has to carry time out of the federation as carefully as it carries positions. Sources are SISO-STD-018-2020, the pinned FOM XML ([`fom/SOURCE.json`](../fom/SOURCE.json), TrickHLA commit `1677fd0`) and the TrickHLA code at the same commit.

## Contents

- [Three kinds of time](#three-kinds-of-time)
- [What the schema carries today](#what-the-schema-carries-today)
- [Unit and epoch of the time tag](#unit-and-epoch-of-the-time-tag)
- [What the schema does not carry](#what-the-schema-does-not-carry)
- [The bridge and HLA time management](#the-bridge-and-hla-time-management)
- [Several bridges](#several-bridges)
- [Open questions](#open-questions)

## Three kinds of time

| Time | What it is | Representation | Source |
|---|---|---|---|
| Time stamp | The HLA logical time for which an update is valid. Federates pass it as a parameter of the HLA services, and updates are sent in time stamp order (TSO) unless the SpaceFOM says otherwise | `HLAinteger64Time`, microseconds since the start of the federation execution | §4.3.2 (p. 36); Rules 4-8, 4-9 (p. 44) and 4-26 (p. 47); FOM `<time>` ([`SISO_SpaceFOM_datatypes.xml` L55–64][xml-time]) |
| Time tag | The simulated physical time, in the Terrestrial Time (TT) scale, that a state refers to. It is part of the data | `Time` (`HLAfloat64LE`, unit `second (s)`) in the `time` field of `SpaceTimeCoordinateState` | §5.4.3.1 (p. 55); Rule 4-10 (p. 44); [`SISO_SpaceFOM_datatypes.xml` L149–155][xml-time-type], [L370–373][xml-stc-time] |
| CTE time | Time from Central Timing Equipment, which keeps real-time federates (for example hardware in the loop) on a common, highly accurate clock | Defined per federation in the FESFA | §7.1.1.2.2 (p. 66); `ExecutionConfiguration.next_mode_cte_time` (§7.1.3, p. 67) |

The standard asks every federate to send the time tag even when it uses HLA time management, so that federates which do not use it can still tell when the data was valid. Its example is a plotting federate that is neither time regulating nor time constrained (§4.3.2, p. 36; §5.4.3.1, p. 55). A consumer outside HLA is in the same position as that plotting federate.

## What the schema carries today

- The time tag of every state: `ReferenceFrame.state`, `PhysicalEntity.state` and `DynamicalEntity.state` are `SpaceTimeCoordinateState`, whose field `time` is the time tag ([`datatypes.proto` L174–188](../proto/siso/spacefom/v1/datatypes.proto#L174-L188)). It travels in the same message as the position, velocity and attitude it belongs to.
- The execution times in `ExecutionConfiguration`: `scenario_time_epoch`, `next_mode_scenario_time` and `next_mode_cte_time` as `double`, and `least_common_time_step` as `int64` microseconds ([`management.proto` L32–64](../proto/siso/spacefom/v1/management.proto#L32-L64)).

The conversion is exact. `HLAfloat64LE` becomes a Protobuf `double` and `HLAinteger64Time` becomes an `int64` ([mapping](technical-overview.md#mapping)), so both sides hold the same 64-bit value: the bridge only changes the byte layout, and a consumer receives exactly the value the federate sent.

## Unit and epoch of the time tag

The FOM gives the unit of `Time` as seconds. Rule 4-10 says time tags are expressed "in the TT scale using the Truncated Julian Date (TJD) format", and §4.3.4.2 defines TJD as a count of days from 1968-05-24 00:00:00. Read alone, the two look inconsistent.

TrickHLA reconciles them by counting seconds from the TJD origin:

- `SpaceTimeCoordinateData::time` is documented as `trick_units{s}`, "Truncated Julian date in TT time scale" ([`SpaceTimeCoordinateData.hh` L53][thla-stc]).
- The scenario timeline epoch is "TT time standard represented in Truncated Julian Date format (TJD) expressed in seconds" ([`ScenarioTimeline.hh` L13–14][thla-st-hh]).
- The value sent is that epoch plus the elapsed simulation time ([`ScenarioTimeline.cpp` L98–101][thla-st-cpp]), assigned to the state before each send ([`PhysicalEntity.cpp` L189][thla-pe], [`RefFrameState.cpp` L162][thla-rf]).

The standard's description of `scenario_time_epoch` points the same way: TT "using the Truncated Julian Date (TJD) origin (1968-05-24 00:00:00 UTC) as the TT epoch" (§7.1.3, p. 67).

So in SpaceFOM 1.0 the time tag is seconds of TT since the TJD origin. The generated comment says only `Time: second (s)`, because that is all the FOM's `<units>` gives; the epoch is not in the schema. SpaceFOM 2.0 plans an updated epoch (2000) and configurable time resolution ([SpaceFOM 2.0 changes](technical-overview.md#spacefom-20-changes-the-generator-must-follow)). After that change the same `double` will mean something different, so a consumer has to know which epoch applies. How the schema should state it is [Q12](../proposal/open-questions.md#time).

## What the schema does not carry

- The HLA time stamp of an update. It is a parameter of the HLA service call, not an attribute, so it is not in the FOM and the generator cannot produce a field for it. A consumer that needs time stamp order, or has to line up data from several sources, needs it. An envelope message around each update could carry it, together with the instance name and a removal marker: see [what the schema does not carry](technical-overview.md#what-the-schema-does-not-carry) and [Q9](../proposal/open-questions.md#schema-design).
- A CTE time per update. The FOM has no such attribute; CTE appears only in `next_mode_cte_time`.

## The bridge and HLA time management

Nothing here is built yet; the bridge is planned in the [demo plan](plans/docker-demo-plan.md). The proposed design:

- Time constrained: A federate must be time constrained to receive TSO data in order (Rule 4-25, p. 47), and SpaceFOM updates are sent TSO (Rule 4-26). The bridge then gets each update in order, with its time stamp, and can pass the time stamp on once the schema has a place for it (Q9).
- Not time regulating: Only time-regulating federates hold back the advance of logical time: "the slowest time regulating federate will determine the rate at which all other time constrained federates will run" (Rule 3-11 rationale, p. 31). A bridge that does not regulate cannot slow the federation, the Pacing Federate or hardware on a CTE clock. If it falls behind, only its own output is late, and that delay is measured.
- Execution control: The bridge still joins the SpaceFOM initialization and the `mtr_run` and `mtr_freeze` synchronization points ([#34](https://github.com/gsantopaolo/spacefom2-protobuf/issues/34)).
- Observation only: data on the bus serves tools outside HLA: analysis, recording, digital twins. A device that must react in real time inside a control loop stays a federate.

Whether the PDG agrees with this time management choice is [Q13](../proposal/open-questions.md#time). The demo will test it on Portico before the design is fixed.

## Several bridges

When one bridge cannot keep up, several bridges can split the subscriptions, by object class or with HLA Data Distribution Management regions. Their outputs then have to be merged in time order. A proposed way:

- every message carries the HLA time stamp (the envelope of Q9) and the TT time tag;
- each bridge regularly publishes a "complete up to time T" marker, taken from the time advance grants it receives;
- a consumer merges the streams in time stamp order and knows that it has all data up to the smallest T across the bridges.

Stream processors call these markers watermarks. The demo will test the idea; nothing is built yet.

## Open questions

- [Q9](../proposal/open-questions.md#schema-design): how a consumer learns the instance, the HLA time stamp and the removal of an instance.
- [Q12](../proposal/open-questions.md#time): how the schema should state the unit and epoch of the time tag.
- [Q13](../proposal/open-questions.md#time): which HLA time management the reference bridge should use.

[xml-time]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L55-L64
[xml-time-type]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L149-L155
[xml-stc-time]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L370-L373
[thla-stc]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/include/SpaceFOM/SpaceTimeCoordinateData.hh#L53
[thla-st-hh]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/include/TrickHLA/time/ScenarioTimeline.hh#L13-L14
[thla-st-cpp]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/source/TrickHLA/time/ScenarioTimeline.cpp#L98-L101
[thla-pe]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/source/SpaceFOM/PhysicalEntity.cpp#L189
[thla-rf]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/source/SpaceFOM/RefFrameState.cpp#L162
