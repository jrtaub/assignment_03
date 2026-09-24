"""
process_files.py — Part 3: many files, one after another, with a running total.

The same job as process_file.py, but the app now remembers what it has already
done: how many files have been processed, how many packages that came to, and a
one-line summary of each file — and it keeps remembering across uploads.

That is the hard part, and it is hard for a specific reason: every interaction
reruns this whole script from the top, so an ordinary variable like
`files_processed = 0` is reset to zero on every rerun. Anything that has to
survive a rerun lives in `st.session_state` instead, and is initialised only
once — the first time the script runs.

The other trap is the uploader itself. Once a file has been chosen it stays
chosen on every rerun, so an app that processes "whenever there is a file" would
count the same file again on every interaction. Processing happens on a button
click instead: `st.button` is True only on the one rerun the click caused.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k process_files
"""

# --- The page ---------------------------------------------------------------------
#
# No scaffolding. You have written two of these now, and this one does the same
# processing as process_file.py — the difference is that it remembers.
#
# What you have to work out for yourself:
#
#   - the three parts of the session-state pattern: initialise once, update on the
#     click, display from state — README Reference #6
#   - a button, key="process", so that choosing a file and clicking are two
#     different things
#   - two st.metric cards, "Files processed" and "Packages processed", side by side
#     in st.columns(2), on the page from the first run
#   - one st.info line per file processed so far, kept in a list
#
# README Step 7 names the two traps. The tests are built around them: choosing a
# file without clicking must change nothing, and a rerun with the same file still
# chosen must not count it again.
import streamlit as st
import json
import os
from packaging_parser import calc_total_units, get_unit, parse_packaging    

st.title("Process Package Files")

# Initialize session state only once
st.session_state.setdefault("files_processed", 0)
st.session_state.setdefault("packages_processed", 0)
st.session_state.setdefault("file_summaries", [])

uploaded_file = st.file_uploader("Upload a package description file", type=["txt"], key="package_file")

process_clicked = st.button("Process file", key="process")

# Optional: Reset button to clear stats and summaries
if st.button("Reset all"):
    st.session_state["files_processed"] = 0
    st.session_state["packages_processed"] = 0
    st.session_state["file_summaries"] = []

if process_clicked and uploaded_file is not None:
    # Decode and split lines from uploaded bytes
    content = uploaded_file.read().decode("utf-8")
    lines = content.splitlines()

    parsed_packages = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parsed = parse_packaging(line)
        parsed_packages.append(parsed)

    # Prepare output JSON path
    filename = uploaded_file.name.replace(".txt", ".json")
    output_path = f"data/{filename}"
    os.makedirs("data", exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(parsed_packages, f, indent=2)

    # Update session state totals and summaries
    st.session_state["files_processed"] += 1
    st.session_state["packages_processed"] += len(parsed_packages)
    summary_line = f"{len(parsed_packages)} packages written to {output_path}"
    st.session_state["file_summaries"].append(summary_line)

# Show metrics side by side
col1, col2 = st.columns(2)
col1.metric("Files processed", st.session_state["files_processed"])
col2.metric("Packages processed", st.session_state["packages_processed"])

# Show all summary lines (one per file processed)
for summary in st.session_state["file_summaries"]:
    st.info(summary)