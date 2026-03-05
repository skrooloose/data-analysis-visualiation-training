# Save list of currently installed packages
old_packages <- installed.packages()[, "Package"]
save(old_packages, file = "~/old_packages.RData")

# Load old package list
load("~/old_packages.RData")

# Reinstall packages that are missing in new R
new_packages <- old_packages[!(old_packages %in% installed.packages()[, "Package"])]

if(length(new_packages) > 0){
  install.packages(new_packages, dependencies = TRUE)
}

# Optional: force rebuild all packages to match new R version
update.packages(ask = FALSE, checkBuilt = TRUE)