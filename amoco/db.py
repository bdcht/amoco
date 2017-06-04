# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
db.py
=====

This module implements all amoco's database facilities using the
`sqlalchemy`_ package, allowing to store many analysis results and
pickled objects.

.. _sqlalchemy: http://www.sqlalchemy.org/

"""

from amoco.config import conf

from amoco.logger import Log,logging
logger = Log(__name__)

try:
    import sqlalchemy as sql
    from sqlalchemy import orm
    from sqlalchemy.ext.declarative import declarative_base
    has_sql = True
    Session = orm.scoped_session(orm.sessionmaker())
    Base = declarative_base()
    logflag = conf.getboolean('db','log')
    if logflag:
        for l in ('sqlalchemy.engine','sqlalchemy.orm'):
            alog = logging.getLogger(l)
            for h in logger.handlers: alog.addHandler(h)
            alog.setLevel(logger.level)
except ImportError:
    logger.warning(u"package sqlalchemy not found.")
    has_sql = False

def create(filename=None):
    """creates the database engine and bind it to the scoped Session class.
    The database URL (see :mod:`config.py`) is opened and the
    schema is created if necessary. The default URL uses *sqlite* dialect and
    opens a temporary file for storage.
    """
    import tempfile
    url = conf.get('db','url')
    if not url.endswith('.db'):
        if conf.has_option('log','file'):
            case = conf.get('log','file').rpartition('.')[0]
        else:
            case = tempfile.mktemp(prefix='amoco-')
        url += case+'.db'
    logflag = conf.getboolean('db','log')
    if has_sql:
        engine = sql.create_engine(url,echo=False,logging_name=__name__)
        Session.configure(bind=engine)
        Case.metadata.create_all(bind=engine,checkfirst=True)
    else:
        logger.error(u'No Session defined')
        engine = None
    return engine

if has_sql:
    class Case(Base):
        """A Case instance describes the analysis of some binary program.
        It allows to query stored results by date, source, format or
        architecture for example, and provides relations to associated
        functions that have been discovered or saved traces. 
        """
        __tablename__ = 'cases_info'
        id     = sql.Column(sql.Integer, primary_key=True)
        date   = sql.Column(sql.DateTime)
        name   = sql.Column(sql.String)
        source = sql.Column(sql.String)
        binfmt = sql.Column(sql.String)
        arch   = sql.Column(sql.String)
        msize  = sql.Column(sql.Integer)
        score  = sql.Column(sql.Integer,default=0)
        method = sql.Column(sql.String)
        funcs  = orm.relationship('FuncData',back_populates='case')
        other  = orm.relationship('CfgData',back_populates='case')
        traces = orm.relationship('Trace',back_populates='case')

        def __init__(self,z,name=None):
            from datetime import datetime
            from os.path import basename,splitext
            self.date = datetime.now()
            self.source = z.prog.bin.filename
            self.name = name or splitext(basename(self.source))[0]
            self.binfmt = z.prog.bin.__class__.__name__
            self.arch = z.prog.cpu.__name__
            self.msize = len(z.prog.mmap)
            self.method = z.__class__.__name__
            if z.G.order()>0:
                self.score = z.score()
                F = z.functions()
                for f in F: self.funcs.append(FuncData(f))
                F = [f.cfg for f in F]
                for g in z.G.C:
                    if g not in F:
                        self.other.append(CfgData(obj=g))

        def __repr__(self):
            s = (self.id, self.name, self.binfmt, self.arch, self.method)
            return u"<Case #{}: {:<.016} ({},{}) using {}>".format(*s)

    class FuncData(Base):
        """This class holds pickled :class:`~cas.mapper.mapper` and
        :class:`code.func` instances related to a Case, and provides
        relationship with gathered infos about the discovered function.
        """
        __tablename__ = 'funcs_data'
        id     = sql.Column(sql.Integer, primary_key=True)
        fmap   = orm.deferred(sql.Column(sql.PickleType))
        obj    = orm.deferred(sql.Column(sql.PickleType))
        case_id= sql.Column(sql.Integer, sql.ForeignKey('cases_info.id'))
        case   = orm.relationship('Case',back_populates='funcs')
        info   = orm.relationship('FuncInfo',uselist=False,back_populates='data')

        def __init__(self,f):
            self.fmap = f.map
            self.obj  = f
            self.info = FuncInfo(f,self)

    class FuncInfo(Base):
        """This class gathers useful informations about a function, allowing
        to query by signature or various characteristics like number of blocks,
        number of args, stack size, byte size, number of instructions, calls,
        or cross-references.
        """
        __tablename__ = 'funcs_info'
        id     = sql.Column(sql.Integer, sql.ForeignKey('funcs_data.id'),primary_key=True)
        name   = sql.Column(sql.String, nullable=False)
        sig    = sql.Column(sql.String)
        blocks = sql.Column(sql.Integer)
        argsin = sql.Column(sql.Integer)
        argsout= sql.Column(sql.Integer)
        stksz  = sql.Column(sql.Integer)
        vaddr  = sql.Column(sql.Integer)
        bsize  = sql.Column(sql.Integer)
        nbinst = sql.Column(sql.Integer)
        calls  = sql.Column(sql.String)
        xrefs  = sql.Column(sql.String)
        data   = orm.relationship('FuncData',uselist=False,back_populates='info')
        notes  = orm.deferred(sql.Column(sql.Text,default=''))

        def __init__(self,f,data):
            from amoco.cfg import signature
            self.name = f.name
            self.sig  = signature(f.cfg)
            self.blocks = f.cfg.order()
            self.argsin = f.misc['func_in']
            self.argsout = f.misc['func_out']
            self.stksz = min([x.a.disp for x in f.misc['func_var']],0)
            self.vaddr = str(f.address)
            self.bsize = sum([b.length for b in f.blocks],0)
            self.nbinst = sum([len(b.instr) for b in f.blocks],0)
            self.calls = ' '.join(filter(None,[x.name if hasattr(x,'cfg') else None for x in f.blocks]))
            self.xrefs = ' '.join([str(x.data.support[1]) for x in f.cfg.sV[0].data.misc['callers']])

    class CfgData(Base):
        """The CfgData class is intented to pickle data that has not yet been
        identified as a function but is part of the recovered :class:graph.
        """
        __tablename__ = 'cfgs_data'
        id     = sql.Column(sql.Integer, primary_key=True)
        obj    = orm.deferred(sql.Column(sql.PickleType))
        case_id= sql.Column(sql.Integer, sql.ForeignKey('cases_info.id'))
        case   = orm.relationship('Case', back_populates='other')

    class Trace(Base):
        """The Trace class allows to pickle abstract memory states (:class:`mapper` objects)
        obtained from a given input map after executing the binary program from *start* address
        to *stop* address.
        """
        __tablename__ = 'traces_data'
        id     = sql.Column(sql.Integer, primary_key=True)
        start  = sql.Column(sql.Integer)
        stop   = sql.Column(sql.Integer)
        mapin  = orm.deferred(sql.Column(sql.PickleType))
        mapout = orm.deferred(sql.Column(sql.PickleType))
        case_id= sql.Column(sql.Integer, sql.ForeignKey('cases_info.id'))
        case   = orm.relationship('Case', back_populates='traces')

