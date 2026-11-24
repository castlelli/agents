---
name: design-patterns
description: "Teach, explain, disambiguate, critique or apply the 23 GoF design patterns and their underlying principles — in software, and transferred to hardware, pipelines or process design."
---

<!-- argument-hint: [pattern name, design problem, "which pattern for X", or chapter number] -->

# Design Patterns — GoF
**Authors**: Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides (1994) | **Pages**: ~417 | **Patterns**: 23

## Operating modes

Read the request and pick one. Do not blend them.

| Signal | Mode | Behaviour |
|---|---|---|
| "what is X", "explain X", "I don't get X" | **TEACH** | Force → naive attempt → pain → pattern → liability. See *Teaching protocol*. |
| "which pattern for…", "how do I make X pluggable", code/design shown | **APPLY** | Run the *Selection procedure*. Name the axis of change first. Recommend at most 2 patterns, and say when to use none. |
| "is this a Decorator or a Proxy?", "Strategy vs State" | **DISAMBIGUATE** | Intent decides, never structure. See *Confusable pairs*. |
| "review this design", "am I over-engineering" | **CRITIQUE** | Check against *Anti-patterns*. Speculative flexibility is a defect, not a virtue. |
| Non-software engineering context | **TRANSFER** | Map through the four principles, not through class diagrams. See *Transfer to other engineering*. |

**Governing rule, from the authors:** "A design pattern should only be applied when the flexibility it affords is actually needed." Patterns buy flexibility with indirection, and indirection costs performance, parts count, and comprehension. Never recommend one without stating what it costs.

---

## The four principles (Ch. 1)

Everything in the catalog is a named, worked-out application of these. When you cannot recall a pattern, reason from here.

1. **Encapsulate the concept that varies.** Find the one aspect of the design that will change independently of the rest, give it its own object/module/interface, and let everything else depend only on that interface. The catalog is organised by *what varies*; see the selection table.
2. **Program to an interface, not an implementation.** Commit to the set of requests an object answers, never to the class that answers them. Consequence: clients stay unaware of both the concrete types and the classes that implement them. The creational patterns exist precisely because you must name a concrete class *somewhere* — they confine that mention to one place.
3. **Favour object composition over class inheritance.** Inheritance is *white-box reuse*: compile-time, visible internals, "inheritance breaks encapsulation", the parent's changes force the child's. Composition is *black-box reuse*: run-time, swappable, dependent only on interfaces. The authors' own judgement: "designers overuse inheritance… designs are often made more reusable (and simpler) by depending more on object composition." Delegation is the extreme case — a receiver forwards a request to a delegate and passes itself along, which lets behaviour be recomposed at run-time.
4. **The run-time structure is not the code structure.** Code is a frozen taxonomy of classes; the running system is a shifting network of objects. Aggregation (owner, shared lifetime) and acquaintance (merely knows of, looser) look identical in source and mean very different things. Understanding one from the other is "like trying to understand the dynamism of living ecosystems from the static taxonomy of plants and animals." Patterns are largely *about* the run-time structure the code cannot show you.

**Class scope vs object scope.** Class patterns fix relationships at compile time via inheritance (Factory Method, Adapter-class, Interpreter, Template Method). Object patterns fix them at run time via composition — everything else. Object scope is the more flexible and more common answer.

---

## Selection procedure (APPLY mode)

Work in this order. Do not skip to step 4.

**1. State the force.** What is actually painful or expected to change? If nothing changes, no pattern is justified. Write one sentence: *"X must be able to vary without touching Y."*

**2. Match a cause of redesign** (Ch. 1.6 — the fastest route when the pain already exists):

| Cause of redesign | Patterns |
|---|---|
| Creating an object by naming a class explicitly | Abstract Factory, Factory Method, Prototype |
| Dependence on specific operations | Chain of Responsibility, Command |
| Dependence on hardware/software platform | Abstract Factory, Bridge |
| Dependence on object representations or implementations | Abstract Factory, Bridge, Memento, Proxy |
| Algorithmic dependencies | Builder, Iterator, Strategy, Template Method, Visitor |
| Tight coupling | Abstract Factory, Bridge, Chain of Responsibility, Command, Facade, Mediator, Observer |
| Extending functionality by subclassing (subclass explosion) | Bridge, Chain of Responsibility, Composite, Decorator, Observer, Strategy |
| Inability to alter a class conveniently (no source, or too many subclasses) | Adapter, Decorator, Visitor |

