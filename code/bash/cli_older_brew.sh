# List the versions: one formula per minor version
brew search galtea-ai/tap/galtea@

# The formulas install the same `galtea` command, so remove the current one first
brew uninstall galtea
brew install galtea-ai/tap/galtea@5.4
