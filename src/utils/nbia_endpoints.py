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
    

    # Helper functions
    def __str__(self):
        return self.value
    
    def _format(self):
        return self.value.split("/")[-1]