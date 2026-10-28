# Chat registry

Which chat holds what. Claude cannot read ChatGPT, so **the owner fills in the ChatGPT rows** (the chat title is enough). Claude reads this file before it tells you where a file goes. Update it whenever you start, rename or retire a chat. Suggested title format: `LLF <ST> <lane>`, for example `LLF MI articles`.

## Claude Code sessions
| Title | Holds | Status |
|---|---|---|
| LookLearnFind Michigan (this repository) | LLF build, Michigan pages, briefs, ledger, packages. The only session that writes to `productions/2026/MI/` | active |
| TIP Florida Remotion animations | TIP video work; holds the `TIP_CLAUDE_SUPPLY_R10` folder and the R11 round (Ford/Koppie, El-Sayed feature pitch) | active; separate workstream, not LLF pages |
| LLF TIP editorial blueprint review | Origin of the lean editorial workflow | reference only |

## ChatGPT chats (owner: fill in)
| Title | Lane | Holds | Which package it was given |
|---|---|---|---|
| ______ | articles | Florida and Illinois article drafting; voice and format rules | (none; predates packages) |
| ______ | images | Illinois heroes, Florida and Illinois tiles, Michigan tile | (none) |
| ______ | video (TIP editorial workflow R10 and R11) | Video scripts and storyboards for the TIP workstream | R10, R11 zips |
| ______ | general (new, if you start one) | Articles and images in one chat, built from a `fresh` package | `handoff.py build MI --lane all --mode fresh` |

## Rules
- One lane per chat is cleaner, but one general chat works if it is given the `fresh` package and the READBACK passes.
- Never send a TIP video-workstream file (R10, R11) to an LLF lane chat, or an LLF brief to the video chat.
- When two chats could write the same angle (for example the El-Sayed Senate poll angle), the ledger says which one owns it. Today: the angle is withdrawn from the LLF articles lane.
