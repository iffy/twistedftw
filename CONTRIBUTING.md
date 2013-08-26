<!--
Copyright (c) The TwistedFTW Team
See LICENSE for details.
-->


Thank you for wanting to contribute!


Goal of TwistedFTW
==================

The goal of TwistedFTW is to get people excited about using Twisted.  There are
many ways to excite people, including: showcasing lesser-known features,
providing easy-to-understand tutorials, showing working code, answering
common questions, correcting misinformation, sharing success stories, etc.  If
what you want to contribute could make people excited about using Twisted it's
probably welcome here.

It is *not* a goal of TwistedFTW to replace the official docs nor to replace
other excellent tutorials or guides.  As much as possible, link to official
docs or other relevant sources rather than duplicating work.


How to contribute
=================

1.  All contributions must be licensed in a manner compatible with the Apache 2.0
    license (See the LICENSE file in this directory).  Include a comment such
    as the following in all source files:

        Copyright (c) The TwistedFTW Team
        See LICENSE for details.


2.  Branch off of the `gh-pages` branch.

3.  Add your name to `AUTHORS` if you want (this is optional).

4.  Submit a pull request through Github to merge into the `gh-pages` branch.


Adding an article
=================

This may change, but for now, to add an article:

1.  Add an html file to the relevant subdirectory, e.g.
    
        touch articles/web/mynewarticle.html

2.  If you want the article to be visible on the front page and article
    navigation menus, include the filename in the `contents` file:

        echo "mynewarticle.html" >> articles/web/contents

3.  Regenerate the JSON article index

        make article_index.json

    or, if you don't mind running the tests too:

        make


Serving the site locally (on your machine)
==========================================

Start the webserver on port 8900

    twistd -n web --port tcp:8900 --path .

Then go to http://127.0.0.1:8900/ to see it.

If you don't see the article you just added, maybe you need to add it to the
`contents` file or remake the `article_index.json` (see
[Adding an article](#adding-an-article) above).
