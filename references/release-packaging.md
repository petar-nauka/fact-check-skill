# Release Packaging

Do not commit generated `.zip` or `.skill` artifacts as source files. Keep the
repository focused on the skill source:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `schema/`
- `tests/`

Use releases for distributable artifacts. A typical release flow:

1. Run validation and tests.
2. Build the package with `scripts/package_skill.py`.
3. Attach the generated package from `dist/` to the tagged release.
4. Keep source and generated artifacts separate.

The package script excludes tests, cache directories, previous packages, and local
output by default. Include tests only for development bundles.
