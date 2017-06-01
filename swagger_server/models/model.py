import datetime
import enum

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from swagger_server.models.base import Base
from swagger_server.models.guid import GUID
from swagger_server.models.json_column import JsonColumn


class Party(Base):
    __tablename__ = 'party'

    id = Column(Integer, primary_key=True)
    party_id = Column(GUID)
    respondent = relationship('Respondent', uselist=False, back_populates='party')
    business = relationship('Business', uselist=False, back_populates='party')

    def __init__(self, party_id):
        self.party_id = party_id


class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer, primary_key=True)
    attributes = Column(JsonColumn())
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship('Party', back_populates='business')
    respondents = relationship('Respondent', secondary='business_respondent', back_populates='businesses')
    # business_ref = Column(Text)
    # name = Column(Text)
    # trading_name = Column(Text)
    # enterprise_name = Column(Text)
    # contact_name = Column(Text)
    # address_line_1 = Column(Text)
    # address_line_2 = Column(Text)
    # address_line_3 = Column(Text)
    # city = Column(Text)
    # postcode = Column(Text)
    # telephone = Column(Text)
    # employee_count = Column(Integer)
    # facsimile = Column(Text)
    # fulltime_count = Column(Integer)
    # legal_status = Column(Text)
    # sic_2003 = Column(Text)
    # sic_2007 = Column(Text)
    # turnover = Column(Integer)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, attributes, party, respondents=None):
        self.attributes = attributes
        self.party = party
        # self.respondents = respondents


class BusinessRespondentStatus(enum.Enum):
    ACTIVE = 0
    INACTIVE = 1
    SUSPENDED = 2
    ENDED = 3


class BusinessRespondent(Base):
    __tablename__ = 'business_respondent'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('business.id'))
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    status = Column('status', Enum(BusinessRespondentStatus))
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, status, effective_from, effective_to):
        self.status = status
        self.effective_from = effective_from
        self.effective_to = effective_to


class RespondentStatus(enum.Enum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2


class Respondent(Base):

    __tablename__ = 'respondent'

    id = Column(Integer, primary_key=True)
    businesses = relationship('Business', secondary='business_respondent', back_populates='respondents')
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship('Party', back_populates='respondent')
    status = Column('status', Enum(RespondentStatus))
    email_address = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    telephone = Column(Text)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, party_id, status, email_address, first_name, last_name, telephone):
        self.party_id = party_id
        self.status = status
        self.email_address = email_address
        self.first_name = first_name
        self.last_name = last_name
        self.telephone = telephone


class EnrolmentStatus(enum.Enum):
    PENDING = 0
    ENABLED = 1
    DISABLED = 2
    SUSPENDED = 3


class Enrolment(Base):

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


class EnrolmentCodeStatus(enum.Enum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentCode(Base):

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


class EnrolmentInvitationStatus(enum.Enum):
    ACTIVE = 0
    REDEEMED = 1
    REVOKED = 2


class EnrolmentInvitation(Base):

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
