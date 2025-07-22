# R dependencies installation script for the MTG Analytics pipeline

# List of required packages
packages <- c(
  "tidyverse",
  "ggplot2",
  "reshape2",
  "gridExtra",
  "scales",
  "RColorBrewer",
  "viridis"
)

# Function to install missing packages
install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

# Install missing packages
sapply(packages, install_if_missing)

# Check that all packages are installed
missing_packages <- packages[!sapply(packages, requireNamespace, quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop("The following packages could not be installed: ", paste(missing_packages, collapse = ", "))
} else {
  cat("All required packages are installed.\n")
}