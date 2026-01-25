FROM ghcr.io/charmbracelet/vhs:latest

# Install Python
RUN apt-get --allow-releaseinfo-change update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-pip \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# App location
WORKDIR /app

# Copy packaging metadata first (better caching)
COPY pyproject.toml README.md LICENSE /app/
COPY src/ /app/src/

# Create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"
RUN pip install --upgrade pip

# Install project
RUN pip install .

# Hard fail if install was unsuccesful
RUN robotunused --help >/dev/null

# Let builder script run on container run
ENTRYPOINT ["/bin/bash"]
