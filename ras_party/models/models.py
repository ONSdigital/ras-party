import datetime
import enum
import uuid

from jsonschema import Draft4Validator

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base

from ras_party.models import GUID
from ras_party.support.util import filter_falsey_values, partition_dict


Base = declarative_base()


class Business(Base):
    __tablename__ = 'business'

    UNIT_TYPE = 'B'

    # TODO: consider using postgres uuid for uuid pkey
    party_uuid = Column(GUID, unique=True, primary_key=True)
    business_ref = Column(Text, unique=True)
    respondents = relationship('BusinessRespondent', back_populates='business')
    attributes = relationship('BusinessAttributes', backref='business',
                              order_by='BusinessAttributes.id', lazy='joined')
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def validate(json_packet, schema):
        """
        Validate the JSON packet against the supplied schema

        :param json_packet: The incoming JSON packet (typically via a POST)
        :param schema: the JSON schema to validate against
        :return: an error iterator if the packet is invalid, otherwise False
        """
        validator = Draft4Validator(schema)
        if not validator.is_valid(json_packet):
            return [str(e) for e in validator.iter_errors(json_packet)]

    @staticmethod
    def to_party(business_data):
        """
        The Business posting is now the same as the Party posting (FIXME: not exactly), except that the Business version
        has a flat structure and the party service has attributes in a dictionary item called 'attributes'.
        So for business postings, we just convert the incoming version into the Party version, then we can
        use the Party code to post the object.

        :param business_data: The raw data in dictionary form
        :return: The same data transformed to generic party format
        """

        party, attrs = partition_dict(business_data, ['sampleUnitRef', 'sampleUnitType', 'id', "sampleSummaryId"])
        party['attributes'] = attrs
        return party

    @staticmethod
    def from_party_dict(party):

        b = Business(party_uuid=party.get('id', uuid.uuid4()), business_ref=party['sampleUnitRef'])
        ba = BusinessAttributes(business_id=b.party_uuid, sample_summary_id=party['sampleSummaryId'])
        ba.attributes = party.get('attributes')
        name = '{runame1} {runame2} {runame3}'.format(**ba.attributes)
        ba.attributes['name'] = ' '.join(name.split())
        b.attributes.append(ba)
        b.valid = True
        return b

    @staticmethod
    def _get_respondents_associations(respondents):
        associations = []
        for business_respondent in respondents:
            respondent_dict = {
                "partyId": business_respondent.respondent.party_uuid,
                "businessRespondentStatus": business_respondent.respondent.status.name
            }
            enrolments = business_respondent.enrolment
            respondent_dict['enrolments'] = []
            for enrolment in enrolments:
                enrolments_dict = {
                    "name": enrolment.survey_name,
                    "surveyId": enrolment.survey_id,
                    "enrolmentStatus": EnrolmentStatus(enrolment.status).name
                }
                respondent_dict['enrolments'].append(enrolments_dict)
            associations.append(respondent_dict)
        return associations

    def add_versioned_attributes(self, party):
        ba = BusinessAttributes(business_id=self.party_uuid, sample_summary_id=party['sampleSummaryId'])
        ba.attributes = party.get('attributes')
        name = '{runame1} {runame2} {runame3}'.format(**ba.attributes)
        ba.attributes['name'] = ' '.join(name.split())
        self.attributes.append(ba)

    def to_business_dict(self):
        d = self.to_business_summary_dict()

        return dict(d, **self.attributes[-1].attributes)

    def to_business_summary_dict(self, collection_exercise_id=None):
        attributes = self._get_attributes_for_collection_exercise(collection_exercise_id)
        d = {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'sampleSummaryId': attributes.sample_summary_id,
            'name': attributes.attributes.get('name'),
            'associations': self._get_respondents_associations(self.respondents)
        }
        return d

    def to_party_dict(self):
        return {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'sampleSummaryId': self.attributes[-1].sample_summary_id,
            'attributes': self.attributes[-1].attributes,
            'name': self.attributes[-1].attributes.get('name'),
            'associations': self._get_respondents_associations(self.respondents)
        }

    def _get_attributes_for_collection_exercise(self, collection_exercise_id=None):
        if collection_exercise_id:
            for attributes in self.attributes:
                if attributes.collection_exercise == collection_exercise_id:
                    return attributes

        return self.attributes[-1]


