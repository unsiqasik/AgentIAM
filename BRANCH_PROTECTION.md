# Branch Protection Configuration

To ensure the integrity of the `main` branch, the following rules should be manually configured in GitHub Settings.

## Access Settings
1. Navigate to **Settings** → **Branches**.
2. Click **Add branch protection rule**.
3. Set **Branch name pattern** to `main`.

## Required Rules

### Protect Matching Branches
- [x] **Require a pull request before merging**
    - [x] **Require approvals**: 1
    - [x] **Dismiss stale pull request approvals when new commits are pushed**
    - [x] **Require review from Code Owners**
- [x] **Require status checks to pass before merging**
    - [x] **Require branches to be up to date before merging**
    - **Status checks that must pass**:
        - `lint`
        - `security`
        - `type-check`
        - `test (3.10)`
        - `test (3.11)`
        - `test (3.12) `
        - `test (3.13)`
- [x] **Require conversation resolution before merging**
- [x] **Lock branch** (optional, prevents all pushes)
- [x] **Restrict pushes** (optional, restricts who can push to the branch)

### Rules Applied to Everyone
- [x] **Require signed commits** (Recommended for enterprise-grade security)
- [x] **Require linear history**
- [x] **Include administrators**
- [x] **Allow force pushes**: [ ] (Unchecked)
- [x] **Allow deletions**: [ ] (Unchecked)

## Automation
The repository has been configured with GitHub Actions to automatically run these checks on every Pull Request.
