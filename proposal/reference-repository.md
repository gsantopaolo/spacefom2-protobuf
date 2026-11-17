# Proposal: a reference repository for SpaceFOM 2.0 Protobuf

**Proposed by** Gian Paolo Santopaolo · 17 November 2026 · for the SISO SpaceFOM 2.0 PDG, as a follow-up to the [one-page pitch](pitch.md)

## Purpose

Background for [Q7 in the open questions](open-questions.md#naming-and-hosting): where the schema, the generator and the multi-language samples should live if the PDG adopts them, and who maintains them.

## What exists today

Everything is in one repository, [gsantopaolo/spacefom2-protobuf](https://github.com/gsantopaolo/spacefom2-protobuf):

- `generator/` reads the SpaceFOM 1.0 FOM modules and writes `.proto` files, with field numbers kept stable in a lock file.
- `proto/siso/spacefom/v1/` holds the generated schema, one file per FOM module.
- `fom/SOURCE.json` pins the FOM modules to a commit of [nasa/TrickHLA](https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM). That is where the XML is distributed today; no SISO-hosted copy is used.
- A GitHub Actions workflow regenerates the schema when the FOM or the generator changes, checks it with `protoc` and `buf`, and opens a pull request with the result.
- In progress: `samples/`, with generated code and a small reader program in C++, Python, Java, C#, TypeScript and Go. All six decode the same data file in CI, which shows that one federate's data can be read in any of those languages. Later: the bridge federate and a Docker Compose demo.

## Options

**A. One repository (current state).** Schema, generator, samples, bridge and demo live together. A schema change and the matching sample changes land in the same pull request, so they cannot drift apart. The cost is that users who want only the schema also get toolchains for six languages.

**B. Two repositories.**
- A *schema* repository: FOM-derived `.proto` files, generator, lock file and CI. It publishes versioned releases, such as `v1.0.0` for SpaceFOM 1.0 and a new major version for SpaceFOM 2.0.
- A *reference implementation* repository: language bindings, samples, the bridge federate and the demo. It pins a schema release and is updated by pull request when a new release appears.

Google's public APIs are organised this way: the `.proto` definitions are in [googleapis/googleapis](https://github.com/googleapis/googleapis), and the [Cloud Client Libraries](https://cloud.google.com/apis/docs/cloud-client-libraries) that use them are documented and published separately. Users depend on the schema, and the code built on it evolves on its own schedule.

**C. Like B, but hosted by SISO or the PDG.** The repositories would sit in an organisation that SISO or the PDG controls, so the schema is clearly the product's and not one contributor's. This also settles the package names. The samples currently use `org.siso.spacefom.v1` for Java as a placeholder, and that name should only be used with SISO's agreement.

## Recommendation

Keep option A while the proposal is under discussion: it is faster to change, and the PDG can review one place. If the PDG adopts the schema, move to option C. I can do the split and hand over admin rights.

## Decisions needed

The decisions this depends on (hosting, licence, authoritative FOM source, package names, review and release process) are Q4 to Q7 in the [open questions](open-questions.md).
