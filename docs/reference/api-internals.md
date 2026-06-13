# API internals

`FamilySafetyAPI` is the low-level HTTP client. Most applications should use
`FamilySafety` and `Account` instead.

!!! note "Advanced usage"
    Direct use of `FamilySafetyAPI` requires knowledge of endpoint keys defined in
    `pyfamilysafety.const.ENDPOINTS`. See the [Endpoint map](../advanced/endpoints.md).

::: pyfamilysafety.api.FamilySafetyAPI
    options:
      show_if_no_docstring: true
