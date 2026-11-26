# Research note: emergency access on a third-party terminal

*Not part of the L-euro specification. Capitalised key words do not apply here. Kept as a research topic; if it were ever adopted, the template would be stored at the depositary, which the specification currently excludes (spec §7.2, §11).*

Purpose: let a holder without their own device reach their account once, at
an acceptor, with a fingerprint.

- Phone operating systems do not give apps the fingerprint image. The built-in
  sensor only confirms the device owner. Emergency access therefore needs an
  **external certified sensor** attached to an acceptor terminal that runs the
  L-euro app.
- The sensor should have presentation attack detection (ISO/IEC 30107-3) and
  must encrypt its output to the depositary key, so that neither the terminal
  nor its operating system sees the raw image.
- The terminal app must prove its integrity (Play Integrity / App Attest) and
  be registered to an acceptor.
- The depositary stores only a protected, revocable template (ISO/IEC 24745).
  Matching uses challenge–response, so a recorded response cannot be replayed.
- Each use must also require a holder PIN, must be capped at a low amount set
  by the programme, and must be single-use until the holder re-binds a device.
- Templates are special-category data (GDPR art. 9): opt-in with explicit
  consent and a data protection impact assessment are required.

Open: sensor certification profile; template protection scheme; DPIA.
