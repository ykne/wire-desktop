#!/bin/sh
# Prints the next Release counter for $1 (the upstream_version being built),
# querying Copr's own published package info as the source of truth for "what
# release came last" -- there's no official baseline wire-desktop package to
# stay ahead of, so a plain incrementing counter (reset to 1 on a version bump)
# is enough; no epoch/timestamp trick needed. Prints 1 for a brand-new
# package/project, a version bump, or any query failure -- never aborts the build.
set -u

owner="ykner"
project="wire-desktop"
pkg="wire-desktop"
upstream_version="$1"

last_json=$(curl -sf "https://copr.fedorainfracloud.org/api_3/package?ownername=${owner}&projectname=${project}&packagename=${pkg}&with_latest_build=true" 2>/dev/null)
last_version_release=$(printf '%s' "$last_json" | grep -oE '"version": *"[^"]*"' | head -1 | sed -E 's/.*"([^"]*)"$/\1/')

if [ -z "$last_version_release" ]; then
  echo 1
  exit 0
fi

# Strip an epoch prefix if present (e.g. "1:3.44.0-2" -> "3.44.0-2"), then split
# version/release on the LAST "-".
no_epoch=${last_version_release#*:}
last_version=${no_epoch%-*}
last_release_full=${no_epoch##*-}
counter=$(printf '%s' "$last_release_full" | grep -oE '^[0-9]+')

if [ "$last_version" = "$upstream_version" ] && [ -n "$counter" ]; then
  echo $((counter + 1))
else
  echo 1
fi
