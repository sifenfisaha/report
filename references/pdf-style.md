# PDF style: what makes the document look written, not generated

Read this before building any PDF with `scripts/build_pdf.py`. The reader is usually a manager or a client who will forward the file; the look is judged in the first two seconds and the trust in the numbers over the next two minutes.

## Layout

- A4 portrait, 18 mm side margins, 20 mm top and bottom. `render_pdf.js` sets these and puts a footer in the bottom margin: document title on the left, "Page X of Y" on the right.
- Title block on page 1: the title, one or two grey meta lines (prepared by, date, project, launch target), a 1.5 pt rule. No cover page under about ten pages.
- Sections: `h2` with a hairline rule above, a one-sentence lead that states the section's point and its number, then the table or list. The first sentence of the document answers the question the reader came with.
- One sans face throughout (Noto Sans, falling back to Liberation Sans or Arial). Body 10 pt, table text 9 pt, descriptions 8.5 pt grey, title 21 pt, `h2` 13 pt. Do not go below 8.5 pt to make something fit.
- A one-page intro that must stay one page: put it in `<div class="page-break">` and trim text until it fits, rather than shrinking type.

## Tables

- Header row repeats on every page (`thead` is set to `table-header-group`), rows never split (`tr` has `break-inside: avoid`), and a heading or lead is never left alone at the bottom of a page (`break-after: avoid` on `h2`, `h3` and `p.lead`, `break-before: avoid` on `table`). Chrome honours these; still check.
- For item tables use the stacked pattern from `assets/report.css`: `#` column (`td.n`), a cell with the item in bold (`span.chg`) and the work underneath in grey (`span.work`), a narrow category column (`td.s`), and a right-aligned numeric column (`td.h`, tabular figures). Ranges use an en dash: `7–11`.
- Totals as a final `tr.total` row, not a sentence under the table. A number that appears in two places (lead and table, table and chart) is rounded the same way in both; round half up consistently.

## Exhibits

- Charts and timelines as inline SVG inside `<figure>` with a short `<figcaption>` saying what the numbers are and where they come from. One accent colour (a navy such as `#1f4e9c`) on the thing the title is about, everything else grey; values printed on the marks, no gridlines competing with them; the finding in the chart title ("Facility work is more than half of the estimate"), not the topic ("Hours by area").
- Keep SVG text at 12 to 13 units in a 760-wide viewBox; it scales to about 0.87 in the column.

## Words

- Typographic quotes and apostrophes (“ ” ’), en dashes in ranges, spelled-out dates (6 October 2026). The markdown converter does this for `.md` input; HTML you write by hand must do it itself.
- No emoji, no icons, no coloured callout boxes, no bold scattered through sentences, no "In conclusion", no "key takeaways", no bullet lists of single words. Sentences under 25 words; a bullet is one or two sentences.
- Internal remarks stay out of anything that may be forwarded: who called what hard, what can be charged for, nicknames. If the audience is unknown, write for the client and tell the user what you left out.

## Check before handing over

Open the PDF with Read, every page, and fix:

- a heading or a lead sentence at the bottom of a page with its table on the next
- a single list item or a single table row carried onto a new page on its own
- a doubled rule (title rule directly above a section rule)
- numbers that differ between the lead, a table and a chart
- straight quotes next to curly ones, hyphens where en dashes belong
- a page that is nearly empty because of a forced break

Fix spills by tightening spacing (`td` padding, `h2` margins, list spacing) or trimming a sentence, never by shrinking fonts below 8.5 pt. Re-render and look again; the layout is deterministic, so one more pass is cheap.
