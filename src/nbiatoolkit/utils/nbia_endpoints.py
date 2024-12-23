from enum import StrEnum


class NBIA_BASE_URLS(StrEnum):  # noqa: N801
	"""
	This enum class defines the NBIA base URLs used in the NBIA toolkit.
	"""

	NBIA: str = 'https://services.cancerimagingarchive.net/nbia-api/services/'
	NLST: str = 'https://nlst.cancerimagingarchive.net/nbia-api/services/'
	LOGOUT_URL: str = 'https://services.cancerimagingarchive.net/nbia-api/logout'


class NBIA_ENDPOINTS(StrEnum):  # noqa: N801
	"""
	This enum class defines the NBIA endpoints used in the NBIA toolkit.
	"""

	GET_COLLECTIONS: str = 'v2/getCollectionValues'
	GET_COLLECTION_PATIENT_COUNT: str = 'getCollectionValuesAndCounts'
	GET_COLLECTION_DESCRIPTIONS: str = 'getCollectionDescriptions'

	GET_MODALITY_VALUES: str = 'v2/getModalityValues'
	GET_MODALITY_PATIENT_COUNT: str = 'getModalityValuesAndCounts'

	GET_PATIENTS: str = 'v2/getPatient'
	GET_NEW_PATIENTS_IN_COLLECTION: str = 'v2/NewPatientsInCollection'
	GET_PATIENT_BY_COLLECTION_AND_MODALITY: str = 'v2/getPatientByCollectionAndModality'
	GET_BODY_PART_PATIENT_COUNT: str = 'getBodyPartValuesAndCounts'

	GET_STUDIES: str = 'v2/getPatientStudy'

	GET_SERIES: str = 'v2/getSeries'
	GET_UPDATED_SERIES: str = 'v2/getUpdatedSeries'  # ?fromDate=01/01/2024
	GET_SERIES_METADATA: str = 'v1/getSeriesMetaData'
	DOWNLOAD_SERIES_MD5: str = 'v2/getImageWithMD5Hash'
	DOWNLOAD_SERIES: str = 'v2/getImage'
	
	# Needs SeriesInstanceUID and SOPInstanceUID
	DOWNLOAD_IMAGE:str = 'v1/getSingleImage'

	GET_DICOM_TAGS: str = 'getDicomTags'

	GET_SOP_INSTANCE_UIDS: str = 'v1/getSOPInstanceUIDs'