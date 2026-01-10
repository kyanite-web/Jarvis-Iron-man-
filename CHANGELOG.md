# Changelog

All notable changes to this project will be documented in this file.

## 2026-01-10

### Added
- voice_assistant.py initial voice assistant implementation. ([f2fd31b](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/f2fd31bc0e0b791e5e5e94480a5af5b2eaf51c89))
- voice_assistant_app.py with enhanced TTS, fuzzy wake word detection, microphone auto-selection, adaptive energy/calibration, robust listening (retries), and more conversational responses. ([21c6ae1](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/21c6ae1e3a62966e71fe4c4e178ffc0a23904ca5))
- voice_assistant2.py with refined recognizer setup, per-listen calibration (faster), normalized wake handling, and simplified TTS engine usage. ([d97b974](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/d97b974ba93df1da00de9d682450468d2b42440a))
- voice_assistant_commands.py: faster processing via queued TTS worker, expanded natural-language triggers/responses, and Spotify open/play support. ([67e0682](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/67e06821c9218df1e620d7057b7a8a392dbbd04b))

### Changed
- Date/time queries: support combined “today + time” requests in app and v2 variants.
- Wake word detection: improved normalization-based matching; fuzzy/token-based matching in app variant.
- TTS:
  - app variant: humanized responses with chunked delivery and slight rate/volume variation
  - v2 variant: simplified one-shot engine usage
  - commands variant: persistent engine with background queue for faster, non-blocking speech
- Microphone handling: auto-select likely device by name; per-listen ambient calibration and dynamic energy where applicable.
- Command handling: expanded natural-language triggers for greetings, thanks, jokes, and site launching; added Spotify open/play behaviors with app or web fallback.

## 2026-01-09

### Added
- Initial commit. ([3294534](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/3294534a8d6811171a096a07fdbeecf33346c681))
- Add CHANGELOG.md with summary of changes. ([758f594](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/758f594669f87aecc3e25d09c4120416da65e548))

### Changed
- Update repository description to reflect its purpose and capabilities. ([38df154](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/38df154eab6b6f026319d9ab19a93a6740b200a8))
- Update CHANGELOG.md with 2026-01-09 entries. ([9bea503](https://github.com/kyanite-web/Jarvis-Iron-man-/commit/9bea50397d9746d0a240ac4757abf924c06f7f63)).