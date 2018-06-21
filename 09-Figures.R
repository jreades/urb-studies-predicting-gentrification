#####################
# This is simply used to output a few of the
# results from the Python work because I happen
# to prefer the 'look' of ggplot2 to Seaborn for
# scientific visualisation.
#####################
devtools::install_github("tidyverse/ggplot2", ref = "sf")
devtools::install_github("r-spatial/sfr")
library(sf)
library(ggplot2)
library(data.table, warn.conflicts = FALSE)
library(dtplyr)
library(scales)
library(grid)
library(gridExtra)

target.crs = 27700

setwd(file.path(path.expand('~'),'Documents','github','ml-gent'))
base.path  = file.path('.','data','analytical')
model.name = 'Untransformed' # One of: Untransformed, Box-Cox or Log

#######################
# First, let's output the 
# results from exploring the
# hyperparameters
#######################

# n_estimators
n.estimators <- fread( file.path(base.path,paste(model.name,'Scores','n_estimators.csv',sep="-")), stringsAsFactors=FALSE )

# max_depth
max.depth <- fread( file.path(base.path,paste(model.name,'Scores','max_depth.csv',sep="-")) )

# max_features
max.features <- fread( file.path(base.path,paste(model.name,'Scores','max_features_and_bootstrap.csv',sep="-")) )
max.features$max_features <- unlist(lapply(as.numeric(max.features$max_features), round, 2))
max.features <- max.features[ bootstrap != TRUE ] # Drop where bootstrap is true
max.features <- max.features[ max_features != is.na(max_features) ] # Drop where 'auto' or 'sqrt'

# min_samples_leaf
min.leaf <- fread( file.path(base.path,paste(model.name,'Scores','min_samples_leaf.csv',sep="-")) )

# Assemble into a single data table
n.estimators$label = 'n Estimators'
max.depth$label = 'Maximum Depth'
max.features$label = 'Maximum Features'
min.leaf$label = 'Minimum Leaf Size'

# Set up ribbons for training
n.estimators$uctr = n.estimators$`Training Score` + n.estimators$`Std. of Training Scores`
n.estimators$lctr = n.estimators$`Training Score` - n.estimators$`Std. of Training Scores`

max.depth$uctr = max.depth$`Training Score`+ max.depth$`Std. of Training Scores` 
max.depth$lctr = max.depth$`Training Score`- max.depth$`Std. of Training Scores`

max.features$uctr = max.features$`Training Score`+ max.features$`Std. of Training Scores` 
max.features$lctr = max.features$`Training Score`- max.features$`Std. of Training Scores`

min.leaf$uctr = min.leaf$`Training Score`+ min.leaf$`Std. of Training Scores` 
min.leaf$lctr = min.leaf$`Training Score`- min.leaf$`Std. of Training Scores`

# Set up ribbons for testing
n.estimators$uctst = n.estimators$`Test Score` + n.estimators$`Std. of Test Scores`
n.estimators$lctst = n.estimators$`Test Score` - n.estimators$`Std. of Test Scores`

max.depth$uctst = max.depth$`Test Score`+ max.depth$`Std. of Test Scores` 
max.depth$lctst = max.depth$`Test Score`- max.depth$`Std. of Test Scores`

max.features$uctst = max.features$`Test Score`+ max.features$`Std. of Test Scores` 
max.features$lctst = max.features$`Test Score`- max.features$`Std. of Test Scores`

min.leaf$uctst = min.leaf$`Test Score`+ min.leaf$`Std. of Test Scores` 
min.leaf$lctst = min.leaf$`Test Score`- min.leaf$`Std. of Test Scores`

