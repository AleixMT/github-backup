FROM ubuntu:latest

# Set the working directory
WORKDIR /

# Install gh
RUN apt update && apt install -y \
  curl \
  gpg
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg;
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null;
RUN apt update && apt install -y gh;

# Copy the source code to the container
COPY ./src src

# Make the entrypoint script executable
RUN chmod +x /src/cloneAll.sh

# Create mount point for the backup
RUN mkdir backup

ENTRYPOINT ["bash", "src/cloneAll.sh"]
