# abx-release-example

Example Python project that uses
[abx-release-tools](https://github.com/mongodb-labs/abx-release-tools).
The project is a demo, not production code.

The release workflows use MongoDB internal release infrastructure:
Garasign, Kondukto, and the release S3 bucket. They do not run outside
MongoDB. Use this repo to read how the actions fit together.

The workflows call every action in the tools repo, in the order the
[documentation](https://github.com/mongodb-labs/abx-release-tools/tree/main/docs)
gives.

## Workflows

| Workflow | Trigger | Actions | Needs AWS |
| --- | --- | --- | --- |
| `ci.yml` | Push to `main`, pull request | `python/generate-sbom` | No |
| `release.yml` | Manual dispatch | `setup`, `python/generate-sbom`, `sbom`, `gpg-sign`, `authorized-pub`, `upload-s3-assets`, `python/publish` | Yes |
| `sign-tag.yml` | Manual dispatch | `setup`, `git-sign` | Yes |

`ci.yml` runs the tests on Python 3.10 to 3.13, builds the
distributions, and generates `sbom.json`. It runs without secrets.

`release.yml` builds, signs, traces, and publishes a release. Run
`sign-tag.yml` to sign the release tag. Sign the tag first, then
release.

## Prerequisites

Both release workflows use the GitHub environment `release`. Create it
in the repository settings before you run them.

### AWS

Set these environment secrets:

| Secret | Value |
| --- | --- |
| `AWS_ROLE_ARN` | Role that can read the release secret and assume the ECR pull role |
| `AWS_SECRET_ID` | Name or ARN of the AWS Secrets Manager secret |

Set this environment variable:

| Variable | Value |
| --- | --- |
| `AWS_REGION_NAME` | Region of the secret, for example `us-east-1` |

The AWS secret holds these JSON keys:

| Key | Required | Use |
| --- | --- | --- |
| `GARASIGN_USERNAME` | Yes | Garasign login |
| `GARASIGN_PASSWORD` | Yes | Garasign password |
| `GPG_KEY_ID` | Yes | Signing key |
| `KONDUKTO_TOKEN` | Yes | SBOM augmentation |
| `RELEASE_ASSETS_BUCKET` | Yes | Release S3 bucket |
| `GPG_PUBLIC_URL` | No | Public key URL |
| `SECURITY_REPORT_URL` | No | Security report URL |

### PyPI

Register a pending publisher for `abx-release-example` on pypi.org. Use
these values:

| Field | Value |
| --- | --- |
| Owner | `aclark4life` |
| Repository | `abx-release-example` |
| Workflow | `release.yml` |
| Environment | `release` |

The publish job needs `id-token: write`. The workflow sets it.

## Run

1. Sign a tag:

   ```shell
   gh workflow run sign-tag.yml -f tag=v0.1.0
   ```

2. Release the version:

   ```shell
   gh workflow run release.yml -f version=0.1.0
   ```

## Layout

```
src/abx_example/       The package
tests/                 The tests
requirements.txt       Pinned release dependencies; the SBOM input
pyproject.toml         Package metadata
.github/workflows/     CI, release, and tag signing
```

## Notes

- `setup` must run before `sbom`, `gpg-sign`, `authorized-pub`, and
  `upload-s3-assets`. It writes `RELEASE_ASSETS`, `S3_ASSETS`,
  `GARASIGN_ENVFILE`, `KONDUKTO_ENVFILE`, and `AWS_BUCKET`.
- `python/generate-sbom` runs before `sbom`. The `sbom` action reads
  `sbom.json`; it does not make one.
- `authorized-pub` runs before `upload-s3-assets`. The first writes
  `authorized-publication.txt` to the S3 assets; the second uploads
  that directory.
- The actions are pinned to a commit SHA. Update the SHA to take a new
  version of the tools.
- Verify a signature against the public key named in `GPG_PUBLIC_URL`:

  ```shell
  gpg --verify abx_release_example-0.1.0-py3-none-any.whl.sig \
      abx_release_example-0.1.0-py3-none-any.whl
  ```
