import datetime
import enum

from ons_ras_common import ons_env
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from swagger_server.controllers_local.util import filter_falsey_values, partition_dict
from swagger_server.models.guid import GUID
from swagger_server.models.json_column import JsonColumn


class Party(ons_env.db.base):
    __tablename__ = 'party'

    id = Column(Integer, primary_key=True)
    party_uuid = Column(GUID, unique=True)
    respondent = relationship('Respondent', uselist=False, back_populates='party')
    business = relationship('Business', uselist=False, back_populates='party')

    def __init__(self, party_uuid):
        self.party_uuid = party_uuid


class Business(ons_env.db.base):
    __tablename__ = 'business'

    UNIT_TYPE = 'B'

    REQUIRED_ATTRIBUTES = [
        'contactName', 'employeeCount', 'enterpriseName', 'facsimile', 'fulltimeCount', 'legalStatus', 'name',
        'sic2003', 'sic2007', 'telephone', 'tradingName', 'turnover'
    ]

    id = Column(Integer, primary_key=True)
    business_ref = Column(Text, unique=True)
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship('Party', back_populates='business')
    respondents = relationship('BusinessRespondent', back_populates='business')
    contact_name = Column(Text)
    employee_count = Column(Integer)
    enterprise_name = Column(Text)
    facsimile = Column(Text)
    fulltime_count = Column(Integer)
    legal_status = Column(Text)
    name = Column(Text)
    sic_2003 = Column(Text)
    sic_2007 = Column(Text)
    telephone = Column(Text)
    trading_name = Column(Text)
    turnover = Column(Integer)
    attributes = Column(JsonColumn())
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_ref, party):
        self.business_ref = business_ref
        self.party = party

    def from_dict(self, d):
        items, attrs = partition_dict(d, self.REQUIRED_ATTRIBUTES)
        self.contact_name = items['contactName']
        self.employee_count = int(items['employeeCount'])
        self.enterprise_name = items['enterpriseName']
        self.facsimile = items['facsimile']
        self.fulltime_count = items['fulltimeCount']
        self.legal_status = items['legalStatus']
        self.name = items['name']
        self.sic_2003 = items['sic2003']
        self.sic_2007 = items['sic2007']
        self.telephone = items['telephone']
        self.trading_name = items['tradingName']
        self.turnover = int(items['turnover'])
        self.attributes = attrs
        return self

    def to_dict(self):
        associations = self.respondents
        d = {
            'id': self.party.party_uuid,
            'businessRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'contactName': self.contact_name,
            'employeeCount': self.employee_count,
            'enterpriseName': self.enterprise_name,
            'facsimile': self.facsimile,
            'fulltimeCount': self.fulltime_count,
            'legalStatus': self.legal_status,
            'name': self.name,
            'sic2003': self.sic_2003,
            'sic2007': self.sic_2007,
            'telephone': self.telephone,
            'tradingName': self.trading_name,
            'turnover': self.turnover,
            'attributes': self.attributes,
            'associations': [{'id': a.respondent.party.party_uuid} for a in associations]
        }
        return filter_falsey_values(d)


class BusinessRespondentStatus(enum.IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    SUSPENDED = 2
    ENDED = 3


class BusinessRespondent(ons_env.db.base):
    __tablename__ = 'business_respondent'

    business_id = Column(Integer, ForeignKey('business.id'), primary_key=True)
    respondent_id = Column(Integer, ForeignKey('respondent.id'), primary_key=True)
    status = Column('status', Enum(BusinessRespondentStatus))
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business = relationship('Business', back_populates='respondents')
    respondent = relationship('Respondent', back_populates='businesses')

    # __table_args__ = (UniqueConstraint('business_id', 'respondent_id', name='_business_respondent_uc'),)

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
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship('Party', back_populates='respondent')
    status = Column('status', Enum(RespondentStatus), default=RespondentStatus.CREATED)
    email_address = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    telephone = Column(Text)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, party):
        self.party = party

    def to_dict(self):
        d = {
            'id': self.party.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'status': self.status,
            'emailAddress': self.email_address,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'telephone': self.telephone
        }

        return filter_falsey_values(d)


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
    business_id = Column(Integer, ForeignKey('business.id'))
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
    business_id = Column(Integer, ForeignKey('business.id'))
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



