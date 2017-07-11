import datetime
import enum
import uuid

from ons_ras_common.ras_database.base import Base
from ons_ras_common.ras_database.guid import GUID
from ons_ras_common.ras_database.json_column import JsonColumn
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from swagger_server.controllers.util import filter_falsey_values, partition_dict
from swagger_server.controllers.validate import Validator, Exists, IsUuid


class Business(Base):
    __tablename__ = 'business'

    UNIT_TYPE = 'B'

    REQUIRED_ATTRIBUTES = [
        'contactName', 'employeeCount', 'enterpriseName', 'facsimile', 'fulltimeCount', 'legalStatus', 'name',
        'sic2003', 'sic2007', 'telephone', 'tradingName', 'turnover'
    ]

    # TODO: consider using postgres uuid for uuid pkey
    party_uuid = Column(GUID, unique=True, primary_key=True)
    business_ref = Column(Text, unique=True)
    respondents = relationship('BusinessRespondent', back_populates='business')
    attributes = Column(JsonColumn())
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def from_business_dict(d):
        v = Validator(Exists('businessRef',
                             'contactName',
                             'employeeCount',
                             'enterpriseName',
                             'enterpriseName',
                             'facsimile',
                             'fulltimeCount',
                             'legalStatus',
                             'name',
                             'sic2003',
                             'sic2007',
                             'telephone',
                             'tradingName',
                             'turnover'
                             ))
        if 'id' in d:
            v.add_rule(IsUuid('id'))

        if v.validate(d):
            b = Business(party_uuid=d.get('id', uuid.uuid4()), business_ref=d['businessRef'])
            _, attr = partition_dict(d, ['id', 'businessRef', 'sampleUnitType', 'attributes'])
            b.attributes = attr
            b.attributes.update(d.get('attributes', {}))
            b.valid = True
            return b

        return v

    @staticmethod
    def from_party_dict(d):
        b = Business(party_uuid=d.get('id', uuid.uuid4()), business_ref=d['sampleUnitRef'])
        b.attributes = d.get('attributes')
        return b

    def to_business_dict(self):
        d = {
            'id': self.party_uuid,
            'businessRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE
        }
        props, attrs = partition_dict(self.attributes, self.REQUIRED_ATTRIBUTES)
        d.update(props)
        d['attributes'] = filter_falsey_values(attrs)
        return d

    def to_party_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'attributes': self.attributes
        }
        return filter_falsey_values(d)


class BusinessRespondentStatus(enum.IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    SUSPENDED = 2
    ENDED = 3


class BusinessRespondent(Base):
    __tablename__ = 'business_respondent'

    business_id = Column(GUID, ForeignKey('business.party_uuid'), primary_key=True)
    respondent_id = Column(Integer, ForeignKey('respondent.id'), primary_key=True)
    status = Column('status', Enum(BusinessRespondentStatus))
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business = relationship('Business', back_populates='respondents')
    respondent = relationship('Respondent', back_populates='businesses')
    enrolment = relationship('Enrolment', back_populates='business_respondent')


class RespondentStatus(enum.IntEnum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2


class Respondent(Base):
    __tablename__ = 'respondent'

    UNIT_TYPE = 'BI'

    id = Column(Integer, primary_key=True)
    businesses = relationship('BusinessRespondent', back_populates='respondent')
    party_uuid = Column(GUID, unique=True)
    status = Column('status', Enum(RespondentStatus), default=RespondentStatus.CREATED)
    email_address = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    telephone = Column(Text)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def to_respondent_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'emailAddress': self.email_address,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'telephone': self.telephone
        }

        return filter_falsey_values(d)

    def to_party_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'attributes': filter_falsey_values({
                'emailAddress': self.email_address,
                'firstName': self.first_name,
                'lastName': self.last_name,
                'telephone': self.telephone})
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
    status = Column('status', Enum(EnrolmentStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business_respondent = relationship('BusinessRespondent', back_populates='enrolment')

    __table_args__ = (
        ForeignKeyConstraint(['business_id', 'respondent_id'],
                             ['business_respondent.business_id', 'business_respondent.respondent_id']),
    )


class EnrolmentCodeStatus(enum.IntEnum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentCode(Base):
    __tablename__ = 'enrolment_code'

    id = Column(Integer, primary_key=True)
    business_id = Column(GUID, ForeignKey('business.party_uuid'))
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    survey_id = Column(Text)
    iac = Column(Text)
    status = Column('status', Enum(EnrolmentCodeStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)


class EnrolmentInvitationStatus(enum.IntEnum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentInvitation(Base):
    __tablename__ = 'enrolment_invitation'

    id = Column(Integer, primary_key=True)
    business_id = Column(GUID, ForeignKey('business.party_uuid'))
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    survey_id = Column(Text)
    target_email = Column(Text)
    verification_token = Column(GUID)
    sms_verification_token = Column(Integer)
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime, default=datetime.datetime.utcnow() + datetime.timedelta(days=2))
    status = Column('status', Enum(EnrolmentInvitationStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
