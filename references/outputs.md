# Deliverables: what each one contains

Pick the section for what the user asked for. Every deliverable is grounded in `transcript.txt`, `screen-notes.md` and `meeting-notes.md`; cite timestamps (`[14:04]`) so the user can jump to the recording and check.

## Meeting summary with decisions and action items

```
# <Meeting> – <date>
<one paragraph: what the meeting was for and what came out of it>

## Decisions
- <decision> — who decided, [mm:ss]

## Requests and changes asked for
- <request>, grouped by area if there are more than ten

## Action items
| Owner | Action | By when | Source |
| --- | --- | --- | --- |

## Open questions
- <question nobody answered, and who should>

## Timeline
| Time | Topic |
```

Keep the summary to one page of text; the tables carry the detail. Attribute only when the transcript or the video makes the speaker clear.

## List of requested changes (bullet points)

One bullet per change, in the words the requester used, with the detail that was given (limits, names, counts). Group by area (user side, coach side, admin side, process) when there are more than about ten. Mark anything the requester left unresolved ("said he would come back to it and did not"). If the note-taker typed a list during the call, reconcile it against the audio and say where they differ; the audio usually adds limits and reasons that the notes compressed.

## Scope and hour estimate

The structure that has worked for a change request:

```
# <Project> changes – scope and hour estimates
Summary: total range and mid-point, the biggest block, what is new versus adjusted, fit against the deadline
Basis and assumptions: source, codebase and date, what an hour covers, team size, how to read ranges, scope classes, exclusions
One section per area: a lead with the area total, then a table (# | change and what it takes | scope | hours low–high)
Dependencies: what gates what, what is built once and shared
Open questions that move the estimate (each with the hours it swings)
Suggested sequencing to the deadline (a drawn timeline when the user wants a plan)
```

- Scope classes: Adjustment (changes an existing screen or rule), New feature (new capability inside an existing module), New module (no foundation in the code today), Ops (setup, QA, design). These are what justify a change-request charge; say so neutrally and leave the contract question to the user.
- Ground every line in the codebase when it is on the machine: find the repo (several copies may exist; take the newest master), identify the stack, the data model, the modules and screens the change touches, and whether a foundation exists (a calendar, a role, an import, a payment tier). Say which copy and date you used.
- Hours cover implementation, unit tests and the developer's own testing; regression QA, builds and load tests are their own line. Give low–high ranges, plan on the mid-point, and compute totals with a script so the lead, the tables and any chart agree.
- Compare the total with the team's own estimate from the call and with the team's capacity (active developers × 40 h) and say plainly whether the deadline holds.

## Clean transcript

`transcript.txt` with the mis-hearings corrected (keep a list of corrections at the top), long runs split into paragraphs at topic changes, and speaker labels only where they are certain. Do not rewrite what people said.

## PDF or shareable doc of any of the above

PDF: build the markdown or HTML, then `scripts/build_pdf.py`; follow `references/pdf-style.md` and check every page. A version for the client is cut from the internal one: keep the tables, drop the internal summary and assumptions, write a one-page neutral introduction (purpose, totals by area, how estimates were made, how to read the tables), and remove names and remarks that do not belong outside the team.

Doc: when a docs connector is available, create the doc first with its outline, then fill it section by section; the connector's own instructions take precedence.
