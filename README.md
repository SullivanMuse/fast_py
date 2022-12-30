# fast_py

A pure Python implementation of the Fast programming language.

## Features

| Term | `parse`? | `eval`? | `check`? | `infer`? |
| --- | --- | --- | --- | --- |
| `1234` | Yes | Yes | Yes | Yes
| `x: y` | Yes | Yes | Yes | Yes
| `int` | Yes | Yes | Yes | Yes
| `type` | Yes | Yes | Yes | Yes
| `(x, y, z)`

## Notes

In checking mode, an expression is checked against a known type to see if it fits.

check :: Env -> Term -> Ty -> Bool

In synthesis mode, a type is derived directly from an expression.

synth :: Env -> Term -> Ty

Type annotations can replace synthesis with checking.

Usually introduction forms correspond to checking rules, and ellimination forms correspond to synthesis.

Redexes arise when elliminators encounter constructors.

For instance, (if true then x else y) is clearly a redex which evaluates to x.

For bidirectional type checking, we can split the notation into two forms of judgement

e => t      (synthesis)
e <= t      (checking)

Bidirectional type checking

Synthesis
    Synthesize the type of a variable by looking it up in the typing context.

    Synthesize an application by first synthesizing a type for the function and then checking that the argument matches the argument type.

    Synthesizing an annotation is done by checking the expression against the annotation, and then returning the annotated type.

Checking
    To check a function, the expected type should be an arrow type, and the body should type check with the return type after extending the context with the annotated argument type.

    To check a constructor, the expected type should be the corresponding type, and the arguments to the constructor should type check with the argument types.

    To type-check introduction forms, first check that the particular form is a constructor of the top level type, and then check that the arguments to the constructor have the appropriate type.

    To check something else, synthesize the type of the expression and check that is is equal to the expected type.

Vocab
    Eta expansion is (f => x -> f x)

Read back is just convenience

| Type | Intro | Ellim |
| --- | --- | --- |
| ._: _ -> _ | _ -> _ | _ _
| ._: _, _ | _, _ | fst, snd

Normalization by evaluation is just a strategy to get expressions into a form where it is easy to check for type equality.
