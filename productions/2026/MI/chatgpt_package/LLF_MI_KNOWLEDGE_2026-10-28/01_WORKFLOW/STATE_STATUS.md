# State of play (2026-10-28, evening)

## Live on looklearnfind.com
| State | Pages | Reported pieces |
|---|---|---|
| Florida | Hub, governor, Senate, House directory, 28 district pages, methods page (`/elections/2026/florida/`) | Florida House independent spending; Florida governor fundraising and polling |
| Illinois | Hub, governor, Senate, House directory, 17 district pages (`/elections/2026/illinois/`). The roster is labeled "not official" because the State Board list was unreadable by automated tools | IL-07 Ford and outside money; Illinois Senate primary money; IL-04 ballot access |
| Michigan | **None yet** | AIPAC/UDP money delta (`/learn/aipac-udp-money-delta-october-2026/`); Michigan Senate Kalshi delta (`/learn/michigan-senate-delta-october-2026/`) |

The homepage leads with the four newest pieces, a two-tile "The state files" strip (Florida, Illinois) and a social card. All hero images are AI illustrations with the credit "AI illustration. Not a photograph of a real place or event."

## Built locally for Michigan, not deployed
Roster reconciled to the official Michigan Department of State listing (read Oct 28), 75 people; 74 link to a working TIP profile; TIP gap profiles added with the owner's approval (five governor entries sit at `review`, so TIP's public Michigan governor page is empty until the owner promotes them); portraits (18 licensed images, the rest monograms); Kalshi markets (governor, Senate, 9 of 13 House districts); Census district geometry; hub, governor, Senate, House directory and 13 district pages; 134 automated tests pass; strict build has no violations. **Waiting on:** the owner's go-ahead to deploy and a Michigan tile image (`s4-michigan`), because the homepage strip has no third tile yet.

## Article pipeline, Michigan
| ID | Angle | Status |
|---|---|---|
| MI-A1 | The independent who left (Duggan) | READY: brief and claims in this package; draft is yours |
| MI-A2 | Senate poll beside the market | WITHDRAWN: the live Senate delta already carries it |
| MI-A3 | MI-13: incumbent loses primary | NOT READY: lead source blocked (403); one damaging claim unverified |
| MI-A4 | MI-10: outside spending in an open seat | RESEARCH IN PROGRESS: FEC data pulled, deduplication to verify; will come as a second package |
| Video | Michigan state video | NOT STARTED: opens after fact-checked articles and an approved script direction. Asset pack only; **no MP4** unless the owner explicitly requests a render |

## Image system (what you have already made)
Four heroes (a stone stoop with mailers at dawn; three wooden trays with a ledger; clipboards on a teal table; mail and a phone on a kitchen table at dusk), two state tiles (a county elections counter in morning light for Florida; a folding table in a brick church hall for Illinois) and one social card (four small stacks on a long desk). Look: photographic, shallow depth of field, warm natural light, muted teal and amber, no people, calm and observational. Michigan tile is a cooler late-October variant. See `04_VISUALS/reference_images/`.

## Names that cause confusion
"The money delta piece" is the owner's concept name for the AIPAC/UDP spending report. The folder `productions/2026/MI/` is only a state folder. The Michigan tile image is `S4` (S3 is the homepage social card).
