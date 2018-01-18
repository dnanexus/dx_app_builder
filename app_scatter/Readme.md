# Scatter app

A generic app for running an executable over a matrix of input elements.

## Example

Applet `A` (applet-xxxx) with inputs:
- a: `file`
- b: `int` (optional)
- c: `string`
- d: `file:array`

* and outputs:
- g: File
- h: Int

We want to launch `A` in parallel, on three sets of inputs:
{a: file-aaaa, b: 1, c: "foo", d: [file-zzzz, file-yyyy]}
{a: file-bbbb      , c: "foo", d: [file-zzzz, file-yyyy]}
{a: file-cccc, b: 4, c: "foo", d: [file-zzzz, file-yyyy]}

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

## Scatter app inputs
- executable: `app-xxxx`, `applet-xxxx`, or `worfklow-xxxx`
  Runnable to launch for each of the inputs
- batch-inputs: `hash`, a dictionary of key-value pairs, where the key is an input name,
and the value is an array of elements.
- common-inputs: `hash`, a dictionary of key-value pairs that are held constant.
- files: `file:array`, an array of any file ID in batch-inputs.
- instance_types (optional): `string:array`, an array of instances types


## Scatter app outputs
