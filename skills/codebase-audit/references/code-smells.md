# Code Smell Catalogue (SMELL-*)

A smell is a surface symptom that usually points to a deeper design problem. It is a prompt to
look closer, not a verdict: report a smell when you can explain the concrete cost (harder to
change, test, or understand) in *this* code. Thresholds are rules of thumb — adjust to the language
and domain (e.g. Rust `match` arms and React JSX inflate line counts).

Based on Fowler's *Refactoring* (2nd ed.), Kerievsky's *Refactoring to Patterns*, and common
static-analysis rules (Sonar, clippy, eslint).

**When reporting a smell**: cite the ID, give the locations, state the cost, and name the
refactoring that removes it. If one smell appears in many places, file one finding listing them.

## Bloaters — code that has grown too large to work with

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-001 | Long Function | > ~40 lines of logic, several comment-delimited "sections", multiple levels of abstraction. | Extract Function, Decompose Conditional, Replace Temp with Query. |
| SMELL-002 | Large Class / Module (God object) | > ~400–500 lines, > ~15 public methods, many unrelated fields, name like `Manager`, `Service`, `Utils`, `Core`. | Extract Class/Module by responsibility, Extract Subclass/trait. |
| SMELL-003 | Long Parameter List | > 3–4 params, or same group of params passed together. | Introduce Parameter Object, Preserve Whole Object. |
| SMELL-004 | Primitive Obsession | Money/ids/emails/status as `string`/`number`; parallel arrays; status strings compared everywhere. | Replace Primitive with Object/newtype, Replace Type Code with enum/union. |
| SMELL-005 | Data Clumps | Same 3+ fields appearing together in many signatures or structs. | Extract Class / struct. |

## Object-orientation / abstraction abusers

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-010 | Repeated Switches | Same `switch`/`match` on a type tag in several places. | Replace Conditional with Polymorphism / trait / lookup table. |
| SMELL-011 | Temporary Field | Fields only set/used in some code paths; nullable "sometimes" fields. | Extract Class; model states as union/enum. |
| SMELL-012 | Refused Bequest | Subclass/implementor ignores or throws on inherited members. | Replace Inheritance with Delegation; split the interface. |
| SMELL-013 | Alternative Classes with Different Interfaces | Two modules do the same job with different APIs. | Unify interface, Extract Superclass/trait, delete one. |

## Change preventers — one change forces many edits

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-020 | Divergent Change | One module is edited for many unrelated reasons (DB schema, UI text, pricing rules). | Split by reason to change (Extract Class/Module). |
| SMELL-021 | Shotgun Surgery | One logical change touches many files (adding a field requires edits in 8 places). | Move Function/Field to gather the knowledge; Combine Functions into Class. |
| SMELL-022 | Parallel Inheritance / Parallel Structures | Adding X requires adding a matching Y elsewhere (e.g. each entity needs handler + DTO + mapper + validator by hand). | Collapse hierarchies; generate from one schema. |

## Dispensables — things that could be removed

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-030 | Duplicated Code | Same logic copy-pasted (≥ ~6 lines or same algorithm), possibly with small tweaks. | Extract Function; Pull Up Method; but only if the copies represent the same knowledge (GEN-008). |
| SMELL-031 | Dead Code | Unreferenced exports, unreachable branches, commented-out code, unused params. | Delete. |
| SMELL-032 | Speculative Generality | Abstract base with one subclass, unused hooks/params, "for future use". | Collapse Hierarchy, Inline Function, Remove Parameter. |
| SMELL-033 | Lazy Element | Class/module/wrapper that adds nothing over what it wraps. | Inline. |
| SMELL-034 | Comments as Deodorant | Long comments explaining confusing code instead of clarifying the code. | Extract Function with a good name; rename variables. |
| SMELL-035 | Data Class (anemic model) | Records with only getters/setters while all their behavior lives in "service" functions elsewhere. | Move Function into the data's owner — when domain behavior exists. DTOs are fine as DTOs. |

## Couplers — excessive coupling between modules

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-040 | Feature Envy | Function uses another module's data far more than its own. | Move Function. |
| SMELL-041 | Inappropriate Intimacy / Insider Trading | Modules reaching into each other's internals; deep imports of private files. | Move members; define explicit interface; Hide Delegate. |
| SMELL-042 | Message Chains | `a.b().c().d().e` — caller knows a long navigation path. | Hide Delegate; Extract Function. |
| SMELL-043 | Middle Man | Class that only forwards calls. | Remove Middle Man / Inline. |
| SMELL-044 | Global / Ambient Dependencies | Hidden reliance on singletons, globals, env vars, current time. | Inject the dependency (parameter, constructor, context). |

## Other common smells

| ID | Smell | Signs / heuristics | Typical refactoring |
|---|---|---|---|
| SMELL-050 | Mysterious Name | Names that require reading the body to understand. | Rename. |
| SMELL-051 | Mutable Data shared widely | Objects mutated by many functions; aliasing bugs. | Encapsulate; return new values; restrict mutation to an owner. |
| SMELL-052 | Flag Arguments | Boolean param that selects between two behaviors. | Split into two functions. |
| SMELL-053 | Arrow Code / Deep Nesting | Nesting > 3 levels. | Guard clauses; Extract Function. |
| SMELL-054 | Magic Numbers / Strings | Unnamed literals with meaning. | Named constants/enums. |
| SMELL-055 | Error Swallowing | Empty catch / ignored Result. | Handle, propagate with context, or report (GEN-040). |
| SMELL-056 | Stringly-Typed Code | Using strings for states, kinds, keys that a type system could check. | enum / union / newtype. |
| SMELL-057 | Boolean Blindness / Contradictory Flags | `isA`, `isB`, `isC` booleans that represent one state machine. | Discriminated union / enum state. |
| SMELL-058 | Loops that should be pipelines (or vice versa) | Manual accumulation that obscures intent, or chains so long they hide the logic. | Replace Loop with Pipeline / or extract named steps. |
| SMELL-059 | Inconsistent Abstraction Levels | One function mixes orchestration with byte-level detail. | Extract Function per level (Single Level of Abstraction). |
| SMELL-060 | Hard-coded Configuration | URLs, credentials, limits, feature switches in code. | Move to validated config (GEN-100). |
| SMELL-061 | Test Smells | See `testing.md` §6. | — |

## Prioritizing smells

Raise priority when the smelly code is:
- on a **hot change path** (frequently modified — check `git log --format= --name-only | sort | uniq -c | sort -rn | head` if git history is available);
- **critical** (auth, money, data integrity);
- **untested** — smell + no tests means changes there are risky.

Lower priority when the code is stable, isolated, generated, or scheduled for removal.
