---
title: This Website!
summary: an ~~excuse~~ excercise to learn web development
created-on: 29/07/2024 01:00PM CDT
last-modified: 14/08/2024 01:34PM CDT
author: Andrew Phifer
link: https://github.com/TechyTrickster/personal_page
folder: software
---


# This Website! {#Title}
##### [github](https://github.com/TechyTrickster/personal_page) {#Link}

---

###### Introduction
I began creating this website during my time on the bench at TCS in order to keep my development skills sharp and to re-learn the skills of a full stack web developer.  When i originally joined TCS in early 2021, I received training as one.  It was essentially a 2 year associates degree compressed into 4 or 5 months.  I learned at lot doing that, and I seem to have retained much of the fundamentals, as I've been able to pick up most of basics fairly quickly over theses past few weeks!


[TOC]


###### design goals
originally, I just wanted to create a website to showcase all the different project's that I've worked on over the years, both at TCS, and on my own.  I still do.  However, feature creep being what it is, I've also ended up creating a well featured portfolio templating system.  As a result, my goals are thus:

1. re-learn full stack web development 
2. create a visually pleasing Portfolio template site
3. showcase all my different projects


I'm doing fairly well for myself for items 1 and 3, but what about item 2?


###### The Portfolio Templating System
The idea was to create a site that would be easy enough for anyone to pull down as source code, run with a python command, and all they would have to do would be to write up project pages.  In its currently implementation, all the user has to do is write up markdown formatted documents (with a wide array of supported extensions) about their project and dump them into the data folder.  The site then, on boot up, loads all those documents, converts them to html, writes the html to an sqlite3, in-memory database, and servers the relevant article when requested by a web browser.  The system automatically populates a side bar with links to all of the different project articles.

Currently, you have to manually modifiy the home page and seperately update a resume as an HTML document.  However, I have plans to generate those standard pages from markdown documents as well!

The markdown documents for projects require you to include some standardized meta-data at the top of the page.  this info is stripped out and written to the database to be used to load fields in the project page template.  Here is an example

![project template](/data/software/this_web_site/project-page-meta-data.png)

You'll need to add those tags.  The system will, for example, use the data in the title tag to generate the text in the page header, like this

![project-in-action](/data/software/this_web_site/how-meta-data-is-used.png)


###### Header Features
The header for each project page is of course populated with data taken from the .md files you provide.  However, the header itself provides a handful of nice features.

1. a nice background image
2. localization of the timestamp for creation and updates
3. a link to the coresponding github page for that project
4. neat visual effect of flipping a flash card between the timestamp and the human readable localization


###### Images
in order to keep page load times manageable, i've been using ffmpeg[^1], a popular and industry standard media manipulation tool to create high quality scaled down versions of all the images included on the site.  This frequently results in a 99% file size reduction.  As a result, project hosting costs are also reduced while image quality is maintained at a more than acceptable level for illustrative purposes.  As an example, the original image[^2] of the Miyoo Mini Plus was about 4.2MB, the version delivered by the site is about 42KB, nearly 100 times smaller.



[^1]: [https://www.ffmpeg.org/about.html](https://www.ffmpeg.org/about.html) - ffmpeg about page
[^2]: [link](/maker/miyoo-mini-plus-case) - Miyoo Mini Shell Project





