# SETUP_AGENT.md

Detect missing connections; assist install; never silent fail.

## Probe

`sealed-eval capabilities` → gh, ctx7, docker, intent-layer skill.

## Assist

- Missing gh: `brew install gh` + `gh auth login`; offer confirm-first `gh repo create` for control-plane (never inside subject)
- Missing ctx7: `npx ctx7 setup --cursor`
- Missing intent-layer: `npx skills add crafter-station/skills --skill intent-layer -g -a cursor -y`
- No seeds: paste AC markdown or run Eval Agent interview; fixture `orders` for dogfood

## Fallbacks

Local `sealed/` store without remote git. Fixture propose without intent-layer.
