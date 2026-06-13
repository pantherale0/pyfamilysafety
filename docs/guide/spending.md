# Spending

Microsoft Family Safety can track Microsoft Store spending allowances. After
`Account.update()`, balance fields are populated when the API returns a single
balance entry.

## Reading balance

```python
await family_safety.update()
account = family_safety.accounts[0]

print(account.account_balance, account.account_currency)
```

Balance is fetched from `GET /v1/Spending/{USER_ID}`. If the response contains
exactly one balance object, `account_balance` and `account_currency` are set.
Otherwise they remain at defaults (`0.0` and `""`).

## Payment methods

The low-level API exposes `async_get_user_payment_methods(user_id, cid)` on
`FamilySafetyAPI`, but there is no high-level `Account` wrapper yet. See the
[Endpoint map](../advanced/endpoints.md) if you need direct access.

## API reference

See [Account](../reference/account.md).
