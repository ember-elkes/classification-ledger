# Method

This document defines the frameworks, scales, and rules the ledger uses. If an entry and this document disagree, the entry is wrong, or this document needs updating. Either way, say so in the changelog.

## Scope

The ledger classifies **groups and personas**, meaning the public identity an actor presents and the judgments analysts make about it. It does not identify or profile individuals. Entries cover groups that present as hacktivists first. Each entry records the `claimed_identity` (how the group presents itself) separately from the placements (what the evidence suggests), so that mismatches between the two can be examined.

## Required frameworks

### 1. Impact and state alignment (Derbyshire et al.)

Source: Derbyshire, Selck-Paulsson, van der Walt and Burton, *From Protest to Power Plant: Interpreting the Role of Escalatory Hacktivism in Cyber Conflict* (2025), arXiv:2509.05104.

Recorded as `placements.derbyshire`:

- `impact`: one or more of `nuisance`, `disruption`, `destabilization`, `harm_to_life` (escalating severity), and `information`, `extortion`, `theft`, `intelligence` (kinds of gain). A group can span several, for example `[nuisance, information]`.
- `alignment`: `opposed`, `agnostic`, `aligned`, or `undetermined`, relative to a state's objectives. Name the state in the entry body.
- `state_band` (optional, only when `alignment` is `aligned`): `tolerated`, `influenced`, `supported`, or `controlled`. The paper collapses Healey's spectrum into these bands. **Take the band from the paper's definitions, not from this ledger's reading of Healey**, and do not derive it automatically from the Healey point.

### 2. Spectrum of state responsibility (Healey)

Source: Healey, *Beyond Attribution: Seeking National Responsibility for Cyber Attacks* (Atlantic Council, 2011).

Recorded as `placements.healey.point`, one of, from least to most state involvement:

`state_prohibited`, `prohibited_but_inadequate`, `state_ignored`, `state_encouraged`, `state_shaped`, `state_coordinated`, `state_ordered`, `state_rogue_conducted`, `state_executed`, `state_integrated`.

Use `undetermined` when the evidence does not support a placement. That is a legitimate result, not a failure to finish.

## Optional frameworks

### Samuel's hacktivist typology

Source: Alexandra Samuel, *Hacktivism and the Future of Political Participation* (doctoral dissertation, 2004).

`placements.samuel.type`: `political_coding`, `political_cracking`, `performative_hacktivism`, or `unnamed_cell`. The last is the fourth cell of the 2x2 (outlaw orientation, artist-activist origin) that the scheme leaves unnamed.

### Forms of deviant organization (Best and Luckenbill)

Source: Best and Luckenbill, *Organizing Deviance* (Prentice-Hall, 1982; 2nd ed. 1994). This is general criminology, not built for hacktivists, so expect awkward fits.

`placements.best_luckenbill.level`: `loner`, `colleagues`, `peers`, `teams`, or `formal_organization`.

Optional frameworks are most useful when they fail. An entry where a framework cannot place a group is worth writing up.

## Confidence

Every placement carries one of three levels. The wording is adapted from the confidence language used in US intelligence community analytic standards; check it against the original before citing it as the same.

- **high**: the judgment rests on good-quality information that is corroborated and leaves few plausible alternatives.
- **moderate**: the sources are credible and the judgment is plausible, but corroboration is limited or reasonable alternative readings remain.
- **low**: the information is sparse, fragmentary, or questionable, or there is significant uncertainty. The placement is the best current reading and no more.

Rules this ledger adds:

- A `high` placement needs at least two evidence items.
- A `high` placement should not rest only on actor-controlled sources, or only on a single vendor. The validator cannot check this, so the entry body should say how the evidence is independent.
- Confidence applies to each placement separately. A group can be `high` on impact and `low` on state responsibility.

## Evidence and sources

Each entry lists its own sources. Every source has an `id`, `title`, `url`, `tier`, and `retrieved` date, and every placement cites sources by `id`.

Source tiers mirror the tiers used in the working Notion database:

`primary_actor_controlled`, `government_law_enforcement`, `vendor_threat_intel`, `journalism_specialist_media`, `academic_think_tank`, `aggregator_wiki`.

Actor-controlled sources show how a group presents itself. They do not show what it is. Cite them for `claimed_identity`, not for state alignment.

## Would change if

Every placement states, in one line, what evidence would move it. This keeps judgments falsifiable and gives later updates a clear trigger.

## Changes and corrections

- Changing an existing placement is recorded in the entry's `history` and in `CHANGELOG.md`, with the date and the reason.
- Placements are never silently overwritten. A reader should be able to see that a group moved and why.
- Corrections from readers follow the same path.

## What the ledger does not claim

Placements are analytic judgments based on public sources at a point in time. They are not formal attribution, legal findings, or statements of fact about any state's conduct.
