from enum import Enum

class NBIA_ENDPOINTS(Enum):
    """
    This enum class defines the NBIA endpoints used in the NBIA toolkit.
    """
    BASE_URL = 'https://services.cancerimagingarchive.net/nbia-api/services/'
    
    GET_COLLECTION_PATIENT_COUNT = 'getCollectionValuesAndCounts'
    GET_COLLECTIONS = 'v2/getCollectionValues'
    GET_BODY_PART_PATIENT_COUNT = 'getBodyPartValuesAndCounts'
    GET_PATIENT_BY_COLLECTION_AND_MODALITY = 'v2/getPatientByCollectionAndModality'    
    GET_SERIES = 'v2/getSeries'
    
    DOWNLOAD_SERIES = 'v2/getImageWithMD5Hash'
    
    
    GET_SERIES_SIZE = 'v2/getSeriesSize'        # TIMES OUT???
    GET_UPDATED_SERIES = 'v2/getUpdatedSeries'
        
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