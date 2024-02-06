

import pydicom
from dataclasses import dataclass
from typing import Optional

@dataclass
class DicomData:
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    sop_instance_uid: Optional[str] = None
    image_type: Optional[str] = None
    study_id: Optional[str] = None
    series_number: Optional[int] = None
    acquisition_number: Optional[int] = None
    instance_number: Optional[int] = None
    image_position_patient: Optional[str] = None
    image_orientation_patient: Optional[str] = None
    frame_of_reference_uid: Optional[str] = None
    position_reference_indicator: Optional[str] = None
    slice_location: Optional[str] = None
    samples_per_pixel: Optional[int] = None
    rows: Optional[int] = None
    columns: Optional[int] = None
    pixel_spacing: Optional[str] = None
    study_date: Optional[str] = None
    series_date: Optional[str] = None
    modality: Optional[str] = None
    study_description: Optional[str] = None
    series_description: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    patient_birth_date: Optional[str] = None
    patient_sex: Optional[str] = None
    patient_age: Optional[str] = None
    instance_creation_date: Optional[str] = None
    instance_creation_time: Optional[str] = None

    def to_dataset(self):
        ds = pydicom.Dataset()
        ds.StudyInstanceUID = self.study_instance_uid
        ds.SeriesInstanceUID = self.series_instance_uid
        ds.SOPInstanceUID = self.sop_instance_uid
        ds.ImageType = self.image_type
        ds.StudyID = self.study_id
        ds.SeriesNumber = self.series_number
        ds.AcquisitionNumber = self.acquisition_number
        ds.InstanceNumber = self.instance_number
        ds.ImagePositionPatient = self.image_position_patient
        ds.ImageOrientationPatient = self.image_orientation_patient
        ds.FrameOfReferenceUID = self.frame_of_reference_uid
        ds.PositionReferenceIndicator = self.position_reference_indicator
        ds.SliceLocation = self.slice_location
        ds.SamplesPerPixel = self.samples_per_pixel
        ds.Rows = self.rows
        ds.Columns = self.columns
        ds.PixelSpacing = self.pixel_spacing
        ds.StudyDate = self.study_date
        ds.SeriesDate = self.series_date
        ds.Modality = self.modality
        ds.StudyDescription = self.study_description
        ds.SeriesDescription = self.series_description
        ds.PatientName = self.patient_name
        ds.PatientID = self.patient_id
        ds.PatientBirthDate = self.patient_birth_date
        ds.PatientSex = self.patient_sex
        ds.PatientAge = self.patient_age
        ds.InstanceCreationDate = self.instance_creation_date
        ds.InstanceCreationTime = self.instance_creation_time

        return ds

def read_subset_dicom(file_path):
    ds = pydicom.dcmread(file_path)
    dicom_data = DicomData(
        study_instance_uid=ds.get("StudyInstanceUID"),
        series_instance_uid=ds.get("SeriesInstanceUID"),
        sop_instance_uid=ds.get("SOPInstanceUID"),
        image_type=ds.get("ImageType"),
        study_id=ds.get("StudyID"),
        series_number=ds.get("SeriesNumber"),
        acquisition_number=ds.get("AcquisitionNumber"),
        instance_number=ds.get("InstanceNumber"),
        image_position_patient=ds.get("ImagePositionPatient"),
        image_orientation_patient=ds.get("ImageOrientationPatient"),
        frame_of_reference_uid=ds.get("FrameOfReferenceUID"),
        position_reference_indicator=ds.get("PositionReferenceIndicator"),
        slice_location=ds.get("SliceLocation"),
        samples_per_pixel=ds.get("SamplesPerPixel"),
        rows=ds.get("Rows"),
        columns=ds.get("Columns"),
        pixel_spacing=ds.get("PixelSpacing"),
        study_date=ds.get("StudyDate"),
        series_date=ds.get("SeriesDate"),
        modality=ds.get("Modality"),
        study_description=ds.get("StudyDescription"),
        series_description=ds.get("SeriesDescription"),
        patient_name=ds.get("PatientName"),
        patient_id=ds.get("PatientID"),
        patient_birth_date=ds.get("PatientBirthDate"),
        patient_sex=ds.get("PatientSex"),
        patient_age=ds.get("PatientAge"),
        instance_creation_date=ds.get("InstanceCreationDate"),
        instance_creation_time=ds.get("InstanceCreationTime")
    )
    return dicom_data


def create_DicomData_from_DICT(data_list):
    dicom_data = DicomData(
        study_instance_uid=data_list.get("StudyInstanceUID"),
        series_instance_uid=data_list.get("SeriesInstanceUID"),
        sop_instance_uid=data_list.get("SOPInstance"),
        image_type=data_list.get("ImageType"),
        study_id=data_list.get("StudyID"),
        series_number=data_list.get("SeriesNumber"),
        acquisition_number=data_list.get("AcquisitionNumber"),
        instance_number=data_list.get("InstanceNumber"),
        image_position_patient=data_list.get("ImagePositionPatient"),
        image_orientation_patient=data_list.get("ImageOrientationPatient"),
        frame_of_reference_uid=data_list.get("FrameOfReferenceUID"),
        position_reference_indicator=data_list.get("PositionReferenceIndicator"),
        slice_location=data_list.get("SliceLocation"),
        samples_per_pixel=data_list.get("SamplesPerPixel"),
        rows=data_list.get("Rows"),
        columns=data_list.get("Columns"),
        pixel_spacing=data_list.get("PixelSpacing"),
        study_date=data_list.get("StudyDate"),
        series_date=data_list.get("SeriesDate"),
        modality=data_list.get("Modality"),
        study_description=data_list.get("StudyDescription"),
        series_description=data_list.get("SeriesDescription"),
        patient_name=data_list.get("PatientName"),
        patient_id=data_list.get("PatientID"),
        patient_birth_date=data_list.get("PatientBirthDate"),
        patient_age=data_list.get("PatientAge"),
        instance_creation_date=data_list.get("InstanceCreationDate"),
        instance_creation_time=data_list.get("InstanceCreationTime")
    )