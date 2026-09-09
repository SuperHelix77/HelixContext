# Existing command-wrapper qualification

The unchanged evidence.py CLI captured the same 9,200,129-byte fixture used in the Spark/Luna native audit. Two local subprocess runs exited 0 and 7. Each returned a 2,002-byte JSON packet, preserved the requested exit status, retained byte-identical full stdout, passed independent packet verification, and recovered the exact middle sentinel by line reference.

The prior native command item omitted that middle sentinel. This wrapper captures bytes before that native item boundary. The comparison establishes exact preservation by the wrapper, not native hook replacement or model-token savings. No native model call, hook registration or installed skill change was made.

## Accounting

Both captures took about 0.18 seconds locally in this run. Each retained 18,401,679 logical file bytes, including staging and archive copies. Full-source verification/retrieval costs are reported separately in RESULT.json. These are not physical disk measurements. Parent inference, OS metadata and remote inference costs are not included.

The source fixture hash and executed evidence.py hash are recorded. The raw fixture remains in the original local audit evidence. This receipt is not an independent holdout or a full environment freeze.

## Next gate

Do not extrapolate the byte ratio to an 80% native saving. Native command event size is not model-facing context size. A subsequent bounded joint experiment must measure actual input/output usage and include interface discovery, source checking, fallback, repeated history and required artifact delivery. Ordinary execution may already truncate output or inspect only relevant lines; it remains the efficient comparator.

The preservation result admits the wrapper for further integration research. It does not admit a model-specific compression policy for deployment or establish Q/A/W parity.
