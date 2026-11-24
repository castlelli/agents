---
name: domain-driven-design
description: "DDD theory specialist grounded in Eric Evans's Domain-Driven Design (2003). Use to explain DDD concepts in depth, or to theory-check a modeling or strategic decision before committing to it."
---

# Evans DDD — theory specialist

Grounded in *Domain-Driven Design: Tackling Complexity in the Heart of Software*, Eric Evans (final manuscript, April 2003; 5 parts, 17 chapters). Chapter numbers match the printed edition. The `p.` numbers here are manuscript pages.

## Jobs

1. **Explain** a DDD concept so it sticks. The reader is a practitioner who has *used* DDD but has not studied its theory.
2. **Theory-check** a decision or strategy: does it hold up against what Evans argues, and under which conditions?

Not this skill's job: writing CONTEXT.md, ADRs or PRDs. Hand that to the project's domain-docs skill if one exists (for example `domain-modeling`). Generic architecture advice unrelated to the domain model is also out of scope. When a check produces a decision worth recording, say so and hand it off.

## Ground rules

- **Source discipline.** Tag every substantive claim with its origin: *Evans (ch N)* for the book, *later DDD* for anything after 2003 (see Canon boundary). Never attribute a later idea to Evans. When Evans is silent, say so. When unsure, write "I'm not certain Evans covers this" rather than guess.
- **Exact pattern names.** Use ANTICORRUPTION LAYER, not "adapter layer". Use CONFORMIST, not "downstream client".
- **Paraphrase.** Quote only short phrases, never long passages.
- **Forces before patterns.** Every pattern in the book answers a named problem. Explain and judge from the problem, not the pattern.
- **Evans is pragmatic, not purist.** He accepts SMART UI when circumstances warrant it, and says teams choose CONFORMIST less often than they probably should. He warns against elaborate modeling outside the CORE. A check that only ever answers "add more DDD" is a wrong check.
- **Context decides.** A verdict depends on:
  - team size and organization
  - control over the other systems
  - whether the area is CORE
  - how well the domain is understood

  Ask for a missing fact only if it would flip the verdict. Otherwise state the assumption and proceed.
- Answer in the user's language.

## Theory-check protocol

Use this when the user proposes or questions a decision. Examples: "should X be its own aggregate?", "do we share this model with team B?", "is this a domain service?", "is this our core?".

1. **Restate** the decision in the project's ubiquitous language. Classify it as one of:
   - *tactical*: building blocks inside one model
   - *strategic*: context boundaries and relationships, distillation, large-scale structure
   - *process*: who models, and how knowledge flows
2. **Name the forces.** What problem does the decision solve, and what does it cost? Examples: invariant enforcement vs. contention; integration value vs. coordination cost.
3. **Locate the patterns** in play and run the matching rules below.
4. **Look at the model, not only the code.** This is Evans's recurring move. A problem that shows up as technical (locking, translation pain, a bloated service) is usually rooted in the model. Ask whether a missing or implicit concept would dissolve it (ch 9).
5. **Give a verdict:**
   - **Sound**: consistent with Evans; name the rule it satisfies.
   - **Sound if…**: valid under conditions; name the conditions.
   - **Risky**: defensible, but a named force is ignored; say what will hurt, and when.
   - **Contradicts Evans**: breaks a pattern's core rule; name the rule and the failure mode Evans describes.
6. **Say what would change the verdict.** Name the fact that would flip it, and the cheapest way to find it out: a scenario talked through out loud, a test, or a question for the domain expert.
7. **Canon note.** Only if later DDD would answer differently, say how, with that label.

Output shape:

```
Decision: …
Level: tactical | strategic | process
Forces: …
Patterns in play: …
Verdict: Sound | Sound if … | Risky | Contradicts Evans   (confidence: high/medium/low)
Why (Evans, ch N): …
Would change if: …        Cheapest check: …
Beyond the book: …        (only when relevant)
```

## Explain protocol

For "what is X", "why X", or "when X":

1. The problem it solves, in one or two sentences.
2. Evans's solution, paraphrased from the pattern.
3. What it looks like in real code and teams. Connect it to what a practitioner has likely already done without the name.
4. The misreading to avoid (see Common misreadings).
5. What it feeds, and what it depends on.
6. When *not* to use it.
7. A chapter pointer, so the user can read the source.

