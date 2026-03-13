# Track B: Develop an AI-Assisted Human-in-the-Loop Workflow for Single Cell Cloning

**Leads:** Rick Wierenga ([rick@monomerbio.com](mailto:rick@monomerbio.com)) / Will Pierce ([will@monomerbio.com](mailto:will@monomerbio.com))

**Goal:** Build an AI-assisted workflow that dilutes and plates a bead suspension (cell proxy) to maximise single-bead wells in a 96-well plate, images the plate, classifies each well with ML, and supports human review via Monomer's Culture Monitor.

---

# Setup

## 1. Python environment

**Python 3.9+** and a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

Install dependencies (includes PyLabRobot from GitHub):

```bash
pip install -r requirements.txt
```

## 2. Connect to the OT-2

Set the robot host. The example script requires `OT2_HOST` (your OT-2's IP):

```bash
export OT2_HOST=192.168.1.1
```

Replace with your robot's actual IP.

## 3. Software stack

| Platform | Role |
|---|---|
| **Opentrons OT-2** | Performs all liquid handling steps via [PyLabRobot](https://docs.pylabrobot.org/index.html). |
| **Cephla Squid** | Images the seeded plate. Make sure to label your experiment ID in the Squid software before imaging. Only square scan shapes are supported for the Monomer data agent. |
| **Monomer Culture Monitor** | Human-in-the-loop review of classified wells. Log in at [cloud-staging.monomerbio.com](https://cloud-staging.monomerbio.com/). |

## 4. Connect to the Monomer Cloud MCP

The Monomer Cloud MCP is your primary method for interacting with plates and cultures programmatically. For this track, **use the MCP to upload classification results and update culture statuses** rather than the Culture Monitor UI directly. (You should still get familiar with the UI so you know how scientists will interact with the system.)

We have provided instructions for multiple ways to connect. If you are unfamiliar with these, we recommend **Option A: Cursor**.

### Option A: Cursor

1. Download [Cursor](https://cursor.com/download)
2. Open Cursor → Settings → Tools & MCP → Add Custom MCP
3. Replace the text in this file with the following:

```json
{
  "mcpServers": {
    "monomer-cloud": {
      "type": "http",
      "url": "https://backend-staging.monomerbio.com/mcp"
    }
  }
}
```

4. Save and close this file.
5. Next to monomer-cloud in the settings, click 'Connect' and go through the authentication flow.

### Option B: Claude Code (requires subscription)

1. Set up Claude Code using the instructions from their [Get Started page](https://code.claude.com/docs/en/overview#get-started).
2. In your terminal, run the following command to set up the **monomer cloud** MCP:

```bash
claude mcp add --scope user --transport http monomer-cloud https://backend-staging.monomerbio.com/mcp
```

3. Open a new claude session (type `claude` in your terminal to start).
4. Type `/mcp` and navigate to monomer-cloud using arrow keys. Press enter twice, and then follow the authentication flow in your browser.

### Option C: Any MCP-compatible tool

Add the following to your MCP config:

```json
{
  "mcpServers": {
    "monomer-cloud": {
      "type": "http",
      "url": "https://backend-staging.monomerbio.com/mcp"
    }
  }
}
```

The Monomer Cloud MCP speaks standard MCP (JSON-RPC 2.0 over HTTP POST).

---

# Part 1: Workcell Tutorial — PyLabRobot + OT-2 Liquid Handling

Monomer Staff will walk both teams through a hands-on tutorial of the OT-2 using PyLabRobot.

With the OT-2 on the network and labware in the expected slots, run the example:

```bash
python monomer_example.py
```

**Deck layout** (see `monomer_example.py` for details):

| Slot | Labware |
|------|--------|
| 1 | 24-well deepwell plate (10 mL) |
| 2 | 96-well deepwell plate (2.2 mL) |
| 3 | 96-well flat bottom plate (360 µL) |
| 6 | 200 µL filter tip rack (P300) |
| 9 | 1000 µL filter tip rack (P1000) |

On error or Ctrl+C, the script discards tips and homes the robot before exiting.

---

# Part 2: Hackathon Challenge

Design, build, and pitch a product for single-cell isolation. Your workflow must:

1. **Dilute and plate** a bead suspension to maximise single-bead wells in a 96-well plate, while minimising empty wells and avoiding multi-bead wells.
2. **Image the plate** using the Cephla Squid microscope to capture per-well fluorescence images.
3. **Classify each well** using an ML pipeline (e.g. `empty`, `single`, `multiple`, `uncertain`).
4. **Upload results to Culture Monitor via MCP**, including per-well labels and flags for wells requiring review.
5. **Support human review**: a scientist should be able to open Culture Monitor, see flagged wells, and record a final QC decision.

### Labeling Wells via the MCP

Use **culture statuses** as your per-well classification labels. The MCP provides:

- `list_culture_statuses()` — discover available statuses (e.g. you might map `empty`, `single`, `multiple`, `uncertain` to custom statuses in your org).
- `update_culture_status(culture_id, status_id, wells)` — apply a status to one or more wells.

Use **comments** to give the reviewing scientist additional context:

- `add_comment(entity_type="culture", entity_id=..., content=...)` — attach a note to a specific culture explaining *why* the algorithm assigned that label, or what the scientist should look out for (e.g. `"Classified as uncertain — two objects detected but one may be debris. Check fluorescence channel."`).

This way the human reviewer opens Culture Monitor, sees the status label at a glance, and can read the comment for details before making a final QC decision.

### Sample Prompt

Once your classification pipeline has produced per-well labels, you can use natural language to prompt the server to assign the appropriate labels and post relevant comments. 

If you're feeling ambitious, you can use a prompt like the following to upload results via the MCP in a single shot:

```
I have classification results for plate <PLATE_BARCODE>. For each well, I have a label
(empty, single, multiple, or uncertain) and a confidence score.

First, use list_culture_statuses() to find the status IDs that correspond to my labels.
Then, for each well:
1. Update the culture status to match the classification label using update_culture_status.
2. For any well classified as "uncertain" or with confidence below 0.8, add a comment to the
   culture explaining what the algorithm detected and what the scientist should verify.

Here are my results:
  A1: single (0.95)
  A2: empty (0.99)
  A3: uncertain (0.62) — two objects detected, one may be debris
  ...
```

## What You Decide

The problem statement defines inputs, outputs, and integration points. Everything in between is yours:

- How do you characterise and validate your seeding density?
- What features does your classifier use, and how do you evaluate it?
- What threshold determines whether a well is flagged vs. automatically accepted?
- How does a reviewer interact with the Culture Monitor upload?
- What are the failure modes of your pipeline, and how would a user know when to distrust it?

## Pitch Format

**30 minutes total: pitch, demo, and judge questions.** How you allocate the time is up to you. You're building and pitching a product, not just a working pipeline.

Your pitch must include a live demo.

## Judging Criteria

| Dimension | Weight |
|---|---|
| Technical execution | 25% |
| Evidence quality | 25% |
| Product clarity | 20% |
| Human-in-the-loop design | 15% |
| Communication | 15% |

## Deliverables

Submit before your pitch slot:

- PyLabRobot protocol file(s)
- Image classification pipeline code and any trained model weights
- Culture Monitor upload script or integration code
- A one-page data summary: runs performed, singles counts, pipeline performance metrics
- Pitch slides or equivalent (PDF)
