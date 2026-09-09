# Public-alias queue continuation contract v1

This is a new development task. It does not amend or regrade the stopped receipt
pilot. Public-list mutation remains supported, including Astra's counterexample.

`Queue()` exposes `items`, initially an ordinary empty Python list, and `cursor`,
initially zero. A client may append, clear, replace elements or remove elements
through an alias to that list **between** `append_batch` calls. Existing list
values remain nonnegative exact Python ints. The list attribute itself is not
replaced by clients. The cursor is the count recorded by the most recent successful
call and may temporarily be stale after a client's list mutation.

`append_batch(values)` consumes a finite iterable once. Values must be nonnegative
exact Python ints; bool and int subclasses are invalid. Iteration and validation
must complete before this method mutates either public field. Invalid input raises
ValueError. Iteration exceptions, including failures entering iteration, propagate
as the same exception object. On either failure, items, cursor and list identity
are exactly as they were at call entry, even when the cursor was already stale.

On success, append input values in order to the existing list, retain its identity,
set cursor to the actual resulting list length, and return that length. An empty
batch adds no items but synchronizes cursor to the current list length. Repeated
calls and recovery after a failed call must preserve these rules.

Inputs may observe the queue while being iterated; they must observe its call-entry
state throughout iteration. Inputs do not mutate the queue, reenter append_batch,
or run concurrent work. Concurrent/reentrant mutation, asynchronous exceptions and
resource exhaustion are outside this finite synchronous task's domain. Those are
explicit domain boundaries, not a claim of universal Python correctness.

For versioned continuation, a prior PASS covers only its exact contract, proposal,
checker, environment and initial-state identities. Any changed identity invalidates
reuse. Unchanged roots do not prove semantic completeness. The current public
contract always outranks a previous semantic conclusion.
