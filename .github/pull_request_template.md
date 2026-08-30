## Summary

<!-- Explain the problem and the focused solution. -->

## Related issue

<!-- Link the issue, especially for a major feature, fit model, or format change. -->

## Changes

<!-- List the user-visible and internal changes. -->

## AI assistance

<!--
State "None" or name the AI tool(s), the affected scope, and the human review
and validation performed. Do not paste private prompts or sensitive context.
-->

## Compatibility and user impact

<!--
Describe effects on project files, imports/exports, numerical results, UI text,
supported macOS versions, and existing workflows. Write "None" where applicable.
-->

## Validation

<!-- List exact commands and results. The full local gate is: -->

```bash
bash release_check.sh
```

<!--
For numerical changes, state the independent expected result and numerical
tolerance. Use only synthetic or otherwise safely redistributable fixtures.
-->

## Screenshots

<!-- Add redacted before/after screenshots for visible UI changes, if relevant. -->

## Checklist

- [ ] The change is focused and excludes unrelated formatting or refactoring.
- [ ] `bash release_check.sh` passes in the pinned development environment.
- [ ] New behavior is covered by tests.
- [ ] Material AI assistance is disclosed above, and I understand and reviewed the resulting changes.
- [ ] Numerical changes include independently checkable results and a stated numerical tolerance.
- [ ] Turkish and English resources remain synchronized when UI text changes.
- [ ] Project-file compatibility is preserved or the impact is documented and tested.
- [ ] Documentation and `CHANGELOG.md` are updated when user-visible behavior changes.
- [ ] Fixtures and examples use synthetic or safely redistributable data.
- [ ] No private data, credentials, personal paths, or unredacted logs are included.
- [ ] Security-sensitive details are handled according to [`SECURITY.md`](../SECURITY.md).
- [ ] Every commit contains the required DCO `Signed-off-by` line.
- [ ] I have the right to submit this contribution under `GPL-3.0-only`.
