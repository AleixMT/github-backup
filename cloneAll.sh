#!/usr/bin/env bash

main()
{
  # Check if $1 is present

  # Check if the user in $1 exists in github, if it does not exist exit program showing error message
  gh api "/users/$1" &>/dev/null
  if [ $? -ne 0 ]; then
    echo "Error: GitHub user '$1' not found."
    exit 1
  fi

  # Check if the token GITHUB_TOKEN exists, if it does not exist exit program showing error message
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token not found. Set the environment variable GITHUB_TOKEN with your GitHub token."
    exit 1
  fi

  # create backup folder
  mkdir -p "${PROJECT_FOLDER}/backup"

  # Obtain the organizations (private or public) that this github user is in and save the list into a text file with the
  # same name as the github user and "_organizations" at the end, for example if my name is JohnDoe, save it to a file
  # called "JohnDoe_organizations.txt"
  gh api -H "Accept: application/vnd.github+json" /user/orgs --jq ".[].login" > "backup/$1_organizations.txt"

  # Obtain the repositories of the profile of this user and save them into a text file with the same name as the github
  # user and the same name and "_repositories" at the end, for example, if my name if JohnDoe, save it to a file called
  # "JohnDoe_JohnDoe_repositories.txt"
  gh api "/users/$1/repos" | jq -r '.[].full_name' > "backup/$1_$1_repositories.txt"

  # Obtain the repositories of each of the organizations that this user is in and save them into a text file. For
  # example, if the user JohnDoe is in the "FooBar" organization, save each repository of the "FooBar" organization into
  # a text file called "JohnDoe_FooBar_repositories.txt"
  while IFS= read -r org; do
    gh api "/orgs/${org}/repos" | jq -r '.[].full_name' > "backup/$1_${org}_repositories.txt"
  done < "backup/$1_organizations.txt"

  # Read all repository list text files with a wild card such as cat "JohnDoe_*_repositories.txt" and iterate over each
  # line and issue a clone of that repository, clone it inside the "backup" folder
  mkdir -p backup
  for file in "backup/$1_"*"_repositories.txt"; do
    while IFS= read -r repo; do
      echo $repo $file
      git clone "https://github.com/${repo}" "backup/$(echo "${file}" | cut -d "_" -f2)/$(basename "${repo}")"
    done < "${file}"
  done

  # Compress the backup folder and write the name with the current date on it.
}



export PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")" &>/dev/null && pwd)"
main $@