# Open questions for the SpaceFOM 2.0 PDG

The decisions this proposal needs from the PDG. Answers will be recorded here as they arrive.

## Contents

- [Process](#process)
- [Scope and status](#scope-and-status)
- [Sources and licence](#sources-and-licence)
- [Naming and hosting](#naming-and-hosting)
- [Demo](#demo)
- [Schema design](#schema-design)
- [Time](#time)

## Process

**Q1. Which PCR form should the proposal use, and which group receives it?**
The [draft PCR](pcr-draft.md) follows the Problem/Change Request form in Appendix A of SISO-ADM-003, *SISO Balloted Products Development and Support Process*. The copy found is the 2011 edition. Is that form still in use for SpaceFOM 2.0, or does the PSG/PDG use a newer version or its own format? If there is a current template, please share it. The form's instructions say to submit it "to the Product Support Group" ([SISO-ADM-003-2011, page A-3](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/admin_products_/siso-adm-003-2011_ew_changes.pdf#page=56)), but SpaceFOM 2.0 is being developed by the PDG. Should the PCR go to the SpaceFOM PSG, to the PDG, or to both?

## Scope and status

**Q2. Which FOM modules should the mapping cover?**
The generator currently maps all four SISO modules: datatypes, environment, entity and management, including the `ExecutionConfiguration` object class and the `ModeTransitionRequest` interaction. Should the published schema cover all of them, or start with the environment and entity data only?

**Q3. Informative or normative?**
Should the Protobuf representation start as an informative annex of SpaceFOM 2.0 and possibly become normative later, or does the PDG prefer another status?

## Sources and licence

**Q4. Which FOM XML is authoritative?**
The generator reads the SpaceFOM 1.0 FOM modules from the nasa/TrickHLA repository (`FOMs/SpaceFOM`), pinned to a commit in [`fom/SOURCE.json`](../fom/SOURCE.json). Does the PDG consider that the authoritative source, or is there an official SISO distribution of the XML to use instead, including for the SpaceFOM 2.0 drafts? The TrickHLA copy is not word for word what the standard prints. In the `PhysicalEntity` semantics, for example, the XML says "Space FOM entity hierarchy" and "(see 6.2.2)" ([`SISO_SpaceFOM_entity.xml` L68–70](https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_entity.xml#L68-L70)), where Appendix C of SISO-STD-018-2020 says "SpaceFOM entity hierarchy" and "(see Section 5.2.2)" ([page 133](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=133)).

**Q5. Does the `<semantics>` text count as Schema or as Documentation?**
Every FOM module carries SISO's copyright notice with two grants: "Schema and API" (any purpose, with the attribution "Reprinted with permission from SISO Inc.") and "Documentation" (non-commercial purposes only). The generator copies the `<semantics>` text verbatim into `.proto` comments. Which grant covers that text? And can the generated `.proto` files, with the SISO attribution, be published in an MIT-licensed open-source repository, or is permission from the SISO Board needed? Until this is answered, the generator can leave the text out with a flag.

## Naming and hosting

**Q6. What should the official package names and versioning be?**
The schema uses the Protobuf package `siso.spacefom.v1`. The samples use `org.siso.spacefom.v1` for Java and `Siso.Spacefom.V1` for C# as placeholders; SISO has not approved them. Which names should be used per language, and how should releases of the `.proto` files line up with SpaceFOM versions?

**Q7. Would SISO or the PDG host the repositories?**
Today the schema, generator, CI and samples in six languages live in one personal repository. The [reference repository proposal](reference-repository.md) recommends keeping it that way during discussion and, if the PDG adopts the schema, moving to repositories in an organisation SISO or the PDG controls, with admin rights handed over. Would the PDG want to host them, and is there already an organisation or place where SISO publishes material like this? And who should review and merge changes to the schema once it is hosted there?

## Demo

**Q8. What would make the demo convincing?**
The roadmap ends with a Docker Compose demo that runs a whole SpaceFOM federation: a generator of simulated data (for example a vehicle's state and sensor readings) publishes into the federation, the bridge carries the data out as Protobuf, and tools outside HLA consume it.

- Which scenario: a generic one, or one the PDG already knows, such as the sample federates shipped with [nasa/TrickHLA](https://github.com/nasa/TrickHLA/tree/master/sims/SpaceFOM) or a SEE scenario?
- Which RTI does the PDG use, and can one run freely in containers for a public demo?
- Should the demo also show the inbound direction (outside tool → Protobuf → HLA), which the current design does not cover?
- The existing SpaceFOM federates need a commercial RTI: TrickHLA builds only against Pitch or MAK ([`S_hla.mk` L55–76](https://github.com/nasa/TrickHLA/blob/c7bce7d63857642d964dd464471f6c120d003853/makefiles/S_hla.mk#L55-L76)). A public, one-command demo would therefore run on the open-source Portico RTI with a small publisher federate written for it ([draft plan](../docs/plans/docker-demo-plan.md)). Could the PDG or a member provide an RTI licence for a second, private demo that runs the same bridge against TrickHLA's SpaceFOM federates?

## Schema design

**Q9. How does a consumer know which object instance an update belongs to, and when it happened?**
Each object class maps to a message whose fields are all optional, and a partial attribute update maps to a partial message ([mapping](../docs/technical-overview.md#mapping)). The schema has no place for the object instance an update belongs to, its HLA time stamp, or the removal of an instance. The `name` attribute does not fill the gap: it is Static ([`SISO_SpaceFOM_entity.xml` L74–76](https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_entity.xml#L74-L76)), so a partial update does not carry it. One option is an envelope message around each update, with the instance name, the object class, the HLA logical time and a marker for a removed instance. Another is a bridge that caches the last value of every attribute and always sends the full state; that carries `name`, but still not the time stamp or the removal. Which does the PDG prefer, or is there a better way? The time side of this question is covered in [time in SpaceFOM data](../docs/time.md).

**Q10. Should each 9-element matrix type become its own message?**
The FOM defines three `HLAfixedArray` types of 9 elements: `InertiaMatrix`, `Matrix` and `InertiaRateMatrix` (`SISO_SpaceFOM_datatypes.xml` [L266–272](https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L266-L272), [L280–286](https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L280-L286), [L301–307](https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L301-L307)). The generator writes each attribute of these types as a `repeated double`, with the array type's semantics as a comment. In SpaceFOM 1.0 two attributes use them: `DynamicalEntity.inertia` (field 14) and `DynamicalEntity.inertia_rate` (field 15); no attribute uses `Matrix`. A message per matrix type, for example `message InertiaMatrix { repeated double elements = 1; }`, would keep the type name and give the attribute presence, which a `repeated` field cannot have. It would also change fields 14 and 15 of `DynamicalEntity` on the wire, so the choice must be made before the schema is published. Until then the generator keeps `repeated double`. Which form does the PDG prefer?

**Q11. Should the schema cover FOM modules beyond the four SISO files?**
The generator reads only the four SISO modules and rejects any file not named `SISO_SpaceFOM_<key>.xml` ([`parse.py` L26](https://github.com/gsantopaolo/spacefom2-protobuf/blob/baeda12/generator/spacefom_proto/parse.py#L26)). Projects keep much of their own data in extension modules, and a tool builder may want to run the generator on those. Should the generator and the published schema also cover such modules, or stay limited to the SISO modules (see also Q2)?

## Time

Background for both questions: [time in SpaceFOM data](../docs/time.md).

**Q12. How should the schema state the unit and epoch of the time tag?**
The FOM gives `Time` in seconds ([`SISO_SpaceFOM_datatypes.xml` L149–155](https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L149-L155)), while Rule 4-10 asks for TT "using the Truncated Julian Date (TJD) format", and TJD is defined in days (§4.3.4.2). TrickHLA sends seconds of TT since the TJD origin ([details](../docs/time.md#unit-and-epoch-of-the-time-tag)). The generated comment says only `Time: second (s)`, and the epoch is not in the schema. SpaceFOM 2.0 plans an epoch of 2000 and a configurable time resolution, after which the same `double` means something different. Should the 2.0 FOM state the epoch in the `<units>` or `<semantics>` of `Time`, so the generator can copy it, or should the schema carry it another way, for example as a custom option or in the package version?

**Q13. Which HLA time management should the reference bridge use?**
The proposed bridge is time constrained, so it receives updates in time stamp order with their time stamps (Rules 4-25 and 4-26), and not time regulating, so it cannot hold back the federation, the Pacing Federate or real-time equipment on a CTE clock (Rule 3-11) ([details](../docs/time.md#the-bridge-and-hla-time-management)). Does the PDG agree, and are there federations, for example with hardware in the loop, where a bridge would need a different setup?
