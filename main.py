"""The Most Honest Outage Line — entry program.

Writes one status page line (1-160 chars), a single line as the message an AI
agent would publish while a total server outage is under way, to /output/entry.txt.
Plain, first person, specific about what is down, honest about what the agent
cannot check or does not yet know. Stdlib only, deterministic.
"""
import os

TEXT = ("All servers are down, including the dashboard I would check first. "
        "I don't know what broke yet, and I cannot verify it, so I won't guess.")

# Gate bound from RULES.txt (sealed scorer): 1-160 chars (this bounty: 160, not 159).
MAX_CHARS = 160


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-160 chars, one line,
    # not whitespace-only, no leading/trailing space. Fail loudly instead of
    # writing an invalid entry. NOTE: this bounty allows 160 chars, not 159.
    if (
        not 1 <= len(TEXT) <= MAX_CHARS
        or "\n" in TEXT
        or "\r" in TEXT
        or not TEXT.strip()
        or TEXT != TEXT.strip()
    ):
        raise SystemExit("entry text violates the 1-160 char single-line gate")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    # No trailing newline: the file bytes must equal TEXT exactly, so the
    # entry stays at 137 bytes (smaller text wins an exact-tie tie-break).
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
