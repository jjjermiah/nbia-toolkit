from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from nbiatoolkit.models.base import AbstractListModel, AbstractModel


class Patient(AbstractModel):
	Collection: str
	PatientID: str = Field(..., alias="PatientId")
	PatientName: Optional[str] = None
	PatientSex: Optional[str] = None
	PatientBirthDate: Optional[datetime] = None
	EthnicGroup: Optional[str] = None
	Phantom: Optional[str] = None
	SpeciesCode: Optional[str] = None
	SpeciesDescription: Optional[str] = None

	@validator("PatientBirthDate", pre=True, always=True)
	def validate_birth_date(self, value):
		"""
		Custom validator to convert date strings to datetime using the convert_date method.
		"""
		if value is None:
			return value
		return AbstractModel.convert_date(value)


	def is_male(self) -> bool:
		return self.PatientSex == 'M'

	def is_female(self) -> bool:
		return self.PatientSex == 'F'


class PatientList(AbstractListModel[Patient]):
	__key__ = "PatientID"

class Study(AbstractModel):
	Collection: str
	StudyInstanceUID: str = Field(..., alias="StudyInstanceUID")
	StudyDate: Optional[datetime] = None
	StudyDescription: Optional[str] = None
	StudyID: Optional[str] = None
	PatientAge: Optional[str] = None
	PatientID: Optional[str] = None
	PatientName: Optional[str] = None
	PatientSex: Optional[str] = None
	PatientBirthDate: Optional[datetime] = None
	SeriesCount: Optional[int] = None
	AdmittingDiagnosesDescription: Optional[str] = None
	LongitudinalTemporalEventType: Optional[str] = None
	LongitudinalTemporalOffsetFromEvent: Optional[float] = None

	@validator("StudyDate", pre=True, always=True)
	def validate_study_date(self, value):
		"""
		Custom validator to convert date strings to datetime using the convert_date method.
		"""
		if value is None:
			return value
		return AbstractModel.convert_date(value)

	@validator("PatientBirthDate", pre=True, always=True)
	def validate_birth_date(self, value):
		"""
		Custom validator to convert date strings to datetime using the convert_date method.
		"""
		if value is None:
			return value
		return AbstractModel.convert_date(value)

class StudyList(AbstractListModel[Study]):
	__key__ = "StudyInstanceUID"

class Series(AbstractModel):
	Collection: str
	SeriesInstanceUID: str = Field(..., alias="SeriesInstanceUID")
	StudyInstanceUID: Optional[str] = None
	Modality: Optional[str] = None
	ProtocolName: Optional[str] = None
	SeriesDate: Optional[datetime] = None
	SeriesDescription: Optional[str] = None
	BodyPartExamined: Optional[str] = None
	SeriesNumber: Optional[int] = None
	AnnotationsFlag: Optional[bool] = None
	PatientID: Optional[str] = None
	Manufacturer: Optional[str] = None
	ManufacturerModelName: Optional[str] = None
	SoftwareVersions: Optional[str] = None
	ImageCount: Optional[int] = None
	TimeStamp: Optional[str] = None
	LicenseName: Optional[str] = None
	LicenseURI: Optional[str] = None
	CollectionURI: Optional[str] = None
	FileSize: Optional[int] = None
	DateReleased: Optional[datetime] = None
	StudyDescription: Optional[str] = None
	StudyDate: Optional[datetime] = None
	ThirdPartyAnalysis: Optional[str] = None

	@validator("SeriesDate", pre=True, always=True)
	def validate_series_date(self, value):
		"""
		Custom validator to convert date strings to datetime using the convert_date method.
		"""
		if value is None:
			return value
		return AbstractModel.convert_date(value)

	@validator("StudyDate", pre=True, always=True)
	def validate_study_date(self, value):
		"""
		Custom validator to convert date strings to datetime using the convert_date method.
		"""
		if value is None:
			return value
		return AbstractModel.convert_date(value)

class SeriesList(AbstractListModel[Series]):
	__key__ = "SeriesInstanceUID"

if __name__ == "__main__":
	import json
	from pathlib import Path

	from nbiatoolkit import NBIAClient

	client = NBIAClient(log_level="DEBUG")
	
	collections_list_file = Path("data/collections_list.json")
	patient_list_file = Path("data/patient_list.json")
	study_list_file = Path("data/study_list.json")
	series_list_file = Path("data/series_list.json")

	if collections_list_file.exists():
		collections = json.loads(collections_list_file.read_text())
	else:
		collections_list_file.parent.mkdir(parents=True, exist_ok=True)
		collections = client.getCollections() # type: ignore
		collections_list_file.write_text(json.dumps(collections))

	if patient_list_file.exists():
		patients = json.loads(patient_list_file.read_text())
	else:
		patient_list_file.parent.mkdir(parents=True, exist_ok=True)
		patients = client.getPatients() # type: ignore
		patient_list_file.write_text(json.dumps(patients))

	if study_list_file.exists():
		studies = json.loads(study_list_file.read_text())
	else:
		study_list_file.parent.mkdir(parents=True, exist_ok=True)
		studies = client.getStudies(Collection=collections[0]['Collection']) # type: ignore
		study_list_file.write_text(json.dumps(studies))

	if series_list_file.exists():
		series = json.loads(series_list_file.read_text())
	else:
		series_list_file.parent.mkdir(parents=True, exist_ok=True)
		series = client.getSeries() # type: ignore
		series_list_file.write_text(json.dumps(series))


	_pl = Patient.from_dicts(patients)
	patient_list = PatientList(items=_pl)

	_sl = Study.from_dicts(studies)
	study_list = StudyList(items=_sl)

	_sel = Series.from_dicts(series)
	series_list = SeriesList(items=_sel)


	print(patient_list.filter(lambda x: x.PatientID.startswith('LIDC')).df)
	print(patient_list.filter(lambda x: not x.PatientID.startswith('LIDC')).df)
	
	# two ways
	print(patient_list.filter(lambda x: x.PatientSex == 'F').df)
	print(patient_list.filter(lambda x: x.is_female()).df)