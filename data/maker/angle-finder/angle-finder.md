---
title: angle finder
summary: need a tool, make a tool
created-on: 22/09/2024 05:04PM CDT
last-modified: 25/09/2024 01:59PM CDT
author: Andrew Phifer
link: NA
folder: maker
---

----

As it turns out, I enjoy *making* stationary (as opposed to the more typical hobbies of using and collecting pieces of it).  This is one of the pieces that I've ended up designing after discovering that like!  Currently, it needs a bit more polish.  Here are the things i'd like to change and do before i call this one done.

1. design and print a sticker to go in the middle of the dial to indicate the actual measured angle.
2. add a few more emblishments to the visual design
3. modify the slice of the stl to prevent the pin holes from getting filled with supports.
4. modify surface geometry to make the coefficient of kinetic and static friction more consistent across a whole spin of the dial


The construction of the product is fairly simple.  It prints in three pieces;

1. lower arm
2. upper arm 
3. upper arm backing

The upper arm comes in two pieces, held together by 2 18mm m3 steel dowls that are super glued in place.  The supports required while printing are actually minimal, as this design has helped me think about how to effectively orient a print to reduce the number of required supports.  The key is to orient all faces of the model with respect to the build plate at an angle higher than the minimal print angle for slopes.  In my case, thats about 30 degrees from horizontal.  I've been applying this method for a while, but it was really this print that made me figure out exactly why it worked in a formal way due to all the slopes and angled faces in this model.  

![prototype](/data/maker/angle-finder/angle-finder-prototype.jpg)