class BusinessAttributes(Base):
    __tablename__ = 'business_attributes'

    id = Column("id", Integer(), primary_key=True)
    business_id = Column(GUID, ForeignKey('business.party_uuid'))
    sample_summary_id = Column(Text)
    collection_exercise = Column(Text)
    attributes = Column(JSONB)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)


class BusinessRespondentStatus(enum.IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    SUSPENDED = 2
    ENDED = 3


class BusinessRespondent(Base):
    __tablename__ = 'business_respondent'

    business_id = Column(GUID, ForeignKey('business.party_uuid'), primary_key=True)
    respondent_id = Column(Integer, ForeignKey('respondent.id'), primary_key=True)
    status = Column('status', Enum(BusinessRespondentStatus), default=BusinessRespondentStatus.ACTIVE)
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business = relationship('Business', back_populates='respondents', lazy='joined')
    respondent = relationship('Respondent', back_populates='businesses', lazy='joined')
    enrolment = relationship('Enrolment', back_populates='business_respondent')


class RespondentStatus(enum.IntEnum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2


class PendingEnrolment(Base):
    __tablename__ = 'pending_enrolment'

    id = Column(Integer, primary_key=True)
    case_id = Column(GUID)
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    business_id = Column(GUID)
    survey_id = Column(GUID)

    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    respondent = relationship('Respondent')

    __table_args__ = (
        ForeignKeyConstraint(['respondent_id'],
                             ['respondent.id']),
    )


class Respondent(Base):
    __tablename__ = 'respondent'

    UNIT_TYPE = 'BI'

    id = Column(Integer, primary_key=True)
    businesses = relationship('BusinessRespondent', back_populates='respondent')
    party_uuid = Column(GUID, unique=True)
    status = Column('status', Enum(RespondentStatus), default=RespondentStatus.CREATED)
    email_address = Column(Text, unique=True)
    first_name = Column(Text)
    last_name = Column(Text)
    telephone = Column(Text)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    pending_enrolment = relationship('PendingEnrolment', back_populates='respondent')

    @staticmethod
    def _get_business_associations(businesses):
        associations = []
        for business_respondent in businesses:
            business_dict = {
                "partyId": business_respondent.business.party_uuid,
                "sampleUnitRef": business_respondent.business.business_ref,
                "businessRespondentStatus": business_respondent.respondent.status.name
            }
            enrolments = business_respondent.enrolment
            business_dict['enrolments'] = []
            for enrolment in enrolments:
                enrolments_dict = {
                    "name": enrolment.survey_name,
                    "surveyId": enrolment.survey_id,
                    "enrolmentStatus": EnrolmentStatus(enrolment.status).name
                }
                business_dict['enrolments'].append(enrolments_dict)
            associations.append(business_dict)
        return associations

    def to_respondent_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'emailAddress': self.email_address,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'telephone': self.telephone,
            'status': RespondentStatus(self.status).name,
            'associations': self._get_business_associations(self.businesses)
        }

        return filter_falsey_values(d)

    def to_party_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'status': RespondentStatus(self.status).name,
            'attributes': filter_falsey_values({
                'emailAddress': self.email_address,
                'firstName': self.first_name,
                'lastName': self.last_name,
                'telephone': self.telephone}),
            'associations': self._get_business_associations(self.businesses)
        }

        return d


class EnrolmentStatus(enum.IntEnum):
    PENDING = 0
    ENABLED = 1
    DISABLED = 2
    SUSPENDED = 3


class Enrolment(Base):
    __tablename__ = 'enrolment'

    business_id = Column(GUID, primary_key=True)
    respondent_id = Column(Integer, primary_key=True)
    survey_id = Column(Text, primary_key=True)
    survey_name = Column(Text)
    status = Column('status', Enum(EnrolmentStatus), default=EnrolmentStatus.PENDING)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business_respondent = relationship('BusinessRespondent', back_populates='enrolment', lazy='joined')

    __table_args__ = (
        ForeignKeyConstraint(['business_id', 'respondent_id'],
                             ['business_respondent.business_id', 'business_respondent.respondent_id']),
    )