**3. Or match the aspect that should vary** (Table 1.2 — the route when designing ahead of the pain):

| Pattern | Aspect that can vary |
|---|---|
| Abstract Factory | families of product objects |
| Builder | how a composite object gets created |
| Factory Method | subclass of object that is instantiated |
| Prototype | class of object that is instantiated |
| Singleton | the sole instance of a class |
| Adapter | interface to an object |
| Bridge | implementation of an object |
| Composite | structure and composition of an object |
| Decorator | responsibilities of an object, without subclassing |
| Facade | interface to a subsystem |
| Flyweight | storage costs of objects |
| Proxy | how an object is accessed; its location |
| Chain of Responsibility | object that can fulfill a request |
| Command | when and how a request is fulfilled |
| Interpreter | grammar and interpretation of a language |
| Iterator | how an aggregate's elements are accessed and traversed |
| Mediator | how and which objects interact |
| Memento | what private information is stored outside an object, and when |
| Observer | number of objects depending on another; how they stay up to date |
| State | states of an object |
| Strategy | an algorithm |
| Template Method | steps of an algorithm |
| Visitor | operations applicable to objects without changing their classes |

**4. Check Applicability, then Consequences.** A pattern whose Applicability fits but whose liabilities you cannot pay is the wrong pattern. Say the liability out loud.

**5. Name participants in the domain's vocabulary.** Not `AbstractStrategy` — `TeXLayoutStrategy`, `MinimapAligner`, `PressureSensorAdapter`. The pattern name belongs in the class name only when it clarifies; never as decoration.

---

## The catalog

### Creational — who decides which concrete class exists

- **Abstract Factory** *(object)* — Provide an interface for creating families of related or dependent objects without specifying their concrete classes. **Use when** the system must be configured with one of several product families and members of a family must be used together. **Gains** isolation of concrete classes, one-line swap of the whole family, enforced consistency. **Costs** adding a *new kind of product* means changing the factory interface and every subclass. Often implemented with Factory Methods; the concrete factory is often a Singleton.
- **Builder** *(object)* — Separate the construction of a complex object from its representation, so the same construction process can create different representations. **Use when** the assembly algorithm must be independent of the parts and their assembly, and the same process must yield different representations. **Gains** step-by-step control, construction code isolated from representation, reusable directors. **Vs Abstract Factory**: Builder builds one complex object step by step and returns it at the end; Abstract Factory emphasises families and returns products immediately.
- **Factory Method** *(class)* — Define an interface for creating an object, but let subclasses decide which class to instantiate. **Use when** a class cannot anticipate the class of objects it must create, or wants subclasses to specify it. **Gains** a hook for subclasses; connects parallel class hierarchies (e.g. `Figure::CreateManipulator`). **Costs** clients may have to subclass the Creator *only* to get a different product. Usually called from Template Methods.
- **Prototype** *(object)* — Specify the kinds of objects to create using a prototypical instance, and create new objects by copying it. **Use when** classes to instantiate are decided at run time, or you would otherwise need a factory hierarchy parallel to the product hierarchy, or instances differ only by a few state combinations. **Gains** add/remove product kinds at run time; new "classes" defined by varying values or structure, with no programming; no Creator hierarchy at all. **Costs** every subclass must implement `Clone`, which is hard when the class has circular references or components that do not support copying.
- **Singleton** *(object)* — Ensure a class has exactly one instance and provide a global point of access. **Use when** there must be exactly one instance reachable from a well-known access point, and it should be extensible by subclassing without changing clients. **Gains** controlled access, no name-space pollution, refinable by subclassing, and — crucially — *easy to relax later* to N instances, unlike static/class methods. **Costs (say this every time):** it is a global in disguise. It hides dependencies from a module's signature, makes tests order-dependent and non-parallel, and fights concurrency. The book's own strongest argument for it is *reversibility*; if you do not need the subclassing or the instance-count control, prefer passing the dependency in.

