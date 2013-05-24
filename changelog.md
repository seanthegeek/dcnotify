Change Log
==========

0.4.0 (2013-05-24)
-----------------

- Fixed incomplete refactoring that caused notifications to fail.
- Templates now pass HTML validation
- Added more code comments

0.3.4 (2013-02-15)
------------------

- Fixed typo in contact view that caused it to fail.
- Fixed bug that caused guest count to be the subscriber count


0.3.0 (2013-01-29)
------------------

- Cleaned up code to match standard mod_wsgi deployments after move from PythonAnywhere to Web Faction
- Modulerize code
- Improve PEP8 compliance
- Abstract subscriber and guest functions
- Remove new guest symbol (>>) from guest descriptions
- Upgrade to HTML5 boilerplate 4.1.0
- Use secure (HTTPS) app URLs
- Add sample http.cpnf and index.py


0.2.0 (2013-01-20)
------------------

- Updated scraper to work with D*C website redesign
- Removed guest count sanity check


0.1.3 (2012-12-22)
------------------

- Fixed a bug in scraper error handler that stopped it from working


0.1.2 (2012-12-22)
------------------

- Fixed regex bug in scraper.py sanity check
- Added email notification to admin in case of scraper failure
- Renamed some .txt files to .md files


0.1.1 (2012-12-01)
------------------

- Fixed formatting in templates/emails/guest.html


0.1.0 (2012-12-01)
------------------

- Initial release