# Training Results -- ylim probably needs to be about 0 -0.3 (but possibly -0.1 and even then that might flatline the results for some params)
p1 <- ggplot(n.estimators) + 
  geom_line( aes(x=n_estimators, y=`Training Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctr, ymax=uctr, x=n_estimators, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) +
  xlab('Number of Trees') + 
  theme_bw() + 
  theme(legend.position="none")
p2 <- ggplot(max.depth) + 
  geom_line( aes(x=max_depth, y=`Training Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctr, ymax=uctr, x=max_depth, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Maximum Tree Depth') +  
  theme_bw() + 
  theme(legend.position="none")
p3 <- ggplot(max.features) + 
  geom_line( aes(x=max_features, y=`Training Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctr, ymax=uctr, x=max_features, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) +
  xlab('Maximum Features Considered') +  
  theme_bw() + 
  theme(legend.position="none")
p4 <- ggplot(min.leaf) + 
  geom_line( aes(x=min_samples_leaf, y=`Training Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctr, ymax=uctr, x=min_samples_leaf, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Minimum Samples per Leaf') +  
  theme_bw() + 
  theme(legend.position="none")

m1 <- grid.arrange(p1,p3,p2,p4, ncol=2, nrow=2, top=textGrob("Hyperparameter Training", gp=gpar(fontsize=15,font=8)))
ggsave(plot=m1, filename="Hyperparameters - Training.pdf", path=file.path(base.path), device='pdf', width=8, height=8, units='in')

# Testing Results -- ylim probably needs to be about 0 (or -0.25) to -0.325
p5 <- ggplot(n.estimators) + 
  geom_line( aes(x=n_estimators, y=`Test Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctst, ymax=uctst, x=n_estimators, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Number of Trees') + 
  theme_bw() + 
  theme(legend.position="none")
p6 <- ggplot(max.depth) + 
  geom_line( aes(x=max_depth, y=`Test Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctst, ymax=uctst, x=max_depth, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Maximum Tree Depth') +  
  theme_bw() + 
  theme(legend.position="none")
p7 <- ggplot(max.features) + 
  geom_line( aes(x=max_features, y=`Test Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctst, ymax=uctst, x=max_features, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Maximum Features Considered') +  
  theme_bw() + 
  theme(legend.position="none")
p8 <- ggplot(min.leaf) + 
  geom_line( aes(x=min_samples_leaf, y=`Test Score`, colour='red') ) + 
  geom_ribbon(aes(ymin=lctst, ymax=uctst, x=min_samples_leaf, fill="band"), alpha = 0.3) +
  scale_y_continuous(labels=comma) + 
  xlab('Minimum Samples per Leaf') +  
  theme_bw() + 
  theme(legend.position="none")

m2 <- grid.arrange(p5,p6,p7,p8, ncol=2, nrow=2, top=textGrob("Hyperparameter Testing", gp=gpar(fontsize=15,font=8)))
ggsave(plot=m2, filename="Hyperparameters - Testing.pdf", path=file.path(base.path), device='pdf', width=8, height=8, units='in')

#### Performance of Predictions

lsoas <- st_read(file.path('.','data','shp','LSOAs 2011.shp'), quiet=TRUE)
lsoas <- lsoas %>% st_set_crs(NA) %>% st_set_crs(target.crs)
cat("Loaded LSOAs file containing",nrow(lsoas),"zones","\n")

dt = fread( paste("gunzip","-c",file.path(base.path,paste(model.name,'Predictions.csv.gz',sep='-'))) )
setkey(dt,'lsoacd')
cat("Loaded predictions file containing",nrow(dt),"rows","\n")

print( cor(x=dt$`SES 2011`, y=dt$`SES 2011 (Predicted)`, use="complete.obs") )

# Work out SD of percentile change
dt$`Z-Score of Percentile Change 2001-2011` = (dt$`SES Percentile Ascent 2001-2011` - mean(dt$`SES Percentile Ascent 2001-2011`))/sd(dt$`SES Percentile Ascent 2001-2011`)
dt$`Z-Score of Percentile Change 2011-2021` = (dt$`SES Percentile Change 2011-2021` - mean(dt$`SES Percentile Change 2011-2021`))/sd(dt$`SES Percentile Change 2011-2021`)

dt[dt$lsoacd=='E01001335',]

dt$z0111 = cut(dt$`Z-Score of Percentile Change 2001-2011`, breaks = c(floor(min(dt$`Z-Score of Percentile Change 2001-2011`)), -4, -2, -1, 0, 1, 2, 4, ceiling(max(dt$`Z-Score of Percentile Change 2001-2011`))), labels=FALSE)
dt$z1121 = cut(dt$`Z-Score of Percentile Change 2011-2021`, breaks = c(floor(min(dt$`Z-Score of Percentile Change 2011-2021`)), -4, -2, -1, 0, 1, 2, 4, ceiling(max(dt$`Z-Score of Percentile Change 2011-2021`))), labels=FALSE)

dt$z0111 = dt$z0111-4.5
dt$z1121 = dt$z1121-4.5

dt[dt$lsoacd=='E01001335',]

write.csv(dt, file=file.path(base.path,paste(model.name,'Predictions-Standardised.csv',sep="-")))

dt.s <- merge(dt, lsoas, left_on='lsoacd', right_on='lsoacd')

ggplot(dt.s) +
  geom_histogram(aes(z0111), stat="count", na.rm=TRUE)

ggplot(dt.s) +
  #geom_sf(data=dt.s, aes(fill=z0111), lwd = 0)
  geom_sf(data=dt.s, color="white", size=0.125, aes(fill=z1121))

ses.min = floor(min(dt.s[, c('SES 2001', 'SES 2011','SES 2021 (Predicted)'), with=FALSE]))
ses.max = ceiling(max(dt.s[, c('SES 2001', 'SES 2011','SES 2021 (Predicted)'), with=FALSE]))

p <- ggplot(data=dt.s) + 
  geom_density( aes(x=`SES 2021 (Predicted)`, fill=NULL), color='green' ) + 
  geom_density( aes(x=`SES 2011`, fill=NULL), color='red' ) + 
  geom_density( aes(x=`SES 2001`, fill=NULL), color='blue' ) + 
  xlab("Neighbourhood Score") + 
  ylab("Density") + 
  ggtitle("Evolution of Neighbourhood Scores Over Time") + 
  scale_color_hue(labels = c("2001", "2011", "2021")) + 
  theme_bw()
#  guide_legend(title=NULL, title.position='top')
ggsave(plot=p, filename="Scores - Distributions.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

p <- ggplot(data=dt.s, aes(x=`SES 2011`, y=`SES 2011 (Predicted)`)) + 
  geom_smooth(method=lm, size=0.5, alpha=0.4, color='red') + 
  geom_point(size=0.5, alpha=0.25) + # aes(color=dt.s$LAD11CD), 
  theme(legend.position="none") + 
  ggtitle("2011 Neighbourhood Scores: Predicted Against Actual") + 
  theme_bw()
ggsave(plot=p, filename="Predictions - 2011 Predicted Against Actual.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

p <- ggplot(data=dt.s, aes(x=`SES 2001`, y=`SES 2011`)) + 
  geom_smooth(method=loess, size=0.5, alpha=1/2) + 
  geom_point(size=0.5, alpha=1/2) + # aes(color=dt.s$LAD11CD), 
  theme(legend.position="none") + 
  ggtitle("Neighbourhood Scores: 2001 against 2011") + 
  xlim( c(ses.min, ses.max) ) + 
  ylim( c(ses.min, ses.max) ) + 
  theme_bw()
ggsave(plot=p, filename="Predictions - 2001 to 2011.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

p <- ggplot(data=dt.s, aes(x=`SES 2011`, y=`SES 2021 (Predicted)`)) + 
  geom_smooth(method=loess, size=0.5, alpha=1/2) + 
  geom_point(size=0.5, alpha=1/2) + # aes(color=dt.s$LAD11CD), 
  theme(legend.position="none") + 
  ggtitle("Neighbourhood Scores: 2011 against 2021") + 
  xlim( c(ses.min, ses.max) ) + 
  ylim( c(ses.min, ses.max) ) + 
  theme_bw()
ggsave(plot=p, filename="Predictions - 2011 to 2021.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

asc.min = floor(min(dt.s[, c('SES Ascent 2001-2011','SES Ascent 2011-2021 (Predicted)'), with=FALSE]))
asc.max = ceiling(max(dt.s[, c('SES Ascent 2001-2011','SES Ascent 2011-2021 (Predicted)'), with=FALSE]))

p <- ggplot(data=dt.s, aes(x=`SES Ascent 2001-2011`, y=`SES Ascent 2011-2021 (Predicted)`)) + 
  geom_smooth(method=loess, size=0.5, alpha=1/2) + 
  geom_point(size=0.5, alpha=1/2) + # aes(color=dt.s$LAD11CD), 
  theme(legend.position="none") + 
  ggtitle("Neighbourhood Score Changes: 2001-2011 against 2011-2021") + 
  xlim( c(asc.min, asc.max) ) + 
  ylim( c(asc.min, asc.max) ) + 
  theme_bw()
ggsave(plot=p, filename="Predictions - Ascent Change.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

#######################
# Variable Importance
fi <- fread( paste("gunzip","-c",file.path(base.path,"Untransformed-Feature_Importance.csv.gz")) )
p <- ggplot(fi, aes(y=importance, x=Category, group=Category)) + geom_point() +
  ylab('Variable Importance') + xlab('Variable Group') + 
  ggtitle('Importance of Variable to Model') + 
  theme_bw() + 
  theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.4))
ggsave(plot=p, filename="Predictions - Variable Importance.pdf", path=file.path(base.path), device='pdf', width=5, height=5, units='in')
rm(p)

# Maps
ggplot(data=dt.s) +
  geom_sf()
