#!/usr/bin/env bash

# Obtain the organizations (private or public) that this GitHub user is in. This function reads implicitly the
# GITHUB_TOKEN variable to know from which user we are listing organizations. It also reads GITHUB_TOKEN for
# authentication, since it lists both private and public organizations.
list_organizations()
{
  gh api -H "Accept: application/vnd.github+json" /user/orgs --jq ".[].login"
}

# Obtain the repositories of the GitHub user from $1. It reads GITHUB_TOKEN for authentication, since it lists both
# private and public repositories.
list_user_repos()
{
  gh api "/users/$1/repos" | jq -r '.[].full_name'
}

# Obtain the GitHub repositories of the organization in $1. It reads GITHUB_TOKEN for authentication, since it lists
# both private and public repositories.
list_org_repos()
{
  gh api "/orgs/$1/repos" | jq -r '.[].full_name'
}

# Clones the repo supplied in $1 in the path $2. It reads GITHUB_TOKEN for authentication, since it clones both private
# and public repositories.
clone_repo()
{
  git clone "https://github.com/$1" "$2"
}

# - Receives a single github username or organization via $1
# - Creates a folder for its backup with the same name as $1
# - Lists the organization that the user is in and writes them into $1/organizations.txt
# - Creates a sub folder in the $1 for each organization that the user is in and for itself
# - Lists the repositories of each organization and the user itself (NAME) and write them into $1/NAME/repositories.txt
# - Clone all repos of each organization and user (NAME) in its sub folder ${BACKUP_FOLDER}/$1/NAME/REPO
do_backup()
{
  # create backup folder for the user in $1
  mkdir -p "${BACKUP_FOLDER}/$1"

  # Save the organizations that the user is in into a text file with the same name as the github user and
  # "_organizations" at the end, for example if my name is JohnDoe, save it to a file called "JohnDoe_organizations.txt"
  list_organizations > "${BACKUP_FOLDER}/$1/organizations.txt"

  # Save user repos into a text file with the same name as the github user and the same name and "_repositories" at the
  # end, for example, if my name if JohnDoe, save it to a file called "JohnDoe_JohnDoe_repositories.txt".
  list_user_repos "$1" > "${BACKUP_FOLDER}/$1/$1/repositories.txt"

  # that this user is in and save them into a text file. For
  # example, if the user JohnDoe is in the "FooBar" organization, save each repository of the "FooBar" organization into
  # a text file called "JohnDoe_FooBar_repositories.txt"
  while IFS= read -r org; do
    list_org_repos "${org}" > "${BACKUP_FOLDER}/$1/${org}/repositories.txt"
  done < "${BACKUP_FOLDER}/$1/organizations.txt"

  # Read all repository list text files with a wild card such as cat "JohnDoe_*_repositories.txt" and iterate over each
  # line and issue a clone of that repository, clone it inside the "backup" folder
  for file in "${BACKUP_FOLDER}/$1/"*"/repositories.txt"; do
    while IFS= read -r repo; do
      echo $repo $file
      echo "${BACKUP_FOLDER}/$(echo "${file}" | cut -d "_" -f2)/$(basename "${repo}")"
      clone_repo "${repo}" "${BACKUP_FOLDER}/$(echo "${file}" | cut -d "_" -f2)/$(basename "${repo}")"
    done < "${file}"
  done
}

main()
{
  # Check if $1 is present.
  if [ -z $1 ]; then
    echo "Error: This program needs at least one argument. Aborting."
    exit 1
  fi

  # Check if the user in $1 exists in github, if it does not exist exit program showing error message.
  gh api "/users/$1" &>/dev/null
  if [ $? -ne 0 ]; then
    echo "Error: GitHub user '$1' not found. Aborting."
    exit 1
  fi

  # Check if the token GITHUB_TOKEN exists, if it does not exist exit program showing error message.
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token not found. Set the environment variable GITHUB_TOKEN with your GitHub token."
    exit 1
  fi

  # Create and set mount point folder. The place where we are putting the final compressed file of the backup.
  MOUNT_POINT="${PROJECT_FOLDER}/backup"
  mkdir -p "${MOUNT_POINT}"

  # Create and set backup folder.
  BACKUP_FOLDER="${PROJECT_FOLDER}/backup/content"
  mkdir -p "${BACKUP_FOLDER}"

  # Do backup for all user and organizations supplied in the arguments
  for arg in "$@"
  do
    do_backup ${arg}
  done

  # Compress the backup folder
  tar -czvf "${MOUNT_POINT}/backup.tar.gz" ${BACKUP_FOLDER}
}


export PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")" &>/dev/null && pwd)"
main $@