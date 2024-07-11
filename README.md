# Record Metrics

Queries our current queue depth in Redis and puts it as a CloudWatch metric,
so we can implement auto-scaling by it..

## Development

```console
just venv             # once
. .venv/bin/activate  # every shell
```

## Tests

```console
just test
```

## Deployment

Merges to `main` result in a new Lambda bundle being placed on S3 and then
an automated commit into our IaC repository, `restyled-io/ops` that will
re-deploy the Lambda with it as source.

---

[LICENSE](./LICENSE.md)
