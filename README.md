# Classification Ledger (working title)

A public, versioned record of how threat actors that present themselves as hacktivists are classified, with the evidence and confidence behind every placement. Other kinds of groups can be added later.

Each entry places one group on published frameworks for classifying hacktivism, states how confident the placement is, links the evidence, and says what would change the judgment. The reasoning is the point. The table is a by-product.

## Why this exists

Hacktivist classification is scattered across academic papers and vendor reports. The frameworks answer different questions (how organized is the group, what culture does it come from, how responsible is a state, what does it hit), and they often disagree about the same group. This ledger works through real groups one at a time and shows where the frameworks agree, where they break, and how placements change over time.

## What this is not

- **Not attribution.** Placements are analytic judgments from public sources. They are not formal attributions and should not be cited as such.
- **Not a detection feed.** There are no indicators of compromise here.
- **Not about individuals.** The ledger covers groups and personas only. It does not identify, or try to identify, the people behind them.

## How an entry works

Each group has one file in `entries/`. The top of the file is structured YAML (identity, aliases, sources, placements). The rest is markdown explaining the reasoning.

Two frameworks are required for every `draft` or `published` entry:

- **Derbyshire et al.**: impact and state alignment.
- **Healey**: the spectrum of state responsibility.

Two are optional, and are worth adding when they say something useful or when they fail to fit:

- **Samuel**: hacktivist origins and orientation.
- **Best and Luckenbill**: forms of deviant organization.

Every placement carries a value, a confidence level (`low`, `moderate`, `high`), evidence IDs that point to the entry's source list, and a one-line `would_change_if`. `METHOD.md` defines all of these.

Entries move through three statuses: `stub` (selected, not yet analyzed), `draft` (analyzed, still being reviewed), and `published`.

## Layout

```
README.md          this file
METHOD.md          frameworks, scales, confidence language, evidence rules
CHANGELOG.md       what changed, when, and why
LICENSE            MIT, for the code
LICENSE-DATA.md    CC BY 4.0 notice, for the data and prose
requirements.txt   Python dependency (PyYAML)
entries/           one markdown file per group; _TEMPLATE.md is the starting point
build/compile.py   validates entries and writes the data files
data/              compiled ledger.json and ledger.csv
```

## Building the data files

```
pip install -r requirements.txt
python build/compile.py --check    # validate only
python build/compile.py            # validate, then write data/ledger.json and data/ledger.csv
```

Stubs are left out of the data files unless you pass `--include-stubs`. The script exits with an error and prints every problem it finds if an entry fails validation.

## Adding an entry

1. Copy `entries/_TEMPLATE.md` to `entries/<id>.md`. The `id` must match the file name.
2. Start as `status: stub`. Move to `draft` once the placements and evidence are filled in.
3. Run `python build/compile.py --check` until it passes.
4. Add a line to `CHANGELOG.md`, and add a `history` item to the entry if it changes an existing placement.

## Licensing

- Code (`build/`): MIT. See `LICENSE`.
- Data and prose (`entries/`, `data/`, `METHOD.md`): CC BY 4.0. See `LICENSE-DATA.md`.

Suggested attribution: "Angela Reeder, Classification Ledger, https://github.com/ember-elkes/classification-ledger/".

## Corrections

Corrections are welcome and expected. Open an issue on this repository with the entry, the placement you think is wrong, and the evidence. Accepted corrections are logged in `CHANGELOG.md` and in the entry's `history`, so changes stay visible.

## Pace

The aim is roughly one new entry every two weeks. Posts on the accompanying site explain the reasoning behind each entry.
