# load libraries
library(devtools)
library('ComplexHeatmap')
library(grid)
library(caret)
library(circlize)
library(MASS)

# first time install:
# install_github("jokergoo/ComplexHeatmap")

setwd('~/Desktop/clemente_lab/Projects/igako/')

# load df of features w/metadata
df = read.table(file=paste('inputs/reproduce_analysis/heatmap-10-asvs.txt',sep=''),sep='\t',header=T)#,row.names = 1)

# drop strain row and rownames 
df_feat = df[-1,-1]

# convert all col to numeric
df_feat[] <- lapply(df_feat, as.numeric)

# convert to matrix
mat_feat <- data.matrix(df_feat)

# grab feature annotations  
cols_anno = df[1,2:ncol(df)]

#Create a custom color scale
# https://stackoverflow.com/questions/6919025/how-to-assign-colors-to-categorical-variables-in-ggplot2-that-have-stable-mappin
library(RColorBrewer)
myColors <- brewer.pal(8,"Set1")
myColors <- brewer.pal(8,"Purples")

# names(myColors) <- levels(df_anno$var_type)
colScale <- scale_colour_manual(name = "Strain",values = myColors)

# set color annotation
# https://www.biostars.org/p/317349/
# ann <- df[1,]
# colnames(ann) <- c('Strain')
colours <- list('Strain' = c('IgAKO' = myColors[1], 
                           'WT' = myColors[2]))

column_ha <- HeatmapAnnotation(df = df[1, ],
                               which = 'col',
                               col = colours,
                               annotation_width = unit(c(1, 4), 'cm'),
                               gap = unit(1, 'mm'))
rows_ha <- HeatmapAnnotation(df = df[,1],
                                     which = 'row')


file_path <- paste('/Users/KevinBu/Desktop/clemente_lab/Projects/igako/outputs/heatmap_10asvs.pdf',sep='')

pdf(GetoptLong::qq(file_path), width = 14, height=5)  # Image size

hm <- Heatmap(mat_feat, use_raster = FALSE,
              col = colorRamp2(c(-1, 0, 8), c("#4C0099", "white", "#CCCC00")), 
              column_split = unlist(cols_anno[1,], use.names = FALSE),
              row_names_side = 'left',
              row_names_max_width = unit(12, "in"),
              row_labels = df[2:nrow(df),1],
              na_col = 'black',
              name = 'Z-Score', 
              show_column_names = FALSE, 
              show_row_names = TRUE,
              row_names_gp = gpar(fontsize = 12),
              column_names_gp = gpar(fontsize = 6),
              # row_title = "ASVs",
              # column_title = "ANCOM Z-Score",# (|X| = 9717)",#9717 from 9727 after near zero var) 17 for sig, 9436 for df_final, 760 for asv, 8676 for quant
              cluster_rows = FALSE,
              cluster_columns = FALSE)#,

hm = draw(
  hm, background = "transparent"
  #heatmap_legend_side="bottom", 
  #annotation_legend_side="bottom"
)  
dev.off()

