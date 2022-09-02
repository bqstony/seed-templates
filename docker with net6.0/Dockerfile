# See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.
# Build Context is ./
#
# Stage for deploymend image
########################
FROM mcr.microsoft.com/dotnet/aspnet:6.0-bullseye-slim AS base
ARG BUILD_VERSION
ARG BUILD_DATE
ARG MAINTAINER
ARG PRODUCT
ARG SOURCEURL
ARG SOURCECOMMITID
WORKDIR /app
EXPOSE 80

# The OCI Spec Labels https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.version=$BUILD_VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.title=$PRODUCT
LABEL org.opencontainers.image.authors=$MAINTAINER
LABEL org.opencontainers.image.source=$SOURCEURL
LABEL org.opencontainers.image.revision=$SOURCECOMMITID
LABEL org.opencontainers.image.base.name=mcr.microsoft.com/dotnet/aspnet:6.0-bullseye-slim
LABEL org.opencontainers.image.vendor="customer"

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:80/health || exit 1

# Install prerequisites for healthcheck
RUN apt-get update && apt-get install -y \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Stage for building and test the app
########################
FROM mcr.microsoft.com/dotnet/sdk:6.0-bullseye-slim AS build-stage
# copy the project data files and build app by ignoring stuff in .dockerignore
WORKDIR /src
COPY . .
RUN dotnet restore
# Build & Test all Testprojects in the sln
# Test only .net6
RUN dotnet test -c Release --framework net6.0 --logger "console;verbosity=detailed" --logger "trx" --results-directory /src/testresults

FROM build-stage AS publish-stage
# Create publish build of the Service Project
WORKDIR /src/myproject
RUN dotnet publish -c Release --framework net6.0 -o /app/publish

# Stage for pack the binary to deploymnd container
########################
FROM base AS final
WORKDIR /app
COPY --from=build-stage /src/testresults ./testresults
COPY --from=publish-stage /app/publish .
ENTRYPOINT ["dotnet", "myproject.dll"]

# Alternative store the testresult in a empty container
# It possible to export the files to dockerhost with: DOCKER_BUILDKIT=1 docker build --target export-test-results --output type=local,dest=testresults --progress=plain .
########################
# FROM scratch as export-test-results
# COPY --from=test-stage /src/testresults/*.trx ./