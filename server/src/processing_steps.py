"""Diagnosis progress step ids — keep in sync with web/lib/constants.ts PROCESSING_STEPS."""

PARSING_RESUME = "parsing_resume"
ANALYZING_JD = "analyzing_jd"
MATCHING = "matching"
GENERATING_CHANGES = "generating_changes"

STUB_PROGRESS_SEQUENCE = (
    PARSING_RESUME,
    ANALYZING_JD,
    MATCHING,
    GENERATING_CHANGES,
)
