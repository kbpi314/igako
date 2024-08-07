
### Load libraries ###

library(ggplot2)
library(ggpubr)
library(tidyverse)
library(rstatix)
library(tidyr)
library(RColorBrewer)

### Beta diversity pcoa ###

# background theme
bkg <- theme_bw() +
  theme(axis.text = element_text(size = 18, color = "black")) +
  theme(axis.title = element_text(size = 24, color = "black", face = "bold")) +
  theme(axis.title.x = element_text(margin = unit(c(8, 0, 0, 0), "mm"))) +
  theme(axis.title.y = element_text(margin = unit(c(0, 8, 0, 0), "mm"))) +
  theme(legend.text = element_text(size = 18, color = "black"))+ #, face = "bold")) +
  # theme(legend.title = element_blank()) +
  theme(legend.title = element_text(size = 24, face = "bold", color = "black"))
theme(legend.justification = "right")# +
#theme(panel.border = element_rect(color = "black", fill = NA, size = 1.5))

# function to specify that axis labels have 2 decimal places
f.dec <- function(x){
  format(round(x, 2), nsmall = 2)
}

# directory for storing files
dir = "/Users/KevinBu/Desktop/clemente_lab/Projects/igako/outputs/"

# list of distance methods
dists <- c('unifrac')

# load data
df <- read.delim(file="/Users/KevinBu/Desktop/clemente_lab/Projects/igako/outputs/unweighted_pcoa.tsv",
                 row.names=1)

# choose colors
# col1 <- colorRampPalette(brewer.pal(9, "Set2"))(length(unique(df$Strain)))
col1 <- c('White','Black')

# order factors for legend
dx.order = c("IgAKO","WT")
df$Strain <- factor(df$Strain, levels=dx.order)

for (j in seq_along(dists)) {
  # create filenames
  filename_plot = paste("bdivplot.pdf", sep = "_")
  
  # plot beta diversity
  p <- ggplot() +
    geom_point(data = df, aes(x = PC1, y = PC2, fill = Strain),size=4,shape=21) +
    scale_fill_manual(values = c("IgAKO" = "White", "WT" = "Black")) +
    bkg + 
    scale_x_continuous(labels = f.dec) + # 2 decimal places on x-axis
    scale_y_continuous(labels = f.dec)   # 2 decimal places on y-axis
  
  # save plot
  fp = paste(dir, filename_plot, sep = "")
  pdf(file = fp, height = 6, width = 8)
  plot(p)
  dev.off()
}
