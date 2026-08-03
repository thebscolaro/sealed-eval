FROM python:3.12-slim
# Works with `podman build` / `podman compose` using the same Dockerfile name.
WORKDIR /app
COPY pyproject.toml README.md SPEC.md ./
COPY src ./src
COPY fixtures ./fixtures
COPY subject-demo ./subject-demo
COPY agents ./agents
RUN pip install --no-cache-dir .
EXPOSE 8787 8080
CMD ["sealed-eval", "serve", "--host", "0.0.0.0", "--port", "8787"]
