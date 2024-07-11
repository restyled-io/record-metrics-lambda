# Record Metrics

Queries `{API}/system/metrics` for things like Queue depth and error rates, and
forwards every value to CloudWatch.

## Virtualenv

```console
python -m venv .venv
. .venv/bin/activate
```

## Development

```console
just setup
just test
```

---

[LICENSE](./LICENSE.md)
