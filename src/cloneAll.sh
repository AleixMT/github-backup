#!/usr/bin/env bash
# github-backup is a bash software to backup all the repos of a GitHub user.
#
# Copyright (C) 2024 Aleix Mariné-Tena
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# http://www.gnu.org/licenses/.

# Obtain the organizations (private or public) that this GitHub user is in. This function reads implicitly the
# GH_TOKEN variable to know from which user we are listing organizations. It also reads GH_TOKEN for
# authentication, since it lists both private and public organizations.
list_organizations()
{
  gh api -H "Accept: application/vnd.github+json" /user/orgs --jq ".[].login"
}

# Obtain the repositories of the GitHub user from $1. It reads GH_TOKEN for authentication, since it lists both
# private and public repositories.
list_user_repos()
{
  gh api "/users/$1/repos" | jq -r '.[].full_name'
}

# Obtain the GitHub repositories of the organization in $1. It reads GH_TOKEN for authentication, since it lists
# both private and public repositories.
list_org_repos()
{
  gh api "/orgs/$1/repos" | jq -r '.[].full_name'
}

# Clones the repo supplied in $1 in the path $2. It reads GH_TOKEN for authentication, since it clones both private
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
  # end, for example, if my name if JohnDoe, save it to a file called "JohnDoe_JohnDoe_repositories.txt". Also save it
  # to the global file of repositories of that user in "${BACKUP_FOLDER}/$1/all_repositories.txt"
  mkdir -p "${BACKUP_FOLDER}/$1/$1"
  echo "INFO: Listing \"/users/$1/repos\""
  local -r USER_REPOS="$(list_user_repos "$1")"
  echo "${USER_REPOS}" > "${BACKUP_FOLDER}/$1/$1/repositories.txt"
  echo "${USER_REPOS}" > "${BACKUP_FOLDER}/$1/all_repositories.txt"

  # Clone all the repos of the $1 user.
  while IFS= read -r repo; do
    clone_repo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
  done < "${BACKUP_FOLDER}/$1/$1/repositories.txt"

  # List repos of the organizations that this user is in and save them into a text file into
  # "${BACKUP_FOLDER}/$1/ORGANIZATION/repositories.txt". Then, clone each of the repositories in
  # "${BACKUP_FOLDER}/$1/ORGANIZATION/REPO". Also save the repository names to the global file of repositories in
  # "${BACKUP_FOLDER}/$1/all_repositories.txt"
  while IFS= read -r org; do
    mkdir -p "${BACKUP_FOLDER}/$1/${org}"
    local ORG_REPOS
    echo "INFO: Listing \"/orgs/$1/repos\""
    ORG_REPOS="$(list_org_repos "${org}")"
    echo "${ORG_REPOS}" > "${BACKUP_FOLDER}/$1/${org}/repositories.txt"
    echo "${ORG_REPOS}" >> "${BACKUP_FOLDER}/$1/all_repositories.txt"
    while IFS= read -r repo; do
      echo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
      clone_repo "${repo}" "${BACKUP_FOLDER}/$1/${repo}"
    done < "${BACKUP_FOLDER}/$1/${org}/repositories.txt"
  done < "${BACKUP_FOLDER}/$1/organizations.txt"
}


# Does not remove the backup folder afterwards. Useful if you want to update the same backup over
# Arguments:
#  - "-r|--no-remove|--no-remove-folder": Do not remove the backup folder after making the backup. Useful if you want to
#    use the same backup folder and update it over time.
#  - "-c|--no-compress|--no-compress-folder": Do not compress folder after making the backup. Useful in combination with
#    -r.
main()
{
  # Declare argument flags
  NO_COMPRESS="false"
  NO_REMOVE="false"
  USERS=()

  # Process arguments
  while [ $# -gt 0 ]; do
    case "$1" in
      -c|--no-compress|--no-compress-folder)
        NO_COMPRESS="true"
      ;;
      -r|--no-remove|--no-remove-folder)
        NO_REMOVE="true"
      ;;
      *)
        USERS+=("$1")
      ;;
    esac
  shift
  done

  # Check if $1 is present.
  if [ -z "${USERS[*]}" ]; then
    echo "Error: This program needs at least one argument telling from which github user we are going to do the backup.
Aborting."
    exit 1
  fi

  # Check the authentication status with GitHub
  authenticated="false"
  if ! gh auth status; then
    if [ -n "${GH_TOKEN_FILE}" ]; then
      gh auth login --with-token < "${GH_TOKEN_FILE}"
      authenticated="true"
    fi
    if [ "${authenticated}" = "false" ] && [ -n "${GH_TOKEN}" ]; then
      echo "${GH_TOKEN}" | gh auth login --with-token
      authenticated="true"
    fi
    if [ "${authenticated}" = "false" ]; then
      echo "ERROR: GitHub token not found and user is not authenticated in gh command.
If you are using this script in a workflow set the environment variable GH_TOKEN with your GitHub token for
the authentication. You can do so by declaring it in your environment variables, in your bashrc or by setting it
before calling the script:

GH_TOKEN=\"your_github_secret_token\" ./cloneAll.sh

If you are using this script in a user environment you can also issue the command \"gh auth login\" to provide the
authentication.

If you are running from Docker or from a workflow it is likely that you did not set the GH_TOKEN_FILE environment
variable, which is the standard way of passing the token to the workflow or container. You can do so by creating a
GitHub token and putting it into secrets/GH_TOKEN.txt"
      exit 1
    fi
  fi

  # Check if the user in $1 exists in github, if it does not exist exit program showing error message.
  for user in "${USERS[@]}"; do
    if ! gh api "/users/${user}" > /dev/null; then
      echo "ERROR: Could not use GitHub API due to missing or wrong authentication GitHub user '$1' not found. Aborting."
      exit 1
    fi
  done

  # Create and set mount point folder. The place where we are putting the final compressed file of the backup.
  MOUNT_POINT="${PROJECT_FOLDER}/backup"
  mkdir -p "${MOUNT_POINT}"

  # Create and set backup folder.
  BACKUP_FOLDER="${PROJECT_FOLDER}/backup/content"
  mkdir -p "${BACKUP_FOLDER}"

  # Do backup for all user and organizations supplied in the arguments
  for user in "${USERS[@]}"
  do
    do_backup "${user}"
  done

  # Compress the backup folder
  if [ "${NO_COMPRESS}" = "false" ]; then
    tar -czvf "${MOUNT_POINT}/backup_$(date +"%Y-%m-%d_%H:%M:%S").tar.gz" -C "$(dirname "${BACKUP_FOLDER}")" "$(basename "${BACKUP_FOLDER}")"
  fi

  # Remove content
  if [ "${NO_REMOVE}" = "false" ]; then
    rm -rf "${BACKUP_FOLDER}"
  fi
}

export PROJECT_FOLDER
PROJECT_FOLDER="$(cd "$(dirname "$(realpath "$0")")/.." &>/dev/null && pwd)"
main "$@"