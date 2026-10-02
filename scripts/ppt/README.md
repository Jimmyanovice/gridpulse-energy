# Local presentation build dependency

Run `npm run ppt:setup` once on a machine that has Codex's locally supplied presentation package available. This places `@oai/artifact-tool` in this repository's `node_modules` for local development.

`@oai/artifact-tool` is a private, bundled Codex package rather than a public npm package. It is deliberately installed without saving an absolute machine path to `package.json`. The repository therefore does not attempt to publish or vendor the package.

Use `npm run ppt:build` to build the deck and `npm run ppt:finalize` to run the local finalization flow. The package and all generated local build artifacts are ignored by Git.
