# Contributing to Sigdraw open-source projects

Thank you for your interest in contributing. This document applies to every
open-source repository in the Sigdraw organization, including Redstone and
Rainglass. Individual repositories may add project-specific instructions in
their README or contributor docs; where they differ, the repository's own
instructions take precedence.

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## The Sigdraw app

The Sigdraw IDE is closed source and is not developed on GitHub. Please send
bug reports and feature requests for the app through
[sigdraw.com/feedback](https://www.sigdraw.com/feedback) rather than opening
issues here. Documentation is at [sigdraw.com/docs](https://www.sigdraw.com/docs).

## Before you start

- **Bugs.** Search existing issues first. If none matches, open a new issue
  with a minimal reproduction.
- **Small changes.** Typo fixes, documentation improvements, and small,
  self-contained bug fixes can go straight to a pull request.
- **Larger changes.** For new features, API changes, significant refactors, or
  anything touching core architecture, open an issue to discuss the approach
  before writing code. This saves time on both sides and avoids work that
  cannot be merged.
- **Security issues.** Do not open a public issue. Follow the
  [security policy](SECURITY.md).

## Pull requests

- Keep pull requests small and focused on a single change. Unrelated fixes
  belong in separate pull requests.
- Reference the related issue in the description, if there is one.
- Add or update tests for any change in behavior.
- Update documentation and doc comments when you change public APIs.
- Be prepared to revise your change in response to review. We may ask you to
  split, rebase, or squash commits before merging.

## Development

Our projects are written in Rust and use the standard Cargo workflow. Before
submitting a pull request, make sure the following pass locally:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```

Continuous integration will run the same checks. Some repositories require
additional tooling, a specific toolchain, or extra test suites; check the
repository's README for details.

General conventions:

- Format code with `rustfmt` using the repository's configuration.
- Avoid introducing new `clippy` warnings. If a lint must be allowed, scope the
  `#[allow(...)]` as narrowly as possible and explain why.
- Avoid adding new dependencies without discussion.
- Avoid `unsafe` unless it is necessary; document the invariants that make each
  `unsafe` block sound.

## Commit messages

- Write a short summary line in the imperative mood, around 50 characters,
  for example: `Fix X propagation in case statements`.
- Separate the summary from the body with a blank line.
- Use the body to explain what changed and why, wrapped at about 72
  characters.
- Reference issues where relevant, for example `Fixes #123`.

## Developer Certificate of Origin

All contributions must be signed off under the
[Developer Certificate of Origin](https://developercertificate.org/) (DCO).
The DCO is a lightweight way for you to certify that you wrote, or otherwise
have the right to submit, the code you are contributing.

To sign off, add a `Signed-off-by` line to every commit message, using your
real name and an email address you control:

```
Signed-off-by: Jane Doe <jane.doe@example.com>
```

Git adds this line for you when you commit with `-s`:

```sh
git commit -s -m "Fix X propagation in case statements"
```

Pull requests with commits that are missing a sign-off cannot be merged.

### Fixing a missing sign-off

To add a sign-off to your most recent commit:

```sh
git commit --amend --no-edit -s
git push --force-with-lease
```

To add sign-offs to every commit on your branch (replace `main` with the
branch you are targeting):

```sh
git rebase --signoff main
git push --force-with-lease
```

## Licensing

Unless a repository states otherwise, Sigdraw open-source projects are
dual-licensed under either of

- the Apache License, Version 2.0 (`LICENSE-APACHE` in each repository, or
  <https://www.apache.org/licenses/LICENSE-2.0>), or
- the MIT license (`LICENSE-MIT` in each repository, or
  <https://opensource.org/licenses/MIT>),

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.

## Questions

For questions about contributing, open an issue or discussion on the relevant
repository. For anything else, see [SUPPORT.md](SUPPORT.md) or email
[hello@sigdraw.com](mailto:hello@sigdraw.com).
