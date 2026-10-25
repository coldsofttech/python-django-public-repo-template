#!/usr/bin/env python3
"""Apply the standard security settings and the "main" ruleset to a repository.

Usage: scripts/apply_repo_settings.py [owner/repo]   (defaults to the current repo)
Requires: gh CLI authenticated with admin rights on the repository.
"""

import json
import subprocess
import sys
from pathlib import Path

RULESET = Path(__file__).resolve().parent.parent / ".github" / "rulesets" / "main.json"


def gh(*args, payload=None):
    result = subprocess.run(
        ["gh", *args],
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main():
    repo = (
        sys.argv[1]
        if len(sys.argv) > 1
        else gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    )
    print(f"Configuring {repo}")

    # Merge settings: squash only, delete head branches after merge.
    gh(
        "api",
        "-X",
        "PATCH",
        f"repos/{repo}",
        "-F",
        "allow_squash_merge=true",
        "-F",
        "allow_merge_commit=false",
        "-F",
        "allow_rebase_merge=false",
        "-F",
        "delete_branch_on_merge=true",
    )

    # Secret protection (secret scanning + push protection).
    gh(
        "api",
        "-X",
        "PATCH",
        f"repos/{repo}",
        "--input",
        "-",
        payload={
            "security_and_analysis": {
                "secret_scanning": {"status": "enabled"},
                "secret_scanning_push_protection": {"status": "enabled"},
            }
        },
    )

    # Dependency graph is on by default for public repos.
    # Dependabot alerts and security updates.
    gh("api", "-X", "PUT", f"repos/{repo}/vulnerability-alerts")
    gh("api", "-X", "PUT", f"repos/{repo}/automated-security-fixes")

    # CodeQL default setup.
    gh(
        "api",
        "-X",
        "PATCH",
        f"repos/{repo}/code-scanning/default-setup",
        "-f",
        "state=configured",
        "-f",
        "query_suite=default",
    )

    # Let the Init workflow open its pull request.
    gh(
        "api",
        "-X",
        "PUT",
        f"repos/{repo}/actions/permissions/workflow",
        "-f",
        "default_workflow_permissions=read",
        "-F",
        "can_approve_pull_request_reviews=true",
    )

    # Label referenced by .github/release.yml (ignored if it already exists).
    subprocess.run(
        [
            "gh",
            "label",
            "create",
            "skip-changelog",
            "--repo",
            repo,
            "--description",
            "Exclude from release notes",
            "--color",
            "ededed",
        ],
        capture_output=True,
    )

    # "pypi" environment used by release.yml: only version tags may deploy to it.
    if (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "release.yml").exists():
        gh(
            "api",
            "-X",
            "PUT",
            f"repos/{repo}/environments/pypi",
            "--input",
            "-",
            payload={
                "deployment_branch_policy": {
                    "protected_branches": False,
                    "custom_branch_policies": True,
                }
            },
        )
        policies = gh(
            "api",
            f"repos/{repo}/environments/pypi/deployment-branch-policies",
            "-q",
            ".branch_policies[].name",
        ).splitlines()
        if "v*" not in policies:
            gh(
                "api",
                "-X",
                "POST",
                f"repos/{repo}/environments/pypi/deployment-branch-policies",
                "-f",
                "name=v*",
                "-f",
                "type=tag",
            )

    # Ruleset (skips creation if one named "main" already exists).
    names = gh("api", f"repos/{repo}/rulesets", "-q", ".[].name").splitlines()
    if "main" in names:
        print("Ruleset 'main' already exists; skipping")
    else:
        gh("api", "-X", "POST", f"repos/{repo}/rulesets", "--input", str(RULESET))

    print("Done. Complete the manual steps in docs/repo-setup.md.")


if __name__ == "__main__":
    main()
