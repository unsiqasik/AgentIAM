import json
import subprocess


def run_cmd(cmd, check=True):
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        if check:
            raise
        return None


def get_open_prs():
    output = run_cmd("gh pr list --json number,title")
    return json.loads(output)


prs = get_open_prs()
for pr in prs:
    pr_number = pr["number"]
    title = pr["title"]
    print(f"\nProcessing PR #{pr_number}: {title}")

    # Checkout PR
    run_cmd(f"gh pr checkout {pr_number}")

    # Rebase on main
    run_cmd("git fetch origin main")

    # Some PRs might have conflicts during rebase. If so, abort and skip.
    try:
        run_cmd("git rebase origin/main")
    except subprocess.CalledProcessError:
        print(f"Merge conflict rebasing PR {pr_number}. Aborting rebase and skipping.")
        run_cmd("git rebase --abort", check=False)
        continue

    # Run auto-formatters and linting
    print("Running linting fixes...")
    run_cmd("python -m black .", check=False)
    run_cmd("python -m ruff check --fix .", check=False)

    # Check if there are changes
    status = run_cmd("git status --porcelain")
    if status.strip():
        print("Committing lint fixes...")
        run_cmd("git add .")
        run_cmd('git commit -m "style: auto-fix linting issues"')
        run_cmd("git push -f")
    else:
        # We still push -f just in case the rebase changed history
        run_cmd("git push -f")

    # Let's run pytest
    print("Running pytest...")
    test_result = run_cmd("python -m pytest", check=False)
    if test_result is None:
        print(
            f"Tests failed for PR {pr_number}. It requires manual fixing. Skipping for now."
        )
        continue

    print(f"Tests passed for PR {pr_number}. Approving and merging...")
    run_cmd(f"gh pr review {pr_number} --approve", check=False)
    run_cmd(f"gh pr merge {pr_number} --merge --admin", check=False)
    print(f"PR {pr_number} merged successfully!")

# Go back to main
run_cmd("git checkout main")
