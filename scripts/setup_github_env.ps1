$ErrorActionPreference = "Stop"

# Setup Labels
$labels = @(
    # Difficulty
    @{"name"="difficulty:beginner"; "color"="0052cc"; "description"="Good for brand new contributors"}
    @{"name"="difficulty:easy"; "color"="0e8a16"; "description"="Good for beginners"}
    @{"name"="difficulty:medium"; "color"="fbca04"; "description"="Intermediate difficulty"}
    @{"name"="difficulty:hard"; "color"="d93f0b"; "description"="Advanced difficulty"}
    @{"name"="difficulty:expert"; "color"="b60205"; "description"="Expert level knowledge required"}
    
    # Category
    @{"name"="category:backend"; "color"="c2e0c6"}
    @{"name"="category:frontend"; "color"="c2e0c6"}
    @{"name"="category:database"; "color"="c2e0c6"}
    @{"name"="category:api"; "color"="c2e0c6"}
    @{"name"="category:security"; "color"="c2e0c6"}
    @{"name"="category:testing"; "color"="c2e0c6"}
    @{"name"="category:documentation"; "color"="c2e0c6"}
    @{"name"="category:performance"; "color"="c2e0c6"}
    @{"name"="category:devops"; "color"="c2e0c6"}
    @{"name"="category:architecture"; "color"="c2e0c6"}
    @{"name"="category:ai"; "color"="c2e0c6"}
    @{"name"="category:integrations"; "color"="c2e0c6"}
    @{"name"="category:observability"; "color"="c2e0c6"}
    @{"name"="category:ui"; "color"="c2e0c6"}
    @{"name"="category:ux"; "color"="c2e0c6"}

    # Priority
    @{"name"="priority:critical"; "color"="b60205"}
    @{"name"="priority:high"; "color"="d93f0b"}
    @{"name"="priority:medium"; "color"="fbca04"}
    @{"name"="priority:low"; "color"="0e8a16"}

    # Status
    @{"name"="status:ready"; "color"="0e8a16"}
    @{"name"="status:blocked"; "color"="d93f0b"}
    @{"name"="status:needs-discussion"; "color"="fbca04"}
    @{"name"="status:research"; "color"="5319e7"}

    # Contributor
    @{"name"="good-first-issue"; "color"="7057ff"}
    @{"name"="help-wanted"; "color"="008672"}
    @{"name"="mentor-available"; "color"="0052cc"}

    # Type
    @{"name"="type:bug"; "color"="d73a4a"}
    @{"name"="type:feature"; "color"="a2eeef"}
    @{"name"="type:refactor"; "color"="ff9f1c"}
    @{"name"="type:enhancement"; "color"="a2eeef"}
    @{"name"="type:security"; "color"="d73a4a"}
    @{"name"="type:maintenance"; "color"="ff9f1c"}
    @{"name"="type:research"; "color"="d4c5f9"}
)

Write-Host "Creating Labels..."
foreach ($l in $labels) {
    gh label create $l.name --color $l.color --description $($l.description -replace '^$','') --force
}

# Setup Milestones
$milestones = @("MVP", "v0.2", "v0.3", "v0.4", "v0.5", "v1.0", "Future")
Write-Host "Creating Milestones..."
# Note: `gh api` doesn't have a simple wrapper for milestones, so we use `gh api`
# We need the repository details
$repo = gh repo view --json owner,name --jq '"{owner}/{name}"'
if (-not $repo) {
    $repo = (git config --get remote.origin.url) -replace '.*github.com[:/](.*?)\.git', '$1'
}

foreach ($m in $milestones) {
    # Check if exists
    $exists = gh api repos/$repo/milestones -X GET -F state=all --jq ".[] | select(.title == `"$m`") | .title"
    if (-not $exists) {
        gh api repos/$repo/milestones -X POST -f title="$m"
    }
}
Write-Host "GitHub Environment Setup Complete."
