"""
Collect some numbers for conda-forge:

* Maintainers
* Number of people in core (active, emeritus)
* Number of staged-recipes reviewers
* Number of repositories (and feedstocks)
* Number of output packages (a feedstock can produce more than one package name)
* Number of artifacts (a package name will have several builds)
* Number of supported platforms
* Number of total commits in the organization (number of commits made by bots)
* Number of issues and PRs
* Total storage used at Anaconda.org
* Number of downloads and bandwidth used
* Number of CI runs
"""

import os
import json

import requests
from conda_forge_metadata.repodata import SUBDIRS, n_artifacts, all_labels
from github import Github


GH_TOKEN = os.environ["GITHUB_TOKEN"]


def _gh_api_query_total_count(query, **kwargs):
    r = requests.get(
        f"https://api.github.com/{query}",
        headers={"Authorization": f"token {GH_TOKEN}"},
        **kwargs
    )
    r.raise_for_status()
    data = r.json()
    try:
        return data["total_count"]
    except KeyError:
        print("ERROR!\n", data)
        raise


def github_data():
    print("Initializing for Github...")

    gh = Github(GH_TOKEN)
    org = gh.get_organization("conda-forge")
    # get creation date
    print("Getting creation date...")
    created = str(org.created_at)

    # get number of members
    print("Getting members...")
    n_members = org.get_members().totalCount
    members_core = set(m.login for m in org.get_team_by_slug("Core").get_members())
    n_members_core = len(members_core)
    members_staged_recipes = set(
        m.login
        for m in org.get_team_by_slug("staged-recipes").get_members()
    )
    n_members_staged_recipes = sum(
        1
        for login in members_staged_recipes
        if login not in members_core
    )

    with open("data/live_counts.json", "r") as f:
        data = json.load(f)

    # get number of issues and PRs - we need to use requests directly here,
    # pygithub says totalCount is 1000 ??
    print("Getting issues / PRs...")
    try:
        n_open_issues = _gh_api_query_total_count(
            "search/issues",
            params={"q": "org:conda-forge type:issue state:open"}
        )
        n_closed_issues = _gh_api_query_total_count(
            "search/issues",
            params={"q": "org:conda-forge type:issue state:closed"},
        )
    except Exception as e:
        print("ERROR!\n", repr(e))
        n_open_issues = data["n_open_issues"]
        n_closed_issues = data["n_closed_issues"]

    try:
        n_open_prs = _gh_api_query_total_count(
            "search/issues",
            params={"q": "org:conda-forge type:pr state:open"},
        )
        n_closed_prs = _gh_api_query_total_count(
            "search/issues",
            params={"q": "org:conda-forge type:pr state:closed"},
        )
    except Exception as e:
        print("ERROR!\n", repr(e))
        n_open_prs = data["n_open_prs"]
        n_closed_prs = data["n_closed_prs"]

    with open("data/download_counts.json", "r") as fp:
        dnlds = json.load(fp)

    data.update({
        "created_at": created,
        "n_members": n_members,
        "n_members_core": n_members_core,
        "n_members_staged_recipes": n_members_staged_recipes,
        "n_repos": org.public_repos,
        "n_issues": n_open_issues + n_closed_issues,
        "n_open_issues": n_open_issues,
        "n_closed_issues": n_closed_issues,
        "downloads": dnlds,
    })
    if (n_open_prs + n_closed_prs) >= data["n_prs"]:
        data.update({
            "n_prs": n_open_prs + n_closed_prs,
            "n_open_prs": n_open_prs,
            "n_closed_prs": n_closed_prs,
        })

    return data


def repodata_data():
    print("Getting artifacts...")
    artifacts, packages = n_artifacts(labels=all_labels(use_remote_cache=False))
    return { 
        "n_artifacts": artifacts,
        "n_packages": packages,
        "n_platforms": len(SUBDIRS) - 1,  # noarch is not a platform
    }


def cache_labels():
    print("Caching labels...")
    labels = all_labels(use_remote_cache=False)
    with open("data/labels.json", "w") as f:
        json.dump(labels, f, indent=2)


def main():
    cache_labels()
    data = {
        **github_data(),
        **repodata_data(),
        # Missing fields - WIP
        "n_commits": None,
        "n_commits_bots": None,
    }
    with open("data/live_counts.json", "w") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))

    return data


if __name__ == "__main__":
    main()
