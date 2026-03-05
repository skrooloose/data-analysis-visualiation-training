# Save list of installed packages
old_packages <- installed.packages()[, "Package"]
save(old_packages, file = "C:/Users/YourUser/Documents/old_packages.RData")
# Load saved package list
load("C:/Users/YourUser/Documents/old_packages.RData")

# Install missing packages in new R
new_packages <- old_packages[!(old_packages %in% installed.packages()[, "Package"])]
if(length(new_packages) > 0){
  install.packages(new_packages, dependencies = TRUE)
}

# Rebuild all old packages for the new R version
update.packages(ask = FALSE, checkBuilt = TRUE)