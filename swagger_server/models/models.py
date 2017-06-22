import datetime
import enum
import uuid

from ons_ras_common import ons_env
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from swagger_server.controllers_local.util import filter_falsey_values, partition_dict
from swagger_server.controllers_local.validate import Validator, Exists, IsUuid
from swagger_server.models.guid import GUID
from swagger_server.models.json_column import JsonColumn


class Business(ons_env.db.base):
    __tablename__ = 'business'

    UNIT_TYPE = 'B'

    REQUIRED_ATTRIBUTES = [
        'contactName', 'employeeCount', 'enterpriseName', 'facsimile', 'fulltimeCount', 'legalStatus', 'name',
        'sic2003', 'sic2007', 'telephone', 'tradingName', 'turnover'
    ]

    business_ref = Column(Text, primary_key=True)
    party_uuid = Column(GUID, unique=True)
    respondents = relationship('BusinessRespondent', back_populates='business')
    attributes = Column(JsonColumn())
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_ref, party_uuid=None):
        self.business_ref = business_ref
        self.party_uuid = party_uuid or uuid.uuid4()

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
            b = Business(d['businessRef'], d.get('id'))
            _, attr = partition_dict(d, ['id', 'businessRef', 'sampleUnitType', 'attributes'])
            b.attributes = attr
            b.attributes.update(d.get('attributes', {}))
            b.valid = True
            return b

        return v

    @staticmethod
    def from_party_dict(d):
        b = Business(d['sampleUnitRef'], d.get('id'))
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


class BusinessRespondent(ons_env.db.base):
    __tablename__ = 'business_respondent'

    business_id = Column(Integer, ForeignKey('business.business_ref'), primary_key=True)
    respondent_id = Column(Integer, ForeignKey('respondent.id'), primary_key=True)
    status = Column('status', Enum(BusinessRespondentStatus))
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business = relationship('Business', back_populates='respondents')
    respondent = relationship('Respondent', back_populates='businesses')

    def __init__(self):
        # TODO: what to use for effective_to?
        self.effective_to = datetime.datetime.now() + datetime.timedelta(days=7)


class RespondentStatus(enum.IntEnum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2


class Respondent(ons_env.db.base):
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

    def __init__(self, party_uuid=None):
        self.party_uuid = party_uuid or uuid.uuid4()

    @staticmethod
    def from_respondent_dict(d):
        expected = ('emailAddress', 'firstName', 'lastName', 'telephone')

        v = Validator(Exists(*expected))
        if 'id' in d:
            v.add_rule(IsUuid('id'))

        if v.validate(d):
            r = Respondent(d.get('id'))
            r.email_address = d['emailAddress']
            r.first_name = d['firstName']
            r.last_name = d['lastName']
            r.telephone = d['telephone']
            r.valid = True
            return r

        return v

    @staticmethod
    def from_party_dict(d):
        r = Respondent(d.get('id'))
        attrs = d.get('attributes', {})
        r.email_address = attrs.get('emailAddress')
        r.first_name = attrs.get('firstName')
        r.last_name = attrs.get('lastName')
        r.telephone = attrs.get('telephone')
        return r

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


class Enrolment(ons_env.db.base):
    __tablename__ = 'enrolment'

    id = Column(Integer, primary_key=True)
    business_association_id = Column(Integer)
    survey_id = Column(Text)
    status = Column('status', Enum(EnrolmentStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_association_id, survey_id, status):
        self.business_association_id = business_association_id
        self.survey_id = survey_id
        self.status = status


class EnrolmentCodeStatus(enum.IntEnum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentCode(ons_env.db.base):
    __tablename__ = 'enrolment_code'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('business.business_ref'))
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    survey_id = Column(Text)
    iac = Column(Text)
    status = Column('status', Enum(EnrolmentCodeStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, respondent_id, business_id, survey_id, iac, status):
        self.respondent_id = respondent_id
        self.business_id = business_id
        self.survey_id = survey_id
        self.status = status
        self.iac = iac


class EnrolmentInvitationStatus(enum.IntEnum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentInvitation(ons_env.db.base):
    __tablename__ = 'enrolment_invitation'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('business.business_ref'))
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    survey_id = Column(Text)
    target_email = Column(Text)
    verification_token = Column(GUID)
    sms_verification_token = Column(Integer)
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime, default=datetime.datetime.utcnow() + datetime.timedelta(days=2))
    status = Column('status', Enum(EnrolmentInvitationStatus))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, respondent_id, business_id, survey_id, target_email,
                 verification_token, sms_verification_token, status):
        self.respondent_id = respondent_id
        self.business_id = business_id
        self.survey_id = survey_id
        self.target_email = target_email
        self.verification_token = verification_token
        self.sms_verification_token = sms_verification_token
        self.status = status
