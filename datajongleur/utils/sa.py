import numpy as np
import zlib
import uuid

import sqlalchemy as sa
from sqlalchemy.orm.util import has_identity
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy.types import TypeDecorator, CHAR
import uuid

from datajongleur import Base, DBSession, cj

class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
      if False: #dialect.name == 'postgresql':
          return dialect.type_descriptor(UUID())
      else:
          return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif False: #dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
 

class UUIDMixin(object):
  @declared_attr
  def __tablename__(cls):
      return cls.__name__.lower()
  uuid = sa.Column('uuid', UUID, unique=True,
      default=uuid.uuid4,
      primary_key=True)


class NumpyType (sa.types.TypeDecorator):
  impl = sa.types.LargeBinary

  def process_bind_param(self, value, dialect):
    return zlib.compress(value.dumps(), 9)

  def process_result_value(self, value, dialect):
    return np.loads(zlib.decompress(value))


class NumpyTypePGSpecific (sa.types.TypeDecorator):
  """
  see `<http://www.sqlalchemy.org/docs/core/types.html>`_
  """
  impl = sa.types.LargeBinary

  def load_dialect_impl(self, dialect):
    if False: #dialect.name == 'postgresql':
      return dialect.type_descriptor(ARRAY(sa.Float))
    else:
      return dialect.type_descriptor(sa.types.LargeBinary)

  def process_bind_param(self, value, dialect):
    """
    not adjusted yet
    """
    return zlib.compress(value.dumps(), 9)

  def process_result_value(self, value, dialect):
    """
    not adjusted yet
    """
    return np.loads(zlib.decompress(value))

#######################
## Decorators        ##

def getSession():
  return DBSession()

def passAttrDTO(cls):
  def genGetMyAttr(attr_name):
    def getMyAttr(self):
      try:
        dto = self.getDTO()
        if has_identity(dto):
          return getattr(self.getDTO(), attr_name)
        return
      except Exception, e:
        print Exception
        print e
    return getMyAttr
  #cls.getKey = genGetMyAttr('key')
  #cls.key = property(cls.getKey)
  cls.getUUID = genGetMyAttr('uuid')
  cls.uuid = property(cls.getUUID)
  return cls

def addInfoQuantityDBAccess():
  """
  This decorator adds the following methods:
  * ``load(PK)``
  * ``save()``
  """
  def decorateClass(cls):
    @classmethod
    def newBySession(cls, uuid):
      if not hasattr(cls, "session"):
        cls.session = getSession()
      dto = cls.session.query(cls._DTO).filter(
          getattr(cls._DTO, 'uuid') == uuid).first()
      return cls.newByDTO(dto)
    @classmethod
    def load(cls, uuid):
      return cls.newBySession(uuid)
    def save(self):
      if not hasattr(self, "session"):
        self.__class__.session = getSession()
      dto = self.getDTO()
      uuid = self.getUUID()
      self.session.add (dto)
      self.session.commit ()
      if uuid is not self.uuid:
        print "Assigned attribute ``uuid`` --> %r" % (self.uuid)
      
    cls.newBySession = newBySession
    cls.load = load
    cls.save = save
    return cls
  return decorateClass

## (end: Decorators) ##
#######################

"""
def connectDB(filename='db_setup.ini'):
  from sqlalchemy import engine_from_config
  from datajongleur import initialize_sql
  config = LoadConfig(filename)
  engine = engine_from_config(config, 'sqlalchemy.')
  initialize_sql(engine)
"""

