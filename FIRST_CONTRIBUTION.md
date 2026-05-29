# Making Your First Contribution

Welcome! We're thrilled that you're interested in contributing to AgentIAM. This guide will walk you through making your first pull request.

## Step 1: Find an Issue
Head over to the [GitHub Issues](../../issues) page and look for issues labeled `good-first-issue` or `difficulty:beginner`. These are specifically selected to be self-contained and approachable.

## Step 2: Fork and Clone
1. Click the "Fork" button in the top right corner of this repository.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/AgentIAM.git
   cd AgentIAM
   ```

## Step 3: Branch
Create a new branch for your work. Use a descriptive name:
```bash
git checkout -b fix-policy-validation
```

## Step 4: Setup Environment
Follow the instructions in [DEVELOPMENT.md](DEVELOPMENT.md) to set up the backend or frontend environment, depending on what your issue requires.

## Step 5: Make Your Changes
Write your code! Remember to:
- Write clear, concise commit messages.
- Follow the existing code style.
- Add tests if applicable.

## Step 6: Test
Run the test suite to ensure nothing is broken.
```bash
cd backend
PYTHONPATH=. pytest
```

## Step 7: Push and Pull Request
1. Push your branch to your fork:
   ```bash
   git push origin fix-policy-validation
   ```
2. Go to the original AgentIAM repository and click "Compare & pull request".
3. Fill out the PR template. Mention the issue you're fixing (e.g., "Fixes #12").

## Need Help?
If you get stuck, don't hesitate to ask for help on the issue thread! Our maintainers (look for the `mentor-available` label) are happy to assist.
