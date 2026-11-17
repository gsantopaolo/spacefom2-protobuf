# Open questions for the SpaceFOM 2.0 PDG

The decisions this proposal needs from the PDG. Answers will be recorded here as they arrive.

## Contents

- [Process](#process)
- [Scope and status](#scope-and-status)
- [Sources and licence](#sources-and-licence)
- [Naming and hosting](#naming-and-hosting)
- [Demo](#demo)

## Process

**Q1. Which PCR form should the proposal use?**
The [draft PCR](pcr-draft.md) follows the Problem/Change Request form in Appendix A of SISO-ADM-003, *SISO Balloted Products Development and Support Process*. The copy found is the 2011 edition. Is that form still in use for SpaceFOM 2.0, or does the PSG/PDG use a newer version or its own format? If there is a current template, please share it.

## Scope and status

**Q2. Which FOM modules should the mapping cover?**
The generator currently maps all four SISO modules: datatypes, environment, entity and management, including the `ExecutionConfiguration` object class and the `ModeTransitionRequest` interaction. Should the published schema cover all of them, or start with the environment and entity data only?

**Q3. Informative or normative?**
Should the Protobuf representation start as an informative annex of SpaceFOM 2.0 and possibly become normative later, or does the PDG prefer another status?

## Sources and licence

**Q4. Which FOM XML is authoritative?**
The generator reads the SpaceFOM 1.0 FOM modules from the nasa/TrickHLA repository (`FOMs/SpaceFOM`), pinned to a commit in [`fom/SOURCE.json`](../fom/SOURCE.json). Does the PDG consider that the authoritative source, or is there an official SISO distribution of the XML to use instead, including for the SpaceFOM 2.0 drafts?

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
