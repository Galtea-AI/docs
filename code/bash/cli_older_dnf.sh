dnf list --showduplicates galtea   # list the versions

sudo dnf install galtea-5.4.0      # also downgrades a newer installed CLI
# Keep 5.4.0 on `dnf upgrade`. On dnf 4 (RHEL 8 and 9), first run:
#   sudo dnf install python3-dnf-plugin-versionlock
sudo dnf versionlock add galtea
