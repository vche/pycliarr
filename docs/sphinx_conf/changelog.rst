*********
Changelog
*********

master
======

v1.0.20
=======

:Date: Sept 23, 2022

New
---
* `Issue #30 <https://github.com/vche/pycliarr/issues/30>`_:
   * Add command line option so list root folders.
   * Add command line option to specify or select a root folder to use when adding movie/show.
   * Update add methods to allow specifying root id.
   * Allow specifying default root folder when creating client

v1.0.19
=======

:Date: Jan 22, 2022

New
---
- Add commands to search missing movies and episodes
- Add movie/serie edit commands

Fix
---
- Missing qet queue parameters
- Missing int cast in build root path
- Missing root folder argument in build path

v1.0.18
=======

:Date: Nov 29, 2021

Fix
---
- fix issue with root paths in radnarr with api v3

v1.0.17
=======

:Date: Nov 26, 2021

Fix
---
- fix radarr lookup url
- fix sonarr add serie new api with language id

New
---
- add import list inclusion api

v1.0.16
=======

:Date: Nov 25, 2021

Fix
---
- delete serie with exclusion list

New
---
- Fully moved to api v3 on both sonarr and radarr
- Added blocklist commands
- Added notification commands
- Added tag commands

v1.0.15
=======

:Date: Nov 23, 2021

Fix
---
- Fix delete movie exclusion option for api v3

v1.0.14
=======

:Date: June 15, 2021

Fix
---
- Remove unsupported chars from movie/serie paths depending on the platform

v1.0.13
=======

:Date: May 23, 2021

New
---
- Add option to specify folder path in add_movie and add_serie
- Default folder path builders
- Update default movie folder with release year to match radarr gui default

Fix
---
- Support for several root folders in get_root_folder()

v1.0.12
=======

:Date: May 16, 2021

Fix
---
- Fix issue with default values for dates

v1.0.11
=======

:Date: May 16, 2021

Fix
---
- Fix wrong url format with delete queue commands

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
