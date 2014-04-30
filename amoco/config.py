from collections import defaultdict

from amoco.logger import Log
logger = Log(__name__)

try:
    import ConfigParser as cp
except ImportError:
    logger.info('ConfigParser not found, fallback to default config')
    cp = None


if cp:
    import os
    conf = cp.SafeConfigParser()
    conf.add_section('block')
    conf.set('block', 'header', 'True')
    conf.set('block', 'bytecode', 'True')
    conf.set('block', 'padding', '4')
    conf.read([os.path.expanduser('~/.amocorc')])
else:
    conf = None

    class DefaultConf(object):
        def __init__(self):
            self.sections = defaultdict(lambda :{})
            self.setdefaults()

        def get(self,section,item):
            s = self.sections[section]
            return s.get(item,None) if s else None

        def getint(self,section,item):
            v = self.get(section,item)
            if v is not None: return int(v,0)
            return v

        def getboolean(self,section,item):
            v = self.get(section,item)
            if v is not None: return bool(v=='True')
            return v

        def set(self,section,item,value):
            s = self.sections[section]
            s[item] = value

        def mset(self,section,**kargs):
            for k,v in kargs.iteritems():
                self.set(section, k, v)

        def write(self,filename):
            with open(filename,'w') as f:
                for sk,sv in self.sections.iteritems():
                    f.write('[%s]\n'%sk)
                    for vk,vv in sv.iteritems():
                        f.write('%s: %s\n'%(vk,vv))

        def setdefaults(self):
            self.mset('block', header=True)
            self.mset('block', bytecode=True)
            self.mset('block', padding=4)

    conf = DefaultConf()
