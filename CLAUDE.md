# Huckleberry Alexa Skill

Private Alexa skill that voice-logs baby tracking events (nursing, diapers, bottles) to the Huckleberry app via its API.

## Structure

```
src/huckleberry_alexa/
  lambda_function.py      # AWS Lambda entry point; registers all handlers via SkillBuilder
  huckleberry_client.py   # Async→sync adapter; auth + child UID resolution
  handlers/
    common.py             # Launch, Help, CancelStop, SessionEnded, CatchAllException
    nursing.py            # StartNursing, PauseNursing, SwitchBreast, StopNursing
    diaper.py             # LogNappy
    bottle.py             # LogBottleFeed
    status.py             # LastFeedStatus, LastNappyStatus

tests/                    # pytest; one file per handler domain
interaction_model/en-GB.json  # Alexa NLU model
scripts/build_lambda.sh   # Builds deployment.zip
```

## Key Patterns

**All Huckleberry API calls** use `run_huckleberry_with_child(coro_factory, child_name=None)` from `huckleberry_client.py`:
- Authenticates, resolves child UID by name, runs async coroutine, returns `(result, resolved_child_name)`
- `coro_factory` signature: `(api: HuckleberryAPI, child_uid: str) -> Coroutine`
- Child defaults to `HUCKLEBERRY_DEFAULT_CHILD` env var (default: `"Frederica"`)

**Tests** mock `run_huckleberry_with_child` at the handler module level:
```python
@patch("huckleberry_alexa.handlers.nursing.run_huckleberry_with_child")
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `HUCKLEBERRY_EMAIL` | yes | — | Account email |
| `HUCKLEBERRY_PASSWORD` | yes | — | Account password |
| `HUCKLEBERRY_DEFAULT_CHILD` | no | `Frederica` | Child name to use when not specified |
| `HUCKLEBERRY_TIMEZONE` | no | `UTC` | Timezone for API calls |

## Lambda Config

- Runtime: Python 3.12, x86_64, 256 MB, 15s timeout
- If zip exceeds 50 MB (grpcio), upload via S3

## Running Tests

```bash
uv run pytest           # all tests
uv run pytest -m "not integration"  # skip live API tests
```

## Adding a New Intent

1. Add handler class in the appropriate `handlers/*.py` file
2. Register it in `lambda_function.py` via `sb.add_request_handler(...)`
3. Add intent + utterances to `interaction_model/en-GB.json`
4. Add tests in `tests/test_<domain>.py`