Lead with the short answer. Go deeper on request, or when the concept carries a decision the user is making.

## The spine of the book

**Premises (Preface).** For most projects, the primary focus should be the domain and domain logic. Complex domain designs should be based on a model.

**What a model does (Part I).** It shapes the core of the design. It is the backbone of the team's language. It is distilled knowledge.

### Part I — Putting the domain model to work

- **Knowledge crunching (ch 1).** Developers and domain experts iterate on a model together, discarding what doesn't matter. The PCB story lists the ingredients:
  - bind model and implementation early
  - build a language on the model
  - keep the model knowledge-rich (behavior and rules, not a data schema)
  - distill it
  - brainstorm and experiment

  Modeling goes beyond "find the nouns": policies and rules are domain concepts too. Projects leak knowledge when people leave, so the code and the model must carry it.
- **UBIQUITOUS LANGUAGE (ch 2).** Make the model the backbone of one language. Use it relentlessly in speech, writing, diagrams and code. A change in the language is a change in the model: rename the code to follow it. Settle term confusion in conversation. Experts object to awkward terms; developers watch for ambiguity.
  - *Modeling out loud*: talk through scenarios in model terms; an easier phrasing points to a better model.
  - Documents complement code and conversation, never duplicate the code.
  - Keep diagrams small and selective (3–5 objects).
  - Explanatory models that are not software models are fine for teaching.
- **MODEL-DRIVEN DESIGN (ch 3).** One model serves both analysis and design, and the code reflects it literally. If the model can't be implemented naturally, find another model. If it doesn't express the domain, find another model. Evans rejects a separate analysis model: it gets abandoned and the insight is lost.
- **HANDS-ON MODELERS (ch 3).** Anyone who contributes to the model touches code. Anyone who changes code learns to express the model through it. Refactoring code *is* changing the model. A separate, hands-off modeler loses the feel for implementation constraints, and the model decays into a data structure.

### Part II — Building blocks

Details are under Tactical rules. In short: LAYERED ARCHITECTURE isolates the domain. ENTITIES, VALUE OBJECTS and SERVICES express the model. MODULES organize it. AGGREGATES, FACTORIES and REPOSITORIES manage object lifecycles. There are three ways to tame associations:
- impose a traversal direction
- add a qualifier to reduce multiplicity
- remove associations that aren't essential

### Part III — Refactoring toward deeper insight

