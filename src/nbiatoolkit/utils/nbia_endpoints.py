from enum import Enum


class NBIA_BASE_URLS(Enum):
    """
    This enum class defines the NBIA base URLs used in the NBIA toolkit.
    """

    NBIA = "https://services.cancerimagingarchive.net/nbia-api/services/"
    NLST = "https://nlst.cancerimagingarchive.net/nbia-api/services/"
    LOGOUT_URL = "https://services.cancerimagingarchive.net/nbia-api/logout"

    # Helper functions
    def __str__(self):
        return self.value

    def _format(self):
        return self.value.split("/")[-1]


class NBIA_ENDPOINTS(Enum):
    """
    This enum class defines the NBIA endpoints used in the NBIA toolkit.
    """

    GET_COLLECTIONS = "v2/getCollectionValues"
    GET_COLLECTION_PATIENT_COUNT = "getCollectionValuesAndCounts"
    GET_COLLECTION_DESCRIPTIONS = "getCollectionDescriptions"

    GET_MODALITY_VALUES = "v2/getModalityValues"

    GET_PATIENTS = "v2/getPatient"
    GET_NEW_PATIENTS_IN_COLLECTION = "v2/NewPatientsInCollection"
    GET_PATIENT_BY_COLLECTION_AND_MODALITY = "v2/getPatientByCollectionAndModality"
    GET_BODY_PART_PATIENT_COUNT = "getBodyPartValuesAndCounts"

    GET_STUDIES = "v2/getPatientStudy"

    GET_SERIES = "v2/getSeries"
    GET_UPDATED_SERIES = "v2/getUpdatedSeries"  # ?fromDate=01/01/2024
    GET_SERIES_METADATA = "v1/getSeriesMetaData"
    DOWNLOAD_SERIES = "v2/getImageWithMD5Hash"
    GET_DICOM_TAGS = "getDicomTags"

    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesMetaData"
    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getSeriesSize"

    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/v2/getUpdatedSeries"

    # curl -H "Authorization:Bearer YOUR_ACCESS_TOKEN" -k "https://services.cancerimagingarchive.net/nbia-api/services/getSeriesMetadata2" -d "list=1.3.6.1.4.1.14519.5.2.1.6834.5010.322628904903035357840500590726"
    # Helper functions
    def __str__(self):
        return self.value

    def _format(self):
        return self.value.split("/")[-1]
