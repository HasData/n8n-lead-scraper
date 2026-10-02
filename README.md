# n8n Lead Scraper Workflow

![HasData, the API the Maps and SERP nodes call](banner.png)

An importable n8n workflow that builds a lead list from a Google Sheets config. It searches Google Maps for businesses, dedupes them, scrapes each website for emails, falls back to a Google search when the site hides them, and writes the merged leads back to the sheet. The written walkthrough is [Scrape Leads with n8n](https://hasdata.com/blog/scrape-leads-with-n8n?utm_source=github&utm_medium=syndication&utm_campaign=scrape-leads-with-n8n&utm_content=n8n-lead-scraper-readme).

## Table of Contents

- [What the Workflow Does](#what-the-workflow-does)
- [Setup](#setup)
- [The Maps Stage, Measured](#the-maps-stage-measured)
- [Disclaimer](#disclaimer)
- [More Resources](#more-resources)

## What the Workflow Does

`scrape-leads-with-n8n.json` imports as 17 connected nodes and a sticky note listing the requirements. The flow reads a `config` sheet (query, location, page count, offset), builds the search tasks, pulls Google Maps results through the [HasData API](https://hasdata.com/apis/google-maps-search-api?utm_source=github&utm_medium=syndication&utm_campaign=scrape-leads-with-n8n&utm_content=n8n-lead-scraper-readme), removes duplicates, and branches per lead. Businesses with a website get their site scraped for emails, businesses without one, or with a site that hides addresses, go through a Google search pass instead. Both branches merge into a new timestamped sheet the workflow creates in the `Leads` file on every run.

## Setup

Import the JSON into n8n, then attach your own credentials where the nodes ask, Google Sheets OAuth and a HasData API key (the placeholders read `REPLACE-WITH-YOUR-CREDENTIAL-ID`). Create a Sheets file named `Leads` with a `config` sheet carrying `leads_query`, `location`, `page_count` and `offset`, then point the two Sheets nodes at your own file. The trigger is manual, so a run starts from the editor.

## The Maps Stage, Measured

`measurement/` holds the numbers behind the article's pagination advice. On a dense query (emergency plumbing in New York) 12 pages returned 240 rows that deduped to 189 unique places, roughly a fifth of the rows repeating across pages. On a narrow small-town query the results ran dry after a single page of 8 unique places, the second fetch came back empty. The exact counts drift between runs because Maps itself does. The dense query keeps producing duplicates across pages, the narrow one exhausts fast. Deduplication by title plus `kgmid` is what the workflow's dedupe node mirrors, and the raw run log carries both runs page by page.

## Disclaimer

The workflow collects publicly visible business listings and contact pages. Whether and how such collection is appropriate depends on jurisdiction, the source, and the use, and nothing in this repository is legal advice. [Is Web Scraping Legal?](https://hasdata.com/blog/is-web-scraping-legal?utm_source=github&utm_medium=syndication&utm_campaign=scrape-leads-with-n8n&utm_content=n8n-lead-scraper-readme) covers how we think about the question.

## More Resources

- [Scrape Leads with n8n](https://hasdata.com/blog/scrape-leads-with-n8n?utm_source=github&utm_medium=syndication&utm_campaign=scrape-leads-with-n8n&utm_content=n8n-lead-scraper-readme), the step-by-step walkthrough of this workflow
- [Web Scraping for Lead Generation](https://hasdata.com/blog/web-scraping-for-lead-generation?utm_source=github&utm_medium=syndication&utm_campaign=scrape-leads-with-n8n&utm_content=n8n-lead-scraper-readme), the wider playbook
