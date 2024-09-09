---
title: markdown and up
summary: sidestepping the one more standard problem for markdown
created-on: 27/08/2024 01:01PM CDT
last-modified: 09/09/2024 11:38PM CDT
author: Andrew Phifer
link: NA
folder: software
---

# Markdown and Up

I started this project for two reasons.  
1. to unify all the different markdown standards
2. to learn how to make a desktop GUI

The approach I've been taking has been tailored to avoid the whole "one standard to rule them all" problem.  

![one more standard](/data/software/mark-up-and-down/xkcd-standards.png)[^1]


Instead of making a new standard, what i've instead done is create an application to simply support all of them, all in a single application.  This eliminates the common problem with authoring markdown documents and not knowing for *sure* what they're going to look like on someone else's system.  

The application is built around a two column system.  One column is there for you to enter your plain text, and the other column is to preview what your article will look like on various platforms.  Selecting which platform to preview is done by editing the configuration of the options menu.  

The application allows the user to easily export the preview as an html formatted text file, making authoring new page content for manually maintained websites (or books if you're going the epub route) fairly straightforward.  

New systems and markdown features can be easily added with additional class files, using the same extension format as the python-markdown package[^2]





[^1]: [https://xkcd.com/927/](https://xkcd.com/927/) - xkcd comics
[^2]: [https://python-markdown.github.io/](https://python-markdown.github.io/) - python markdown package