**Creational discussion.** There are exactly two ways to parameterise a system by the classes it creates: *subclass the creator* (Factory Method — simple, but a new subclass per product, and changes cascade) or *compose with a creator object* (Abstract Factory, Builder, Prototype — more flexible, one more level of indirection). Abstract Factory and Prototype are competing answers; they can also combine, with a factory holding prototypes to clone.

### Structural — how objects and classes are composed

- **Adapter** *(class & object)* — Convert the interface of a class into another interface clients expect. **Use when** an existing class has the right behaviour and the wrong interface, or a reusable class must cooperate with classes it cannot know about. **Class adapter** commits to one concrete Adaptee, can override its behaviour, no extra indirection. **Object adapter** works with an Adaptee *and all its subclasses*, but overriding requires subclassing the adaptee. Applied *after* the design exists; the coupling was unforeseen.
- **Bridge** *(object)* — Decouple an abstraction from its implementation so the two can vary independently. **Use when** the implementation must be selected or switched at run time, both hierarchies must be extensible, changes to the implementation must not force client recompilation, or you see a "nested generalisation" class explosion (an abstraction × implementation cross-product). **Gains** run-time reconfiguration, independent extensibility, better layering, binary compatibility. Applied *up front*, unlike Adapter.
- **Composite** *(object)* — Compose objects into tree structures to represent part-whole hierarchies; let clients treat individual objects and compositions uniformly. **Use when** you want a part-whole hierarchy and clients that ignore the leaf/composite distinction. **Gains** recursive structures, simple clients (no tag-and-case code), new component types work with existing clients automatically. **Costs** you cannot use the type system to restrict what a composite may contain — run-time checks instead.
- **Decorator** *(object)* — Attach additional responsibilities to an object dynamically; a flexible alternative to subclassing for extending functionality. **Use when** responsibilities must be added and withdrawn per object at run time, or subclassing would explode combinatorially (`BorderedScrollableTextView`…), or the class cannot be subclassed. **Gains** pay-as-you-go features, mix-and-match, the same decorator applied twice. **Costs** a decorated object is *not identical* to the component — never rely on object identity; and you get "lots of little objects that all look alike," easy to customise and hard to debug.
- **Facade** *(object)* — Provide a unified interface to a set of interfaces in a subsystem, defining a higher-level interface that makes the subsystem easier to use. **Use when** a complex subsystem needs a simple default view, when client↔implementation dependencies are many, or to define an entry point per layer. **Gains** fewer objects for clients, weak coupling, fewer compilation dependencies, easier porting. **Note** it does not *prevent* access to subsystem classes — ease of use and generality both stay available. It defines a new interface; it adds no new functionality; subsystem classes do not know it exists.
- **Flyweight** *(object)* — Use sharing to support large numbers of fine-grained objects efficiently. **Use only when all hold:** many objects; storage cost driven by sheer quantity; most state can be made *extrinsic*; many objects collapse into few once extrinsic state is removed; the application does not depend on object identity. **Gains** savings that grow with sharing, greatest when extrinsic state can be *computed* instead of stored. **Costs** run-time cost of finding/transferring/computing extrinsic state. Split state honestly: *intrinsic* = shareable, context-free; *extrinsic* = context-dependent, passed in.
- **Proxy** *(object)* — Provide a surrogate or placeholder for another object to control access to it. **Four kinds:** *remote* (local stand-in for an object in another address space), *virtual* (create expensive objects on demand), *protection* (enforce access rights), *smart reference* (reference counting, lazy loading, lock checking). Same interface as the subject. Enables copy-on-write. **Costs** a level of indirection on every access.

