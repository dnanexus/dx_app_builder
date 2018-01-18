# Scatter app

A generic app for running an executable over a matrix of input elements.

## Example

Assume that we have applet `A` (applet-xxxx) that takes the input hash:
```
{
    a: file,
    b: int (optional),
    c: string,
    d: file:array
}
```

It produces the outputs:
```
{
   g: File,
   h: Int
}
```

We want to launch `A` in parallel, on three sets of inputs:

| a         | b  | c     |  d                     |
| --        | -- | --    | --                     |
| file-aaaa | 1  | "foo" | [file-zzzz, file-yyyy] |
| file-bbbb |    | "foo" | [file-zzzz, file-yyyy] |
| file-cccc | 4  | "foo" | [file-zzzz, file-yyyy] |

We split the inputs to those that change between invocations
(*batch-inputs*), and those that remain fixed (*common-inputs*).
Then, we call the scatter app with:
```
{
executable: applet-xxxx,
batch-inputs:
  { a: [file-aaaa, file-bbbb, file-cccc]
    b: [1, null, 4] },
common-inputs:
  { c: "foo",
    d: [file-yyyy, file-zzzz]},
files: [file-aaaa, file-bbbb, file-cccc, file-yyyy, file-zzzz]
}
```

The outputs are:
```
{
launch_args: {
   { a: file-aaaa, b: 1, c: "foo", d: [file-zzzz, file-yyyy]
   { a: file-bbbb, c: "foo", d: [file-zzzz, file-yyyy] }
   { a: file-cccc, b: 4, c: "foo", d: [file-zzzz, file-yyyy] }

  results: {
    h : file:array
    g : int:array
  }
}
```

## Scatter app inputs
- executable: `app-xxxx`, `applet-xxxx`, or `worfklow-xxxx`
  Runnable to launch for each of the inputs
- batch-inputs: `hash`, a dictionary of key-value pairs, where the key is an input name,
and the value is an array of elements.
- common-inputs: `hash`, a dictionary of key-value pairs that are held constant.
- files: `file:array`, an array of any file ID in batch-inputs.
- instance_types (optional): `string:array`, an array of instances types


## Scatter app outputs
- ouputs: `hash`
-
