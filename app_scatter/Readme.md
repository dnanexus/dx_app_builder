# Scatter app

A generic app for running an executable over a matrix of input elements.

## Example

Assume that we have applet `A` (applet-xxxx) that takes the input hash:
```
{
    a: file,
    b: int (optional),
    c: string,
    d: array:file
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
(*batch_inputs*), and those that remain fixed (*common_inputs*).
Then, we call the scatter app with:
```
{
  executable: applet-xxxx,
  batch_inputs: {
    a: [file-aaaa, file-bbbb, file-cccc]
    b: [1, null, 4]
  },
  common_inputs: {
    c: "foo",
    d: [file-yyyy, file-zzzz]
  },
  files: [file-aaaa, file-bbbb, file-cccc, file-yyyy, file-zzzz]
}
```

The outputs are:
```
{
  results: {
    outputs: {
       h : [file-uuuu, file-vvvv, file-wwww],
       g : [5, 9, 11]
    },
    launched: {
      { a: file-aaaa, b: 1, c: "foo", d: [file-zzzz, file-yyyy] }
      { a: file-bbbb,       c: "foo", d: [file-zzzz, file-yyyy] }
      { a: file-cccc, b: 4, c: "foo", d: [file-zzzz, file-yyyy] }
  }
}
```

## Scatter app inputs
- executable_id: `string`, an id of an *app*, *applet*, or *workflow*,
  to launch for each of the inputs
- batch_inputs: `hash`, a dictionary of key-value pairs, where the key is an input name,
and the value is an array of elements.
- common_inputs: `hash`, a dictionary of key-value pairs that are held constant.
- files: `array:file`, an array of any file ID in batch-inputs.
- instance_types (optional): `array:string`, an array of instance types


## Scatter app outputs
- results: `hash` a dictionary with two fields
   * outputs: an array for each output of the executable.
   * launched: an array of dictionaries that were used to call the executable
