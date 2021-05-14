*********
Changelog
*********

master
======

v1.0.10
=======

:Date: May 14, 2021

Fix
---
- Remove debug log

v1.0.9
======

:Date: May 13, 2021

Fix
---
- Add missing files to radarr item
- Fix issue when a single item is returned as lookup results

v1.0.8
======

:Date: May 9, 2021

New
---
- Issue with delete requests parameters sent as data instead of url parameters

New
---
- Add season folder creation option to sonarr

v1.0.7
======

:Date: May 3, 2021

New
---
-  Added optional selection of seaons to monitor in sonarr.add_serie(), (use case from https://github.com/marc0janssen/pixlovarr)

v1.0.6
======

:Date: Jan 19, 2021

Fix
---
-  Fix bug when servers return an array of 1 element

v1.0.5
======

:Date: Dec 18, 2020

New
---
- Add raw server response in server exception
- Add classes imports to api module

Fix
---
- Radarr quality profile parsing issue in CLI aith api v3
- Cleanup debug logs

v1.0.4
======

:Date: Dec 17, 2020

New
---
- Added cli status command
- Use radarr api v3

v1.0.3
======

:Date: Aug 30, 2020

Fix
---
- Re release of 1.0.2 with updated doc

v1.0.2
======

:Date: Aug 28, 2020

Fix
---
- Fix issue when adding using tmdb/imdb/tvdb id

v1.0.1
======

:Date: Aug 26, 2020

New
---

* Full unit tests coverage
* Available in pip
* Full command set

v0.0.1
======

:Date: Aug 23, 2020

New
---

* Initial version with sonarr and radarr clients
