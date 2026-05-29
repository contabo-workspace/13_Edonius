from .school_year import SchoolYear
from .school_class import SchoolClass
from .study_field import StudyField, StudyFieldInSchoolYear
from .subject import Subject, SubjectClassInSchoolYear, SubjectInSchoolYear
from .teaching_assignment import TeacherAssignment, TeachingGroupInSchoolYear
from .teacher import Teacher
from .user_profile import UserProfile
from .global_settings import GlobalSettings

__all__ = [
	"SchoolYear",
	"SchoolClass",
	"StudyField",
	"StudyFieldInSchoolYear",
	"Subject",
	"SubjectInSchoolYear",
	"SubjectClassInSchoolYear",
	"Teacher",
	"TeachingGroupInSchoolYear",
	"TeacherAssignment",
	"UserProfile",
	"GlobalSettings",
]
