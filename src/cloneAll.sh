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

# - Receives a single github username or organization via $1.
# - Creates a folder for its backup with the same name as $1.
# - Lists the organization that the user is in and writes them into "${BACKUP_FOLDER}/$1/organizations.txt".
# - Creates a sub folder in the $1 for each organization that the user is in and for itself.
# - Lists the repositories of each organization and the user itself (NAME) and write them into
#   "$1/NAME/repositories.txt".
# - Clone all repos of each organization and user (NAME) in its sub folder "${BACKUP_FOLDER}/$1/NAME/REPO".
do_backup()
{
  # Create backup folder for the user in $1.
  mkdir -p "${BACKUP_FOLDER}/$1"

  # Save the organizations that the user is in into a text file with the same name as the github user and
  # "_organizations" at the end, for example if my name is JohnDoe, save it to a file called
  # "JohnDoe_organizations.txt".
  list_organizations > "${BACKUP_FOLDER}/$1/organizations.txt"

  # Save user repos into a text file with the same name as the github user and the same name and "_repositories" at the
  # end, for example, if my name if JohnDoe, save it to a file called "JohnDoe_JohnDoe_repositories.txt".
  mkdir -p "${BACKUP_FOLDER}/$1/$1"
  list_user_repos "$1" > "${BACKUP_FOLDER}/$1/$1/repositories.txt"

  # Clone all the repos of the $1 user.
  while IFS= read -r repo; do
    clone_repo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
  done < "${BACKUP_FOLDER}/$1/$1/repositories.txt"

  # List repos of the organizations that this user is in and save them into a text file into
  # "${BACKUP_FOLDER}/$1/ORGANIZATION/repositories.txt". Then, clone each of the repositories in
  # "${BACKUP_FOLDER}/$1/ORGANIZATION/REPO"
  while IFS= read -r org; do
    mkdir -p "${BACKUP_FOLDER}/$1/${org}"
    list_org_repos "${org}" > "${BACKUP_FOLDER}/$1/${org}/repositories.txt"
    while IFS= read -r repo; do
      echo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
      clone_repo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
    done < "${BACKUP_FOLDER}/$1/${org}/repositories.txt"
  done < "${BACKUP_FOLDER}/$1/organizations.txt"
}

main()
{
  # Check if $1 is present.
  if [ -z "$1" ]; then
    echo "Error: This program needs at least one argument. Aborting."
    exit 1
  fi

  # Check the authentication status with GitHub
  if [ -z "$GITHUB_TOKEN" ]; then
    # Check the exit status of the previous command
    if ! gh auth status; then
      # Check if the token GITHUB_TOKEN exists, if it does not exist exit program showing error message.
      echo "ERROR: GitHub token not found and user is not authenticated in gh command.
If you are using this script in a workflow set the environment variable GITHUB_TOKEN with your GitHub token for
the authentication. You can do so by declaring it in your environment variables, in your bashrc or by setting it
before calling the script:

GITHUB_TOKEN=\"your_github_secret_token\" ./cloneAll.sh

If you are using this script in a user environment you can also issue the command \"gh auth login\" to provide the
authentication."
      exit 1
    fi
  fi

  # Check if the user in $1 exists in github, if it does not exist exit program showing error message.
  if ! gh api "/users/$1" > /dev/null; then
    echo "ERROR: Could not use GitHub API due to missing or wrong authentication GitHub user '$1' not found. Aborting."
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
    do_backup "${arg}"
  done

  # Compress the backup folder
  tar -czvf "${MOUNT_POINT}/backup.tar.gz" -C "$(dirname "${BACKUP_FOLDER}")" "$(basename "${BACKUP_FOLDER}")"

  # Remove content
  rm -rf "${BACKUP_FOLDER}"
}

export PROJECT_FOLDER
PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")/.." &>/dev/null && pwd)"
main $@