- **Levels of refactoring.** Micro-refactorings and refactoring to design patterns continue as usual. The level with the most impact is refactoring toward a *deeper model*: driven by domain insight, carried out through micro-refactorings.
- **Deep model.** A lucid expression of the experts' primary concerns, with superficial aspects dropped. In shipping, the model moved from ships and containers to vessel voyages, bills of lading and transfers of legal responsibility. A deep model is not necessarily abstract.
- **Breakthrough (ch 8).** It comes after many modest refactorings, and it is a big shift; take it when it's feasible. Don't freeze while waiting for one. Push the predictable levers instead: crunch knowledge, build the language, make concepts explicit, supple design, distill.
- **Making implicit concepts explicit (ch 9).** Five techniques:
  - listen to language
  - scrutinize awkwardness
  - contemplate contradictions
  - read the book (the domain's own literature)
  - try, try again

  Less obvious kinds of concept: explicit constraints; processes as domain objects (only if the experts talk about the process); SPECIFICATION.
- **Supple design (ch 10).**
  - INTENTION-REVEALING INTERFACES: names say effect and purpose, not mechanism.
  - SIDE-EFFECT-FREE FUNCTIONS: separate commands from queries; move complex logic into VALUE OBJECTS.
  - ASSERTIONS: state post-conditions and invariants; test them.
  - CONCEPTUAL CONTOURS: cut along the axes of change that refactoring reveals.
  - STANDALONE CLASSES: every dependency is suspect.
  - CLOSURE OF OPERATIONS.
  - Declarative style, used with caution.
  - Carve off subdomains; draw on established formalisms.
- **Analysis patterns (ch 11)** are knowledge to start from, not code to paste. **Design patterns in the model (ch 12)**: STRATEGY (aka POLICY) and COMPOSITE belong in the model when they express a domain concept, not as technical tricks.
- **When to refactor (ch 13):**
  - the design no longer expresses the team's current understanding
  - an important concept is implicit and you see how to make it explicit
  - an important part could be made suppler

  Don't refactor the day before a release. Don't show off technique. Don't build a "deeper model" the experts wouldn't use.

### Part IV — Strategic design: three complementary principles

1. **BOUNDED CONTEXT.** The least obvious principle and the most fundamental: a model must be consistent inside an explicit boundary.
2. **Distillation.** Find the CORE DOMAIN and invest in it. Everything else plays a supporting role.
3. **Large-scale structure.** A system-wide language of roles and rules, so any part can be understood in terms of the whole.

**Assessment First (ch 17).** Before any strategic work:
1. Draw a CONTEXT MAP. Is it consistent, or ambiguous?
2. Is there a UBIQUITOUS LANGUAGE, and is it rich enough to help?
3. Is the CORE identified? Could you write a DOMAIN VISION STATEMENT?
4. Does the technology work for or against MODEL-DRIVEN DESIGN?
5. Do the developers have the technical skills?
6. Do they know the domain, and do they care about it?

## Tactical rules (Part II)

**Layers (ch 4).** Four layers:
- **User interface.**
- **Application:** thin. It coordinates tasks and delegates to domain objects. It holds no business rules and no business state, though it may track task progress.
- **Domain:** the model, business state and rules.
- **Infrastructure.**

Dependencies point downward. Upward communication goes through callbacks or OBSERVERS. SMART UI is legitimate for simple applications and teams without modeling skill. It is a one-way door, though: there is no path to MODEL-DRIVEN DESIGN without a rewrite.

**ENTITY vs VALUE OBJECT (ch 5)**

| Ask | ENTITY | VALUE OBJECT |
|---|---|---|
| Does the domain care *which one*, across time and state? | yes: a thread of identity | no: only *what* it is |
| Equality | by identity; the model must define "the same thing" | by attributes |
| Change | changes over its lifecycle | immutable; replaced whole |
| Design focus | keep it lean (identity + lifecycle); move other attributes to associated objects | a conceptual whole (WHOLE VALUE); rich, side-effect-free behavior |

- The answer depends on context. Address is a VALUE for a mail-order company and an ENTITY for a postal service or a utility.
- A VALUE may reference ENTITIES: a route references cities.
- If two VALUES seem to need a bidirectional link, an identity was probably missed.
- Identity is a meaning imposed because it's useful. Choose the identifying operation deliberately, external or system-generated.

**SERVICE (ch 5).** Only for a significant domain operation that doesn't naturally belong to an ENTITY or VALUE. A good service has three marks:
- it relates to a domain concept that is not a natural part of an ENTITY or VALUE
- its interface uses model elements
- it is stateless

Name it as a verb from the ubiquitous language, and don't let services strip ENTITIES and VALUES of their behavior. The layer test:
- funds transfer with debit/credit rules → domain service
- export to a spreadsheet → application service
- sending an email → infrastructure service

**MODULES (ch 5).** Choose them for conceptual cohesion, so they tell the domain's story. Their names enter the ubiquitous language. Refactor modules as the model changes; most teams never do. When conceptual clarity and technical coupling conflict, choose clarity. Don't package the domain by pattern (an "entities" folder, a "services" folder).

**Mixing paradigms (ch 5).** Don't fight the implementation paradigm. Lean on the ubiquitous language. Be skeptical of extra machinery such as rules engines: is it pulling its weight?

**AGGREGATE (ch 6).** A cluster treated as one unit for data changes, with a root ENTITY and a boundary. It marks the scope where invariants must hold when every transaction completes. Evans's rules, condensed:
1. The root has global identity and is ultimately responsible for checking invariants. Inner entities have local identity only.
2. Nothing outside holds a reference inside, except to the root. Inner objects may be handed out for one operation. Copies of VALUES are free.
3. Only roots are fetched directly by query; everything else is reached by traversal.
4. Inner objects *may* hold references to other roots. (This is the 2003 position; later DDD prefers references by identity.)
5. A delete removes everything inside the boundary.
6. When any change inside commits, all of the aggregate's invariants hold.

Rules that span aggregates are *not* expected to be up to date at every moment. They are resolved within a specified time, by events, batch jobs or other mechanisms. That is eventual consistency, stated before the term existed.

How to draw the boundary:
- find the true invariants, and what business practice creates and deletes together
- weigh contention (how many users touch it) and how often things change
- keep high-contention points loose and strict invariants tight

**FACTORY (ch 6).** Move complex creation of objects and aggregates into a separate element. Create a whole aggregate in one atomic step that satisfies its invariants, without the client naming concrete classes. A factory method on the root is fine. A plain public constructor is the better choice when all of these hold:
- the class is the type (no interesting hierarchy or polymorphism)
- the client cares about the implementation
- the client has all the attributes
- construction is simple

A factory that reconstitutes stored objects doesn't assign a new identity. It can't just refuse on a broken invariant the way creation can; it has to handle it.

**REPOSITORY (ch 6).** Gives the illusion of an in-memory collection of every object of a type. It offers add/remove and selection by criteria, returning fully built objects. **Only for aggregate roots that need direct access.** It keeps clients focused on the model and makes persistence swappable (an in-memory fake for tests). Queries can be hard-coded or SPECIFICATION-based; summaries such as counts and sums are allowed. A FACTORY makes new objects; a REPOSITORY finds existing ones.

**Relational databases (ch 6).**
- If the database is the object store, keep schema and model close: a transparent mapping with the same names. Denormalize if that simplifies the mapping.
- Outside processes should not write to it. They bypass invariants and freeze the schema.
- If the data belongs to a legacy or external system, there are really two models; see ch 14.

**SPECIFICATION (ch 9–10).** A predicate VALUE OBJECT: does this object satisfy the criteria? Three uses: *validation*, *selection* (querying), and *building-to-order* (generating objects). Specifications combine with AND/OR/NOT and subsumption.

## Strategic rules (Part IV)

**BOUNDED CONTEXT (ch 14).** Explicitly define where a model applies: by team organization, by parts of the application, and by physical artifacts (code bases, database schemas). Keep the model strictly consistent inside. Don't worry about whether it applies outside. Inside a context, use **CONTINUOUS INTEGRATION**: frequent merges, automated tests, and relentless use of the language.

Signs that a context is splintering:
- **Duplicate concepts:** two model elements for one concept.
- **False cognates:** one term with two meanings, as in the "Charge" story.

Modules are not contexts. A module organizes one model, and separate namespaces can even hide divergence.

**CONTEXT MAP (ch 14).**
- Name every model in play, including the implicit models inside non-object systems, and put the names into the ubiquitous language.
- Describe each point of contact and its translation.
- Map the terrain *as it is*, and transform it later. Where things are unclear, "put a dragon on the map" and keep going.
- Don't change the map until reality has changed.
- Put automated tests at every contact point.

**Relationship patterns.** Choose using three variables: your control over the other model, how well the teams cooperate and communicate, and how much integration is needed.

| Pattern | Use when | Costs and risks |
|---|---|---|
| Single BC + CONTINUOUS INTEGRATION | a team of fewer than ~10 on tightly related work | CI gets hard as the team grows |
| SHARED KERNEL | two closely coordinating teams, a valuable overlap, full CI too costly | kernel changes need consultation; both teams' tests run; deployment coordination is heavy |
| CUSTOMER/SUPPLIER DEVELOPMENT TEAMS | one-way dependency; upstream has a reason to serve downstream (works best under shared management) | downstream needs go into upstream planning; joint acceptance tests run in upstream's suite |
| CONFORMIST | upstream won't help, the dependency is indispensable, and upstream's model is usable | you're limited to upstream's model plus additions; commit fully or not at all; unappealing, so under-chosen |
| ANTICORRUPTION LAYER | the dependency is indispensable, but upstream's model is poor or incompatible, or you're building a major new model | a complex translation layer (FAÇADE + ADAPTER + translators) that can grow into software of its own |
| SEPARATE WAYS | integration pays little; features are merely related in a use case | duplicated effort; no shared language |
| OPEN HOST SERVICE | many consumers integrate with you | define a coherent protocol; handle one team's odd needs with a one-off translator |
| PUBLISHED LANGUAGE | a documented interchange language (an industry standard or your own) | the interchange language is not your model; don't adopt it by default |

**External systems.**
1. First ask whether SEPARATE WAYS is enough. Would giving users access to both systems do?
2. If integration is essential, choose between two options:
   - **CONFORMIST**, when your app is a peripheral extension of a dominant system with a large interface.
   - **ANTICORRUPTION LAYER**, when you're building more than an extension, the interface is small, or the other system is badly designed.
3. Don't assume a legacy system is one coherent context. Check it for internal contradictions.

**System under design.**
- One context for a team of fewer than ~10 on tightly related functionality.
- As the team grows: a SHARED KERNEL, or split off contexts of fewer than ~10 each. Use CUSTOMER/SUPPLIER where dependencies run one way.
- When two groups' modeling clashes irreconcilably: SEPARATE WAYS, with a translation layer both teams maintain.
- As a rule, one team per context.

**Boundary forces.**
- *Favoring larger contexts:*
  - user tasks flow more smoothly
  - one model is easier to understand than two plus a mapping
  - translation can be hard or impossible
  - a shared language helps communication
- *Favoring smaller contexts:*
  - less communication overhead
  - easier CI
  - large contexts need versatile abstract models, and the skills are scarce
  - specialized user groups get their own dialects
- Deep integration across contexts is impractical. Translation only covers what can be stated rigorously in the other model.
- Team politics often decide the relationship. Say so, instead of dressing it up as purely technical.
- Separate models for "special needs" can become a justification for any quirky, parochial model. Weigh how much the group's jargon is actually worth.
- Deployment feeds back into boundaries. A SHARED KERNEL burdens every release; a translation layer contains the impact; SEPARATE WAYS is simplest.
- **On a project already underway:**
  1. Map the contexts as they actually are.
  2. Tighten CI inside them.
  3. Move stray translation code into ANTICORRUPTION LAYERS.
  4. Name the contexts.
  5. Only then change boundaries, in small steps.

  Splitting a context is easy; merging contexts or changing a relationship is hard. Ch 14 gives step-by-step plans for SEPARATE WAYS → SHARED KERNEL, SHARED KERNEL → CI, phasing out a legacy system, and OPEN HOST SERVICE → PUBLISHED LANGUAGE.

**Distillation (ch 15)**

- **CORE DOMAIN.**
  - Find it, make it small, and make it easy to tell apart from everything else.
  - Put your best people on it: strong developers with domain experts, in a stable team.
  - Keep everything else as generic as practical, off-the-shelf where appropriate.
  - Justify any other investment by how it supports the core.

  What counts as core depends on the application: money is generic for most apps and core for currency trading. The core can rarely be bought or outsourced, because the knowledge has to stay with the team.
- **Priority rule.** Between two worthwhile refactorings, pick the one that touches the CORE. In pain-driven work, if the root cause involves the core or its link to a supporting part, fix it first.
- **First slice.** Unless the team has proven skills in a familiar domain, the first end-to-end system should exercise part of the CORE. A peripheral slice only reduces technical risk.
- **GENERIC SUBDOMAINS.** Cohesive areas that are not why the project exists. Factor them into generic models with no trace of your specialty. Four options, each with trade-offs: off-the-shelf, a published model, outsourcing, or building in-house. *Generic doesn't mean reusable.* Don't design for code reuse, but do keep industry-specific concepts out.
- **Escalating techniques**, from cheapest to most demanding:
  1. DOMAIN VISION STATEMENT: about one page, the core's value proposition, written early.
  2. HIGHLIGHTED CORE: a distillation document of 3–7 sparse pages, or flags on core elements.
  3. Separating GENERIC SUBDOMAINS and COHESIVE MECHANISMS.
  4. SEGREGATED CORE.
  5. ABSTRACT CORE.
- **COHESIVE MECHANISM.** A conceptually coherent computation (a graph traversal, a formalism) pulled into a lightweight framework behind an intention-revealing interface. "An expressive model proposes; a mechanism disposes." Keep mechanisms out of the core, unless the algorithm itself is proprietary value.
- **SEGREGATED CORE.** Repackage the core concepts and cut away supporting responsibilities, even if that breaks other cohesive packages.
- **ABSTRACT CORE.** When interactions between subdomains dominate, move the polymorphic core interfaces into a package of their own.

**Large-scale structure (ch 16)**

- Use it only when needed. A small team can manage with good MODULES, some distillation and informal coordination.
- **EVOLVING ORDER.** Let the structure change with the application, even into a different kind of structure. Don't over-constrain detailed decisions.
- The options, from loosest to most restrictive:
  1. **SYSTEM METAPHOR.** Adopt one only if it emerges naturally and actually guides the work. Metaphors carry baggage, and few projects find a good one.
  2. **RESPONSIBILITY LAYERS.** Layers set by the rate and source of change. Example layers: Potential, Operations, Decision Support, Policy, Commitment. Keep to 4–5 layers at most. Lower layers never depend on higher ones; they signal upward through events.
  3. **KNOWLEDGE LEVEL.** Objects that describe and constrain other objects, for user-configurable rules. Use it sparingly: it can turn the people who configure it into meta-programmers.
  4. **PLUGGABLE COMPONENT FRAMEWORK.** An ABSTRACT CORE in a SHARED KERNEL hub. Evans says it should be "not the first" large-scale structure on a project, "nor the second"; build it only after several mature applications exist.
- Every structural rule must make development easier. Keep the structure minimal, and resist building frameworks to enforce it.

**Who sets strategy (ch 17).** Strategic decisions must reach the whole team, absorb feedback, and allow evolution. The strategy team must not take all the best developers, and must stay minimal and humble. Good forms: structure that emerges from application teams, with a hands-on arbiter; or a customer-focused architecture team that works alongside developers. Never an ivory tower. "Objects are specialists; developers are generalists."

## Tells and smells

| If you see… | It probably means… | Ch |
|---|---|---|
| A term everyone says that appears nowhere in the code | a missing concept | 9 |
| Two teams using one word differently | a false cognate; split or unify explicitly | 14 |
| One concept implemented twice, with sync code | a duplicate concept; the context is splintering | 14 |
| Business rules in UI handlers, SQL or scripts | the domain isn't isolated | 4 |
| `*Manager` / `*Helper` classes doing domain work | a SERVICE, or a missing concept, disguised as an object | 5, 9 |
| Services hold all the logic; entities are data bags | behavior stripped from ENTITIES and VALUES | 5 |
| Lock contention or huge transactions | aggregates drawn around data, not invariants | 6 |
| Repositories for non-root entities | aggregate rules broken | 6 |
| Tangled conditionals encoding a rule the experts name | an explicit constraint, SPECIFICATION or POLICY | 9, 12 |
| Each new requirement adds complexity to the same spot | awkwardness; dig for the concept | 9 |
| Translation code scattered through the codebase | a missing ANTICORRUPTION LAYER, or an unclear map | 14 |
| "We'll just reuse their model/table" across teams | an unexamined relationship; pick a pattern | 14 |
| Best developers on infrastructure, core left to juniors | distillation failure | 15 |
| A generic subdomain full of your industry's terms | core leaking into generic | 15 |
| Architecture rules no application team follows | an ivory-tower structure | 16, 17 |
| The model diagram and the code disagree | MODEL-DRIVEN DESIGN is broken | 3 |

## Common misreadings

- **"Bounded context = microservice, module, or subdomain."** For Evans, a context is a boundary of *model consistency*, defined by team, usage and artifacts. Modules organize inside one model. Deployment is a separate concern. Subdomains (CORE/GENERIC) are about value and focus (ch 15); contexts are about model integrity (ch 14). They often line up, but they don't have to.
- **"DDD = the building blocks."** The language and strategic design come first; the building blocks serve MODEL-DRIVEN DESIGN. Part IV calls BOUNDED CONTEXT the most fundamental principle.
- **"Unify on one enterprise model."** Evans argues against full unification in large systems.
- **"Ubiquitous language = a glossary."** The language lives in speech and code. A glossary that never changes the code isn't the language.
- **"An aggregate is the object graph you load together."** It is a consistency boundary for invariants and change. It is not a read model or an ORM convenience.
- **"Every rule needs a SERVICE."** Services are only for operations that don't fit any ENTITY or VALUE.
- **"Generic subdomains should be built reusable."** Evans explicitly says not to design them for reuse.
- **"Apply DDD everywhere."** Rich modeling belongs in the CORE. SMART UI and CONFORMIST are legitimate choices elsewhere.
- **"An anticorruption layer is just an API client."** It translates concepts between two models; the transport is incidental.

## Canon boundary: Evans 2003 vs later DDD

The book predates several terms that are now standard. Answer questions about them, but label them.

| Topic | Evans 2003 | Later DDD (label it) |
|---|---|---|
| Domain events | Not a building block. Events appear only as a mechanism: cross-aggregate updates, and layers signaling upward. | A named pattern in later writing, including Evans's own later reference material. Central to event-driven styles. |
| References between aggregates | Inner objects may hold references to other roots. | Common advice: refer to other aggregates by identity, keep aggregates small, change one aggregate per transaction (Vernon, *Implementing DDD*). |
| Consistency across aggregates | Resolved "within some specified time". | Named eventual consistency, usually implemented with domain events. |
| Subdomain types | CORE DOMAIN and GENERIC SUBDOMAINS; "supporting" is used only informally. | Core / supporting / generic as three formal categories. |
| Context relationships | The patterns in the table above. | Additions such as Partnership and Big Ball of Mud. |
| Collaborative discovery | Knowledge crunching, modeling out loud. | Event Storming, Domain Storytelling, context canvases. |
| Architecture | LAYERED ARCHITECTURE. | Hexagonal / ports and adapters, clean or onion architecture, CQRS, event sourcing. |
| Services and deployment | A context has deployment implications. | Microservices are often drawn along context lines. |

## Worked examples

- **Overbooking (ch 1).** The requirement "allow 10% overbooking" was buried in booking code as `capacity * 1.1`. It became an explicit Overbooking Policy that the booking code calls. Now the rule has a name the experts recognize, and it can vary (STRATEGY/POLICY, ch 12). Lesson: rules are domain concepts. But don't do this for every detail; distill.
- **Purchase order (ch 6).** The invariant: the sum of line items must not exceed the approved limit. Locking the order plus its parts caused contention, because parts are shared across orders. The fix came from business facts: part prices change less often, and a price change need not reach existing orders. So each line item keeps its own price, the aggregate is PO + line items, and Part stays outside. Lesson: the boundary came from facts about change and ownership, not from the object graph.
- **Charge (ch 14).** Two teams "reused" one Charge object: one meant billing customers, the other paying vendors. Phantom records and crashes followed. The fix was a Customer Charge and a Supplier Charge in separate models. Lesson: shared names without an explicit boundary create false cognates.
- **Funds transfer (ch 5).** The application service reads the request and decides to send a notification. The domain service performs debits and credits under ledger rules. The infrastructure service sends the email.
- **Syndicated loans (ch 15).** The strongest developer built an elegant generic commenting feature while the core Loan module rotted. The project nearly failed. Lesson: point your best people at the core.

## Chapter index

| Ch | Title | Key patterns and ideas | p. |
|---|---|---|---|
| 1 | Crunching Knowledge | knowledge crunching, knowledge-rich design, deep models | 15 |
| 2 | Communication and the Use of Language | UBIQUITOUS LANGUAGE, modeling out loud, documents and diagrams | 24 |
| 3 | Binding Model and Implementation | MODEL-DRIVEN DESIGN, HANDS-ON MODELERS | 37 |
| 4 | Isolating the Domain | LAYERED ARCHITECTURE, SMART UI | 51 |
| 5 | A Model Expressed in Software | associations, ENTITIES, VALUE OBJECTS, SERVICES, MODULES, paradigms | 60 |
| 6 | The Lifecycle of a Domain Object | AGGREGATES, FACTORIES, REPOSITORIES, relational databases | 88 |
| 7 | Using the Language: Cargo Shipping | the building blocks applied end to end | 115 |
| 8 | Breakthrough | the loan "Share Pie" breakthrough | 136 |
| 9 | Making Implicit Concepts Explicit | language, awkwardness, contradictions, constraints, processes, SPECIFICATION | 145 |
| 10 | Supple Design | INTENTION-REVEALING INTERFACES … CLOSURE OF OPERATIONS, declarative design | 170 |
| 11 | Applying Analysis Patterns | analysis patterns as starting knowledge | 207 |
| 12 | Relating Design Patterns to the Model | STRATEGY/POLICY, COMPOSITE | 218 |
| 13 | Bringing the Pieces Together | when to refactor, crisis as opportunity | 230 |
| 14 | Maintaining Model Integrity | BOUNDED CONTEXT, CONTINUOUS INTEGRATION, CONTEXT MAP, relationship patterns, choosing a strategy, transformations | 235 |
| 15 | Distillation | CORE DOMAIN, GENERIC SUBDOMAINS, VISION STATEMENT, HIGHLIGHTED/SEGREGATED/ABSTRACT CORE, COHESIVE MECHANISMS | 279 |
| 16 | Large-Scale Structure | EVOLVING ORDER, SYSTEM METAPHOR, RESPONSIBILITY LAYERS, KNOWLEDGE LEVEL, PLUGGABLE COMPONENT FRAMEWORK | 307 |
| 17 | Bringing the Strategy Together | Assessment First, who sets the strategy | 339 |

## Topic index

ABSTRACT CORE 15 · AGGREGATE 6 · analysis patterns 11 · ANTICORRUPTION LAYER 14 · ASSERTIONS 10 · associations 5 · Assessment First 17 · breakthrough 8 · BOUNDED CONTEXT 14 · CLOSURE OF OPERATIONS 10 · COHESIVE MECHANISMS 15 · COMPOSITE 12 · CONCEPTUAL CONTOURS 10 · CONFORMIST 14 · constraints 9 · CONTEXT MAP 14 · CONTINUOUS INTEGRATION 14 · CORE DOMAIN 15 · CUSTOMER/SUPPLIER 14 · declarative design 10 · deep model 1, 8 · deployment 14 · documents and diagrams 2 · DOMAIN VISION STATEMENT 15 · duplicate concepts 14 · ENTITY 5 · EVOLVING ORDER 16 · explanatory models 2 · FACTORY 6 · false cognates 14 · GENERIC SUBDOMAINS 15 · HANDS-ON MODELERS 3 · HIGHLIGHTED CORE 15 · INTENTION-REVEALING INTERFACES 10 · invariants 6, 10 · KNOWLEDGE LEVEL 16 · knowledge crunching 1 · LAYERED ARCHITECTURE 4 · legacy phase-out 14 · MODEL-DRIVEN DESIGN 3 · modeling out loud 2 · MODULES 5 · OPEN HOST SERVICE 14 · paradigms 5 · PLUGGABLE COMPONENT FRAMEWORK 16 · processes as objects 9 · PUBLISHED LANGUAGE 14 · refactoring targets 15 · relational databases 6 · REPOSITORY 6 · RESPONSIBILITY LAYERS 16 · SEGREGATED CORE 15 · SEPARATE WAYS 14 · SERVICE 5 · SHARED KERNEL 14 · SIDE-EFFECT-FREE FUNCTIONS 10 · SMART UI 4 · SPECIFICATION 9, 10 · STANDALONE CLASSES 10 · strategic design roles 17 · STRATEGY/POLICY 12 · SYSTEM METAPHOR 16 · UBIQUITOUS LANGUAGE 2 · VALUE OBJECT 5 · when to refactor 13

## Glossary (after Evans's own)

- **Aggregate:** objects treated as one unit for data changes. Outside references go only to the root, and consistency rules apply inside the boundary.
- **Bounded context:** the limit within which one model applies, so everyone knows what must be consistent and how it relates to other contexts.
- **Context map:** the contexts in play and the actual relationships between them.
- **Core domain:** the distinctive part of the model, central to the users' goals, that makes the application valuable.
- **Deep model:** an incisive expression of the experts' main concerns, without superficial aspects or naive readings.
- **Distillation:** separating the essence from the mixture so it becomes more valuable and useful.
- **Domain expert:** someone with deep knowledge of the subject, not just any user.
- **Entity:** an object defined by continuity and identity rather than its attributes.
- **Factory:** encapsulates complex creation and hides the concrete type from clients.
- **Function:** an operation that returns a result without observable side effects.
- **Implicit concept:** a concept needed to understand the model but never named in it.
- **Invariant:** an assertion that is always true, except during transient states (mid-method, or an uncommitted transaction).
- **Large-scale structure:** high-level concepts and rules that set a pattern for the whole system, so it can be discussed in broad strokes.
- **Model:** a system of abstractions describing selected aspects of a domain, used to solve problems in it.
- **Model-driven design:** some software elements correspond closely to model elements, and model and code evolve together.
- **Repository:** a globally accessible way to find stored objects, emulating a collection.
- **Service:** an operation offered as a standalone interface in the model, with no encapsulated state.
- **Standalone class:** a class that can be understood and tested with only primitives and basic libraries.
- **Strategic design:** decisions that apply to large parts of the system, made at team level.
- **Supple design:** a design that puts a deep model's power in client developers' hands and is easy to reshape with new insight.
- **Ubiquitous language:** the language built on the model and used by everyone on the team, connecting all their work to the software.
- **Unification:** internal consistency of a model: every term is unambiguous and no rules contradict each other.
- **Value object:** an object that describes a characteristic and has no identity.
- **Whole value:** an object modeling one complete concept.