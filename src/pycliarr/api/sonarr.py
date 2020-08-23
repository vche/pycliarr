from pycliarr.api.base_media import BaseCliMediaApi


class SonarrCli(BaseCliMediaApi):
    pass


#     def getRoot(self):
#         """Returns the Root Folder"""
#         path = "/api/rootfolder"
#         res = self.request_get(path)
#         return res.json()
#
#     def getQualityProfiles(self):
#         """Gets all quality profiles"""
#         path = "/api/profile"
#         res = self.request_get(path)
#         return res.json()
#
#
# get_history
# episodeId (int) - Filters to a specific episode ID
