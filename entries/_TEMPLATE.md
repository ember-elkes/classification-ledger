---
# Copy this file to entries/<id>.md. The id must match the file name.
# Files that start with an underscore are ignored by the build script.

id: example-group                 # lowercase letters, numbers, hyphens
name: "Example Group"
claimed_identity: hacktivist      # hacktivist | cybercriminal | extortion | state | unknown | other
aliases:
  - Example Grp
status: stub                      # stub | draft | published
last_reviewed: 2026-11            # YYYY-MM or YYYY-MM-DD

sources:
  - id: src-01
    title: "Title of the source"
    url: "https://example.org/source"
    tier: vendor_threat_intel     # primary_actor_controlled | government_law_enforcement | vendor_threat_intel
                                  # | journalism_specialist_media | academic_think_tank | aggregator_wiki
    retrieved: 2026-11-04

# Required for draft and published: derbyshire and healey.
# Optional: samuel, best_luckenbill.
# Every placement needs confidence, evidence (source ids), and would_change_if.
placements:
  derbyshire:
    impact: [nuisance, information]   # nuisance | disruption | destabilization | harm_to_life
                                      # | information | extortion | theft | intelligence
    alignment: aligned                # opposed | agnostic | aligned | undetermined
    state_band: supported             # optional, only if aligned: tolerated | influenced | supported | controlled
    confidence: moderate              # low | moderate | high  (high needs 2+ evidence ids)
    evidence: [src-01]
    would_change_if: "One line: what evidence would move this placement."
  healey:
    point: state_encouraged           # state_prohibited | prohibited_but_inadequate | state_ignored | state_encouraged
                                      # | state_shaped | state_coordinated | state_ordered | state_rogue_conducted
                                      # | state_executed | state_integrated | undetermined
    confidence: low
    evidence: [src-01]
    would_change_if: "One line."
  # samuel:
  #   type: political_cracking        # political_coding | political_cracking | performative_hacktivism | unnamed_cell
  #   confidence: low
  #   evidence: [src-01]
  #   would_change_if: "One line."
  # best_luckenbill:
  #   level: peers                    # loner | colleagues | peers | teams | formal_organization
  #   confidence: low
  #   evidence: [src-01]
  #   would_change_if: "One line."

# Add an item whenever an existing placement changes.
history:
  - date: 2026-11-04
    change: "Entry created."
---

## Summary

Two or three sentences: who the group presents itself as, and where it landed.

## Why these placements

One short paragraph per placement. State the evidence, the alternative readings,
and why the confidence level is what it is.

## Where the frameworks disagree or break

The most useful section. Note any framework that cannot place the group.

## Alias notes

Names the group uses and names others use for it. Note collisions with other groups.

## Open questions

What would be worth checking next.
