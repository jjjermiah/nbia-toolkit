from enum import Enum, auto

from enum import Enum

class NBIA_ENDPOINTS(Enum):
    """
    This enum class defines the NBIA endpoints used in the NBIA toolkit.
    """
    GET_COLLECTION_PATIENT_COUNT = 'getCollectionValuesAndCounts'
    GET_COLLECTIONS = 'v2/getCollectionValues'
    GET_BODY_PART_PATIENT_COUNT = 'getBodyPartValuesAndCounts'
    GET_PATIENT_BY_COLLECTION_AND_MODALITY = 'v2/getPatientByCollectionAndModality'    
    GET_SERIES = 'v2/getSeries'
    
    DOWNLOAD_SERIES = 'v2/getImageWithMD5Hash'
    
    # TIMES OUT???
    GET_SERIES_SIZE = 'v2/getSeriesSize'
    GET_UPDATED_SERIES = 'v2/getUpdatedSeries'
    
    # curl -H 'Authorization:Bearer eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkZGFhMGY3YS1kZTBmLTRkYWQtYjM1ZS05MjljYjBiMTY3YjgifQ.eyJleHAiOjE3MDA1MDI1MzksImlhdCI6MTcwMDQ5NTMzOSwianRpIjoiYmY0NjgyNDktYjU4ZS00MTM2LTllYTQtOWE2NjkzOTVhZjQxIiwiaXNzIjoiaHR0cHM6Ly9rZXljbG9hay5kYm1pLmNsb3VkL2F1dGgvcmVhbG1zL1RDSUEiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiZjowMTliNTYzNC1kYWJkLTQyMTEtYTQxZC03MjNjNDRhZmNmZmQ6bmJpYV9ndWVzdCIsInR5cCI6IkJlYXJlciIsImF6cCI6Im5iaWEiLCJzZXNzaW9uX3N0YXRlIjoiMjgzZDc0MjYtZGE1Yi00NTExLWI2MzEtN2YyMzY5YjA2MmU0IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3NlcnZpY2VzLmNhbmNlcmltYWdpbmdlYXJjaGl2ZS5uZXQiLCJodHRwczovL25iaWEuY2FuY2VyaW1hZ2luZ2VhcmNoaXZlLm5ldCIsImh0dHBzOi8vd3d3LmNhbmNlcmltYWdpbmdlYXJjaGl2ZS5uZXQiLCIqIiwiaHR0cDovL3RjaWEtbmJpYS0yLmFkLnVhbXMuZWR1OjQ1MjEwIiwiaHR0cHM6Ly9jYW5jZXJpbWFnaW5nZWFyY2hpdmUubmV0IiwiaHR0cDovL3RjaWEtbmJpYS0xLmFkLnVhbXMuZWR1OjQ1MjEwIiwiaHR0cHM6Ly9wdWJsaWMuY2FuY2VyaW1hZ2luZ2VhcmNoaXZlLm5ldCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJkZWZhdWx0LXJvbGVzLXRjaWEiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJzaWQiOiIyODNkNzQyNi1kYTViLTQ1MTEtYjYzMS03ZjIzNjliMDYyZTQiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6Ik5CSUEgR3Vlc3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJuYmlhX2d1ZXN0IiwiZ2l2ZW5fbmFtZSI6Ik5CSUEiLCJmYW1pbHlfbmFtZSI6Ikd1ZXN0IiwiZW1haWwiOiJuYmlhX2d1ZXN0QGNhbmNlcmltYWdpbmdhcmNoaXZlLm5ldCJ9.YIrmcZcDT9w22diON2bFxDVcY1-BU59FwcklsnYHBT0' -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesMetaData?SeriesInstanceUID=1.3.6.1.4.1.9590.100.1.2.374115997511889073021386151921807063992"
    
    # https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesMetaData?SeriesInstanceUID=1.3.6.1.4.1.9590.100.1.2.374115997511889073021386151921807063992
    
    # https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesSize?SeriesInstanceUID=1.3.6.1.4.1.9590.100.1.2.374115997511889073021386151921807063992
    
    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeries"
    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesMetaData"
    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesSize"
    
    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getUpdatedSeries"
    
    # Helper functions
    def __str__(self):
        return self.value
    
    def _format(self):
        return self.value.split("/")[-1]