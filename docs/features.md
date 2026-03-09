# Huckleberry Alexa Skill — Features

## Invocation
Say "Alexa, open Huckleberry" or use one-shot commands:
"Alexa, ask Huckleberry to [command]"

## Commands

### Nursing (Breast Feeding)
- **Start feed**: "start a feed on my left/right breast"
  - Side is required; Alexa will ask if omitted
- **Pause feed**: "pause the feed"
- **Switch breast**: "switch breast" / "switch sides" / "swap breast" / "other side"
  - Records duration on current side and continues on the other
- **Stop & save feed**: "stop the feed" / "finish the feed" / "end the feed" / "save the feed"
  - Saves the feed session with all durations to Huckleberry history

### Bottle Feeding
- **Log bottle**: "log a bottle feed" or "log an 80ml bottle feed"
  - If amount not given, uses last bottle size from history
  - If no history, Alexa asks for the amount

### Nappy / Diaper Changes
- **Log nappy**: "log a nappy change" or "log a yellow nappy change"
  - Supported colours: yellow, green, brown, black, red, gray

### Status
- **Last feed**: "how long ago was the last feed" / "when was the last feeding" / "when did she last eat"
  - Searches last 48 hours; responds with elapsed time (e.g. "The last feed was 2 hours and 15 minutes ago")
- **Last nappy**: "how long ago was the last nappy" / "when was the last nappy change" / "when was the last diaper change" / "how long since the last diaper"
  - Searches last 48 hours; responds with elapsed time

## Multiple Children
All commands accept an optional child name: "log a nappy change for Frederica" or "start a feed on my left breast for [name]".
- Default child: **Frederica** (set via `HUCKLEBERRY_DEFAULT_CHILD` environment variable)
- Child names are looked up from your Huckleberry account at runtime
- If name not recognised, Alexa will tell you the available names

## Adding a New Feature
1. Add a new intent + utterances to `interaction_model/en-GB.json`
2. Add a new handler file in `src/huckleberry_alexa/handlers/`
3. Register it in `src/huckleberry_alexa/lambda_function.py`
4. Write tests in `tests/` following existing patterns
5. Update this file