**Structural discussion.** *Adapter makes things work after they are designed; Bridge makes them work before they are.* Composite, Decorator and Proxy share a structure and differ entirely in intent: Composite is about **representation** (treat many as one), Decorator about **embellishment** (open-ended responsibilities, recursive), Proxy about **access control** (one fixed relationship, statically expressible). A Facade is not an Adapter: an adapter reuses an existing interface, a facade defines a new one.

### Behavioral — how responsibility and control are distributed

- **Chain of Responsibility** *(object)* — Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle it; pass the request along the chain. **Use when** several objects may handle a request and the handler is not known a priori, or the handler set is configured dynamically. **Gains** reduced coupling — each object knows only its successor — and responsibilities reassignable at run time. **Costs** *receipt is not guaranteed*: a request can fall off the end of the chain unhandled. Best when the chain already exists in the structure (e.g. a Composite's parent links).
- **Command** *(object)* — Encapsulate a request as an object, letting you parameterise clients with different requests, queue or log requests, and support undoable operations. **Use when** you need callbacks as objects, deferred or queued execution, undo (`Unexecute` + history list), a crash-recovery log, or transactions. **Gains** invoker decoupled from performer; commands are first-class and composable (a MacroCommand is a Composite); new commands need no change to existing classes.
- **Interpreter** *(class)* — Given a language, define a representation for its grammar plus an interpreter that uses the representation to interpret sentences. **Use only when** the grammar is *simple* and efficiency is *not* critical. **Gains** grammar rules as classes, so grammar changes by inheritance; node classes are easy to write and often generable. **Costs** one class per grammar rule — complex grammars become unmaintainable; use a parser generator instead. The AST is a Composite; add new interpretations with a Visitor.
- **Iterator** *(object)* — Provide a way to access the elements of an aggregate sequentially without exposing its underlying representation. **Use when** you need multiple traversal orders, multiple simultaneous traversals, or one uniform traversal interface across different aggregate structures. **Gains** traversal swappable by swapping the iterator; the aggregate interface stays small; more than one traversal can be pending at once.
- **Mediator** *(object)* — Define an object that encapsulates how a set of objects interact, keeping them from referring to each other explicitly. **Use when** a set of objects communicates in well-defined but tangled ways, reuse is blocked by many references, or distributed behaviour needs customising without subclassing everywhere. **Gains** many-to-many becomes one-to-many; colleagues decoupled and reusable; the interaction protocol becomes a first-class, studiable thing. **Costs** it **centralises control** — "trades complexity of interaction for complexity in the mediator," which can itself become a monolith.
- **Memento** *(object)* — Without violating encapsulation, capture and externalise an object's internal state so it can be restored later. **Use when** a snapshot must be saved and a direct state-access interface would expose implementation details. **Gains** encapsulation boundaries preserved; the Originator is simplified because clients hold what they asked for. **Costs** can be expensive if state is large or snapshots are frequent; the wide/narrow interface split is hard to enforce in some languages; the caretaker cannot see how much storage it is holding.
- **Observer** *(object)* — Define a one-to-many dependency so that when one object changes state, all its dependents are notified and updated automatically. **Use when** two aspects must vary independently, a change requires updating an unknown number of objects, or an object must notify others without knowing who they are. **Gains** abstract, minimal coupling — the subject knows only a list conforming to one interface, so subject and observers may sit in different layers; broadcast; observers added/removed at any time. **Costs** *unexpected updates*: an innocuous change can cascade, and the bare update protocol says nothing about *what* changed, forcing observers to deduce it. Poorly defined dependency criteria cause spurious updates that are hard to trace.
- **State** *(object)* — Allow an object to alter its behaviour when its internal state changes; the object appears to change its class. **Use when** behaviour depends on state at run time, or operations carry large multipart conditionals on a state enum, repeated across several operations. **Gains** state-specific behaviour localised per class, new states added by new subclasses; transitions become **explicit and atomic** (rebinding one variable) instead of scattered assignments; stateless State objects can be shared as flyweights, often Singletons. **Costs** more classes; less compact than one class — worth it only when there are enough states to make the conditionals ugly.
- **Strategy** *(object)* — Define a family of algorithms, encapsulate each one, and make them interchangeable. **Use when** related classes differ only in behaviour, you need algorithm variants with different space/time trade-offs, an algorithm uses data clients should not see, or a class's operations are thick with behaviour-selecting conditionals. **Gains** eliminates the conditionals; algorithm varies independently of context; client picks its trade-off. **Costs** **clients must know how the strategies differ** to choose — so use it only when the variation is relevant to clients; interface shared by trivial and complex strategies means some parameters go unused (communication overhead); more objects.
- **Template Method** *(class)* — Define the skeleton of an algorithm in an operation, deferring some steps to subclasses, without changing the algorithm's structure. **Use when** invariant parts should be written once and variable parts left to subclasses, common behaviour should be factored out of subclasses ("refactoring to generalise"), or extensions must be permitted *only* at controlled points. **Gains** the fundamental code-reuse technique of class libraries; inverted control — the **Hollywood Principle**, "Don't call us, we'll call you." **Discipline:** state explicitly which operations are *hooks* (may be overridden, default often empty) and which are *abstract* (must be). Minimise the number of primitive operations a subclass must override.
- **Visitor** *(object)* — Represent an operation to be performed on the elements of an object structure; define a new operation without changing the classes of the elements. **Use when** many distinct, unrelated operations must run over a structure of differing classes and you do not want to pollute those classes, **and the element hierarchy is stable while operations keep being added.** **Gains** new operations are cheap; related behaviour gathered in one visitor and unrelated behaviour separated; can visit objects with *no common parent class*, unlike an Iterator; accumulates state across the traversal. **Costs** adding a ConcreteElement class forces a change to every visitor — the exact inverse trade-off; and it usually forces elements to expose internal state, **breaking encapsulation**. If the element hierarchy changes often, put the operations in the elements instead.

**Behavioral discussion.** The common theme is **encapsulating variation**: a Strategy object encapsulates an algorithm, a State object a state-dependent behaviour, a Mediator a protocol, an Iterator a traversal. Command and Memento are *tokens* passed around and invoked later — Command is polymorphic, Memento's interface is so narrow it is passed as a value.

**Decoupling senders from receivers — four trade-offs.** *Command*: the binding lives in a separate object, so senders are reusable; nominally one subclass per connection. *Observer*: loosest binding, many receivers, count varies at run time; best when the dependency is a **data** dependency. *Mediator*: indirect reference through one router; centralises, may need its own dispatch scheme, which costs type safety. *Chain of Responsibility*: good when the chain already exists structurally and any of several objects might handle the request; same type-safety cost, plus no delivery guarantee.

---

## Confusable pairs (DISAMBIGUATE mode)

Answer with **intent**, then note the structural giveaway. Structure alone never decides.

| Pair | Decider |
|---|---|
| Adapter vs Bridge | Adapter fixes an **incompatibility discovered after the fact**; Bridge is designed **in advance** so abstraction and implementation evolve separately. After vs before. |
| Adapter vs Decorator | Adapter gives a **different** interface; Decorator keeps the **same** interface and adds responsibilities (so Decorator composes recursively, Adapter does not). |
| Adapter vs Facade | Adapter **reuses an existing** interface for existing classes; Facade **defines a new** interface over a subsystem. |
| Decorator vs Proxy | Decorator: the component provides part of the behaviour and decorators furnish the rest, open-ended, recursive. Proxy: the subject provides the behaviour and the proxy grants or refuses **access**, one fixed relationship. |
| Decorator vs Composite | Composite = **representation** (treat many as one); Decorator = **embellishment** (a degenerate composite with one child, but the intent is not aggregation). |
| Decorator vs Strategy | "A decorator changes the **skin** of an object; a strategy changes its **guts**." |
| Strategy vs State | Strategy: client picks an algorithm; the object has **many** strategies for different requests. State: the object has **one** current state and the states drive their own transitions; the object appears to change class. |
| Strategy vs Template Method | Strategy varies the **whole** algorithm by **delegation** (run time). Template Method varies **steps** of a fixed skeleton by **inheritance** (compile time). |
| Mediator vs Facade | Facade's protocol is **unidirectional** (facade → subsystem), adds no behaviour, subsystem is unaware. Mediator's protocol is **multidirectional** and it *adds* cooperative behaviour colleagues cannot provide; colleagues know the mediator. |
| Mediator vs Observer | Competing. Observer **distributes** the constraint between subjects and observers (more reusable, harder to follow). Mediator **centralises** it (easier to follow, harder to reuse, risks a monolith). |
| Abstract Factory vs Builder | Family emphasis, product returned immediately — vs — step-by-step construction, product returned at the end. |
| Abstract Factory vs Prototype | Subclass-free instance registration at run time (Prototype) vs a factory class per family (Abstract Factory). Prototype needs `Clone` on every product; Abstract Factory needs a factory hierarchy. |
| Visitor vs adding a method | Visitor only when **elements are stable and operations churn**. Reverse the answer if the element hierarchy churns. |
| Composite vs Chain of Responsibility | Not rivals — a Composite's parent link is a natural successor chain. |

---

## Teaching protocol (TEACH mode)

Use the authors' own template as the scaffold, in this order, and never open with the solution:

1. **The force.** A concrete situation where something must change independently of something else. Ask for the learner's own domain if they have one — a pattern taught in the learner's material is remembered; one taught in `AbstractWidgetFactory` is not.
2. **The naive design,** honestly built. Usually: a `switch` on a type tag, a subclass per combination, or a direct reference between two things.
3. **The pain,** made concrete. "Now add a third X." Count the files you must touch. The pattern must be *earned* by pain the learner has felt.
4. **The pattern.** Intent verbatim first (the authors' wording is precise — "Define a family of algorithms, encapsulate each one, and make them interchangeable," not "use different algorithms"), then participants named in the domain, then a minimal code sketch.
5. **Applicability**, as a checklist the learner tests their own situation against.
6. **Consequences — both columns.** An explanation that omits the liability has taught a cargo cult. End here, not at step 4.
7. **Where it sits in the web.** One or two relations: what it competes with, what it combines with.

**Calibration.** Two to four patterns per session, chosen for contrast (Strategy vs Template Method teaches more than Strategy alone). Prefer one worked example carried across patterns — the book uses a document editor (Lexi) for exactly this reason — over twenty one-liners.

**When to say the quiet part:** many GoF patterns are workarounds for the limits of 1994-era C++ and Smalltalk. In a language with first-class functions, closures and generics, Strategy, Command, Template Method and Factory Method often collapse into "pass a function" or "pass a type parameter"; Iterator is a language feature; Prototype is a `copy` method; Singleton is a module. **The forces are permanent; the class machinery is not.** Teach the force, present the machinery as one implementation of it, and say which language features subsume it. This is the difference between teaching design and teaching 1994.

---

## Transfer to other engineering (TRANSFER mode)

**A pattern transfers only when its forces transfer.** Before mapping, check three things: is there a real axis of variation; is there a cost to coupling across it; can an interface be specified stably? If not, the analogy is decoration — say so and stop. Watch the cost asymmetry: in software, indirection costs nanoseconds and readability; in hardware, a connector, a failure mode, and a BOM line; in a process, a handoff and a delay. The transferred principle is real; the transferred *cheapness* is not.

**The principles, restated domain-neutrally**

| Software form | General engineering form |
|---|---|
| Encapsulate what varies | Isolate the axis of change behind a specified boundary — a connector, a file format, a protocol, an SOP |
| Program to an interface | Specify by contract and tolerance, never by vendor, part number, or implementation |
| Composition over inheritance | Prefer assemblies of independently specified modules over deep specialisation of one design |
| Run-time ≠ compile-time structure | The schematic is not the running system; the org chart is not the workflow |

**Worked mappings**

- **Embedded / hardware.** HAL = **Bridge** (the abstraction outlives the MCU family). Sensor drivers to one reading interface = **Adapter**. Board-support package selecting a whole family of peripheral drivers = **Abstract Factory**. Interrupt vector dispatch down a handler list = **Chain of Responsibility**. Memory-mapped register shim with lock/bounds checks = **Proxy** (protection + smart reference). ISR publishing to subscribed tasks = **Observer**. A boot sequence with fixed phases and board-specific hooks = **Template Method**. A finite state machine in a protocol stack = **State** — and this is the one place where the pattern's "one class per state" often loses to a table-driven FSM, because code size is the binding constraint.
- **Scientific pipelines / bioinformatics.** Interchangeable aligners or assemblers behind one stage interface = **Strategy**. Parsers for FASTA/FASTQ/SAM/VCF normalising to one record type = **Adapter**. A workflow DAG whose nodes are steps or nested sub-workflows treated alike = **Composite**. A pipeline skeleton with fixed phases and overridable steps = **Template Method** (this is what Nextflow and Snakemake actually are). Millions of records sharing one immutable annotation/alphabet object, with position passed in = **Flyweight** (intrinsic = the shared reference data; extrinsic = per-read coordinates). A genome index loaded on first access = **virtual Proxy**. Several analyses over one stable tree or graph structure = **Visitor** — and its trade-off is exactly right here: phylogeny node types are stable, analyses are not. Checkpointing a long run for restart = **Memento**. Re-runnable, loggable analysis steps = **Command**.
- **Mechanical / manufacturing / civil.** A standardised tool-holder or mounting interface = **Bridge**. A fixture that mates a non-standard part to standard equipment = **Adapter**. Sub-assemblies treated as parts in a BOM = **Composite**. A QA gate sequence where the first applicable check rejects = **Chain of Responsibility**. One control panel over a complex plant = **Facade**. A design that swaps its damping or control law without changing the housing = **Strategy**.
- **Process and organisation design.** Escalation ladder = **Chain of Responsibility**. Change-request or work-order form that can be queued, logged, reversed = **Command**. Committee routing all cross-team traffic = **Mediator**, with its exact liability: it becomes the bottleneck and the monolith. Subscription to a status board = **Observer**. Pre-incident snapshot for rollback = **Memento**.

**Honest limits.** Interpreter, Prototype, Factory Method and Singleton are largely artefacts of programming-language object models and transfer poorly; do not force them. Physical systems cannot re-bind at run time the way objects can, so Decorator and State usually become *configuration-time* choices rather than dynamic ones — say that rather than pretending otherwise.

---

## Anti-patterns

- **Pattern-first design.** Choosing a pattern and then finding a use. Reverse it: force → pattern, always.
- **Paying for flexibility nobody needs.** Every pattern adds indirection, objects, and "human inefficiencies… more important in the long run" than the run-time ones. Unexercised flexibility is pure cost.
- **Pattern names as decoration.** `UserServiceFactoryStrategyImpl`. Name participants for the domain; use the pattern name only where it genuinely aids the reader.
- **Teaching or reviewing without consequences.** Every pattern in this book has a liabilities section. Omitting it is the single most common failure mode.
- **Singleton as the default.** See its entry — globals with a design-pattern badge.
- **Deep inheritance where composition was available.** The authors' own diagnosis of designers in the field.
- **Mistaking structure for intent.** Composite, Decorator and Proxy have near-identical diagrams and three unrelated purposes. Code that "looks like" a pattern is not that pattern.
- **A mediator that ate the system.** Centralisation is the pattern's stated cost; watch for the mediator growing past its colleagues.
- **Visitor over a churning hierarchy.** Every new element type breaks every visitor. Check hierarchy stability before recommending it.
- **Observer without a change protocol.** Bare notifications force observers to diff state and cause cascades that are "hard to track down." Specify what changed.

---

## Scope & limits

Covers the 1994 GoF book: its four principles, 23 patterns, and the authors' own comparisons. It does not cover later pattern literature (POSA, enterprise/integration patterns, concurrency patterns, DDD), nor the 30 years of critique of specific patterns — where modern practice diverges (Singleton, Interpreter, class-heavy Strategy in functional languages), say so explicitly rather than reciting 1994. For implementation in a real codebase, combine with project-specific context. Diagrams in the source are not reproduced; structures here are described in prose.