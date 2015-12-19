# This is a trimmed down version of SELAFIN IO reader/writer utilities
# originally written by HRW for the TELEMAC system

# This was modified to depend only on stuff found in ppmodules

# ~~> dependencies towards standard python
from struct import unpack,pack
import sys
from os import path,getcwd
import glob
from copy import deepcopy
import numpy as np
from ppmodules.ProgressBar import *

def getFloatTypeFromFloat(f,endian,nfloat):
   pointer = f.tell()
   ifloat = 4
   cfloat = 'f'
   l = unpack(endian+'i',f.read(4))
   if l[0]!=ifloat*nfloat:
      ifloat = 8
      cfloat = 'd'
   r = unpack(endian+str(nfloat)+cfloat,f.read(ifloat*nfloat))
   chk = unpack(endian+'i',f.read(4))
   if l!=chk:
      print '... Cannot read '+str(nfloat)+' floats from your binary file'
      print '     +> Maybe it is the wrong file format ?'
      sys.exit(1)
   f.seek(pointer)
   return cfloat,ifloat

def getEndianFromChar(f,nchar):
   pointer = f.tell()
   endian = ">"       # "<" means little-endian, ">" means big-endian
   l,c,chk = unpack(endian+'i'+str(nchar)+'si',f.read(4+nchar+4))
   if chk!=nchar:
      endian = "<"
      f.seek(pointer)
      l,c,chk = unpack(endian+'i'+str(nchar)+'si',f.read(4+nchar+4))
   if l!=chk:
      print '... Cannot read '+str(nchar)+' characters from your binary file'
      print '     +> Maybe it is the wrong file format ?'
      sys.exit(1)
   f.seek(pointer)
   return endian

def getFileContent(file):
   ilines = []
   SrcF = open(file,'r')
   for line in SrcF:
      ilines.append(line)
   SrcF.close()
   return ilines

def putFileContent(file,lines):
   if path.exists(file): remove(file)
   SrcF = open(file,'wb')
   if len(lines)>0:
      ibar = 0; pbar = ProgressBar(maxval=len(lines)).start()
      SrcF.write((lines[0].rstrip()).replace('\r','').replace('\n\n','\n'))
      for line in lines[1:]:
         pbar.update(ibar); ibar += 1
         SrcF.write('\n'+(line.rstrip()).replace('\r','').replace('\n\n','\n'))
      pbar.finish()
   SrcF.close()
   return

def subsetVariablesSLF(vars,ALLVARS):
   ids = []; names = []
   # vars has the form "var1:object;var2:object;var3;var4"
   # /!\ the ; separator might be a problem for command line action
   v = vars.replace(',',';').split(';')
   for ivar in range(len(v)):
      vi = v[ivar].split(':')[0]
      for jvar in range(len(ALLVARS)):
         if vi.lower() in ALLVARS[jvar].lower():  #.strip()
            ids.append(jvar)
            names.append(ALLVARS[jvar].strip())
   if len(ids) < len(v):
      print "... Could not find ",v," in ",ALLVARS
      print "   +> may be you forgot to switch name spaces into underscores in your command ?"
      sys.exit(1)

   return ids,names

def getValueHistorySLF( hook,tags,time,support,NVAR,NPOIN3,NPLAN,(varsIndexes,varsName) ):
   """
      Extraction of time series at points.
      A point could be:
      (a) A point could be a node 2D associated with one or more plan number
      (b) A pair (x,y) associated with one or more plan number
/!\   Vertical interpolation has not been implemented yet.
      Arguments:
      - time: the discrete list of time frame to extract from the time history
      - support: the list of points
      - varsIndexes: the index in the NVAR-list to the variable to extract
   """
   f = hook['hook']
   endian = hook['endian']
   ftype,fsize = hook['float']
   
   # ~~ Total size of support ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   lens = 0
   for xy,zp in support: lens += len(zp)

   # ~~ Extract time profiles ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   z = np.zeros((len(varsIndexes),lens,len(time)))
   for it in range(len(time)):            # it is from 0 to len(time)-1
      f.seek(tags['cores'][time[it]])     # time[it] is the frame to be extracted
      f.seek(4+fsize+4,1)                     # the file pointer is initialised
      for ivar in range(NVAR):            # ivar is from 0 to NVAR-1
         f.seek(4,1)                      # the file pointer advances through all records to keep on track
         if ivar in varsIndexes:          # extraction of a particular variable
            VARSOR = unpack(endian+str(NPOIN3)+ftype,f.read(fsize*NPOIN3))
            jvar = varsIndexes.index(ivar)
            ipt = 0                       # ipt is from 0 to lens-1 (= all points extracted and all plans extracted)
            for xy,zp in support:
               if type(xy) == type(()):   # xp is a pair (x,y) and you need interpolation
                  for plan in zp:   # /!\ only list of plans is allowed for now
                     z[jvar][ipt][it] = 0.
                     ln,bn = xy
                     for inod in range(len(bn)): z[jvar][ipt][it] += bn[inod]*VARSOR[ln[inod]+plan*NPOIN3/NPLAN]
                     ipt += 1             # ipt advances to keep on track
               else:
                  for plan in zp:   # /!\ only list of plans is allowed for now
                     z[jvar][ipt][it] = VARSOR[xy+plan*NPOIN3/NPLAN]
                     ipt += 1             # ipt advances to keep on track
         else:
            f.seek(fsize*NPOIN3,1)            # the file pointer advances through all records to keep on track
         f.seek(4,1)

   return z

class SELAFIN:

   DATETIME = [1972,07,13,17,24,27]  # ... needed here because optional in SLF (static)
   
   def __init__(self,fileName):
      self.file = {}
      self.file.update({ 'name': fileName })
      self.file.update({ 'endian': ">" })    # "<" means little-endian, ">" means big-endian
      self.file.update({ 'float': ('f',4) }) #'f' size 4, 'd' = size 8
      if fileName != '':
         self.file.update({ 'hook': open(fileName,'rb') })
         # ~~> checks endian encoding
         self.file['endian'] = getEndianFromChar(self.file['hook'],80)
         # ~~> header parameters
         self.tags = { 'meta': self.file['hook'].tell() } #TODO remove?
         self.getHeaderMetaDataSLF()
         # ~~> sizes and connectivity
         self.getHeaderIntegersSLF()
         # ~~> checks float encoding
         self.file['float'] = getFloatTypeFromFloat(self.file['hook'],self.file['endian'],self.NPOIN3)
         # ~~> xy mesh
         self.getHeaderFloatsSLF()
         # ~~> time series
         self.tags = { 'cores':[],'times':[] }
         self.getTimeHistorySLF()
      else:
         self.TITLE = ''
         self.NBV1 = 0; self.NBV2 = 0; self.NVAR = self.NBV1 + self.NBV2
         self.VARINDEX = range(self.NVAR)
         self.IPARAM = []
         self.NELEM3 = 0; self.NPOIN3 = 0; self.NDP3 = 0; self.NPLAN = 1
         self.NELEM2 = 0; self.NPOIN2 = 0; self.NDP2 = 0
         self.NBV1 = 0; self.VARNAMES = []; self.VARUNITS = []
         self.NBV2 = 0; self.CLDNAMES = []; self.CLDUNITS = []
         self.IKLE3 = []; self.IKLE2 = []; self.IPOB2 = []; self.IPOB3 = []; self.MESHX = []; self.MESHY = []
         self.tags = { 'cores':[],'times':[] }
      self.fole = {}
      self.fole.update({ 'name': '' })
      self.fole.update({ 'endian': self.file['endian'] })
      self.fole.update({ 'float': self.file['float'] })
      self.tree = None
      self.neighbours = None
      self.edges = None
      self.alterZnames = []

   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #   Parsing the Big- and Little-Endian binary file
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHeaderMetaDataSLF(self):
      f = self.file['hook']
      endian = self.file['endian']
      # ~~ Read title ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      l,self.TITLE,chk = unpack(endian+'i80si',f.read(4+80+4))
      # ~~ Read NBV(1) and NBV(2) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      l,self.NBV1,self.NBV2,chk = unpack(endian+'iiii',f.read(4+8+4))
      self.NVAR = self.NBV1 + self.NBV2
      self.VARINDEX = range(self.NVAR)
      # ~~ Read variable names and units ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      self.VARNAMES = []; self.VARUNITS = []
      for _ in range(self.NBV1):
         l,vn,vu,chk = unpack(endian+'i16s16si',f.read(4+16+16+4))
         self.VARNAMES.append(vn)
         self.VARUNITS.append(vu)
      self.CLDNAMES = []; self.CLDUNITS = []
      for _ in range(self.NBV2):
         l,vn,vu,chk = unpack(endian+'i16s16si',f.read(4+16+16+4))
         self.CLDNAMES.append(vn)
         self.CLDUNITS.append(vu)
      # ~~ Read IPARAM array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      d = unpack(endian+'12i',f.read(4+40+4))
      self.IPARAM = np.asarray( d[1:11] )
      # ~~ Read DATE/TIME array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      self.DATETIME = [1972,07,13,17,15,13]
      if self.IPARAM[9] == 1:
         d = unpack(endian+'8i',f.read(4+24+4))
         self.DATETIME = np.asarray( d[1:9] )

   def getHeaderIntegersSLF(self):
      f = self.file['hook']
      endian = self.file['endian']
      # ~~ Read NELEM3, NPOIN3, NDP3, NPLAN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      l,self.NELEM3,self.NPOIN3,self.NDP3,self.NPLAN,chk = unpack(endian+'6i',f.read(4+16+4))
      self.NELEM2 = self.NELEM3
      self.NPOIN2 = self.NPOIN3
      self.NDP2 = self.NDP3
      self.NPLAN = max( 1,self.NPLAN )
      if self.IPARAM[6] > 1:
         self.NPLAN = self.IPARAM[6] # /!\ How strange is that ?
         self.NELEM2 = self.NELEM3 / ( self.NPLAN - 1 )
         self.NPOIN2 = self.NPOIN3 / self.NPLAN
         self.NDP2 = self.NDP3 / 2
      # ~~ Read the IKLE array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.seek(4,1)
      self.IKLE3 = np.array( unpack(endian+str(self.NELEM3*self.NDP3)+'i',f.read(4*self.NELEM3*self.NDP3)) ) - 1
      f.seek(4,1)
      self.IKLE3 = self.IKLE3.reshape((self.NELEM3,self.NDP3))
      if self.NPLAN > 1: self.IKLE2 = np.compress( np.repeat([True,False],self.NDP2), self.IKLE3[0:self.NELEM2], axis=1 )
      else: self.IKLE2 = self.IKLE3
      # ~~ Read the IPOBO array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.seek(4,1)
      self.IPOB3 = np.asarray( unpack(endian+str(self.NPOIN3)+'i',f.read(4*self.NPOIN3)) )
      f.seek(4,1)
      self.IPOB2 = self.IPOB3[0:self.NPOIN2]

   def getHeaderFloatsSLF(self):
      f = self.file['hook']
      endian = self.file['endian']
      # ~~ Read the x-coordinates of the nodes ~~~~~~~~~~~~~~~~~~
      ftype,fsize = self.file['float']
      f.seek(4,1)
      self.MESHX = np.asarray( unpack(endian+str(self.NPOIN3)+ftype,f.read(fsize*self.NPOIN3))[0:self.NPOIN2] )
      f.seek(4,1)
      # ~~ Read the y-coordinates of the nodes ~~~~~~~~~~~~~~~~~~
      f.seek(4,1)
      self.MESHY = np.asarray( unpack(endian+str(self.NPOIN3)+ftype,f.read(fsize*self.NPOIN3))[0:self.NPOIN2] )
      f.seek(4,1)
      
   def getTimeHistorySLF(self):
      f = self.file['hook']
      endian = self.file['endian']
      ftype,fsize = self.file['float']
      ATs = []; ATt = []
      while True:
         try:
            ATt.append(f.tell())
            # ~~ Read AT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            f.seek(4,1)
            ATs.append(unpack(endian+ftype,f.read(fsize))[0])
            f.seek(4,1)
            # ~~ Skip Values ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            f.seek(self.NVAR*(4+fsize*self.NPOIN3+4),1)
         except:
            ATt.pop(len(ATt)-1)   # since the last record failed the try
            break
      self.tags.update({ 'cores': ATt })
      self.tags.update({ 'times': np.asarray(ATs) })

   def getVariablesAt( self,frame,varsIndexes ):
      f = self.file['hook']
      endian = self.file['endian']
      ftype,fsize = self.file['float']
      z = np.zeros((len(varsIndexes),self.NPOIN3))
      # if tags has 31 frames, len(tags)=31 from 0 to 30, then frame should be >= 0 and < len(tags)
      if frame < len(self.tags['cores']) and frame >= 0:
         f.seek(self.tags['cores'][frame])
         f.seek(4+fsize+4,1)
         for ivar in range(self.NVAR):
            f.seek(4,1)
            if ivar in varsIndexes:
               z[varsIndexes.index(ivar)] = unpack(endian+str(self.NPOIN3)+ftype,f.read(fsize*self.NPOIN3))
            else:
               f.seek(fsize*self.NPOIN3,1)
            f.seek(4,1)
      return z
   
   def alterEndian(self):
      if self.fole['endian'] == ">": self.fole['endian'] = "<"
      else: self.fole['endian'] = ">"

   def alterFloat(self):
      if self.fole['float'] == ('f',4): self.fole['float'] = ('d',8)
      else: self.fole['float'] = ('f',4)
      
   def alterVALUES(self,vars=None,mZ=1,pZ=0):
      if vars != None:
         self.alterZm = mZ; self.alterZp = pZ; self.alterZnames = vars.split(':')

   def appendHeaderSLF(self):
      f = self.fole['hook']
      endian = self.fole['endian']
      ftype,fsize = self.fole['float']
      # ~~ Write title ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i80si',80,self.TITLE,80))
     # ~~ Write NBV(1) and NBV(2) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'iiii',4+4,self.NBV1,self.NBV2,4+4))
      # ~~ Write variable names and units ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      for i in range(self.NBV1):
         f.write(pack(endian+'i',32))
         f.write(pack(endian+'16s',self.VARNAMES[i]))
         f.write(pack(endian+'16s',self.VARUNITS[i]))
         f.write(pack(endian+'i',32))
      for i in range(self.NBV2):
         f.write(pack(endian+'i',32))
         f.write(pack(endian+'16s',self.CLDNAMES[i]))
         f.write(pack(endian+'16s',self.CLDUNITS[i]))
         f.write(pack(endian+'i',32))
      # ~~ Write IPARAM array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i',4*10))
      for i in range(len(self.IPARAM)): f.write(pack(endian+'i',self.IPARAM[i]))
      f.write(pack(endian+'i',4*10))
      # ~~ Write DATE/TIME array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      if self.IPARAM[9] == 1:
         f.write(pack(endian+'i',4*6))
         for i in range(6): f.write(pack(endian+'i',self.DATETIME[i]))
         f.write(pack(endian+'i',4*6))
      # ~~ Write NELEM3, NPOIN3, NDP3, NPLAN ~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'6i',4*4,self.NELEM3,self.NPOIN3,self.NDP3,1,4*4))  #/!\ where is NPLAN ?
      # ~~ Write the IKLE array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i',4*self.NELEM3*self.NDP3))
      f.write(pack(endian+str(self.NELEM3*self.NDP3)+'i',*(n+1 for e in self.IKLE3 for n in e)))
      f.write(pack(endian+'i',4*self.NELEM3*self.NDP3))
      # ~~ Write the IPOBO array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i',4*self.NPOIN3))
      f.write(pack(endian+str(self.NPOIN3)+'i',*(self.IPOB3)))
      f.write(pack(endian+'i',4*self.NPOIN3))
      # ~~ Write the x-coordinates of the nodes ~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i',fsize*self.NPOIN3))
      f.write(pack(endian+str(self.NPOIN3)+ftype,*(np.tile(self.MESHX,self.NPLAN))))
      f.write(pack(endian+'i',fsize*self.NPOIN3))
      # ~~ Write the y-coordinates of the nodes ~~~~~~~~~~~~~~~~~~~~~~~
      f.write(pack(endian+'i',fsize*self.NPOIN3))
      f.write(pack(endian+str(self.NPOIN3)+ftype,*(np.tile(self.MESHY,self.NPLAN))))
      f.write(pack(endian+'i',fsize*self.NPOIN3))

   def appendCoreTimeSLF( self,t ):
      f = self.fole['hook']
      endian = self.fole['endian']
      ftype,fsize = self.fole['float']
      # Print time record
      if type(t) == type(0.0): f.write(pack(endian+'i'+ftype+'i',4,t,4))
      else: f.write(pack(endian+'i'+ftype+'i',4,self.tags['times'][t],4))

   def appendCoreVarsSLF( self,VARSOR ):
      f = self.fole['hook']
      endian = self.fole['endian']
      ftype,fsize = self.fole['float']
      # Print variable records
      for v in VARSOR:
         f.write(pack(endian+'i',fsize*self.NPOIN3))
         f.write(pack(endian+str(self.NPOIN3)+ftype,*(v)))
         f.write(pack(endian+'i',fsize*self.NPOIN3))

   def putContent( self,fileName,showbar=True ):
      self.fole.update({ 'name': fileName })
      self.fole.update({ 'hook': open(fileName,'wb') })
      ibar = 0
      if showbar: pbar = ProgressBar(maxval=len(self.tags['times'])).start()
      self.appendHeaderSLF()
      for t in range(len(self.tags['times'])):
         ibar += 1
         self.appendCoreTimeSLF(t)
         self.appendCoreVarsSLF(self.getVALUES(t))
         if showbar: pbar.update(ibar)
      self.fole['hook'].close()
      if showbar: pbar.finish()

   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #   Tool Box
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   def getVALUES( self,t ):
      VARSOR = self.getVariablesAt( t,self.VARINDEX )
      for v in self.alterZnames:
         for iv in range(len(self.VARNAMES)):
            if v.lower() in self.VARNAMES[iv].lower(): VARSOR[iv] = self.alterZm * VARSOR[iv] + self.alterZp
         for iv in range(len(self.CLDNAMES)):
            if v.lower() in self.CLDNAMES[iv].lower(): VARSOR[iv+self.NBV1] = self.alterZm * VARSOR[iv+self.NBV1] + self.alterZp
      return VARSOR

   def getSERIES( self,nodes,varsIndexes=[],showbar=True ):
      f = self.file['hook']
      endian = self.file['endian']
      ftype,fsize = self.file['float']
      if varsIndexes == []: varsIndexes = self.VARINDEX
      # ~~ Ordering the nodes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      # This assumes that nodes starts at 1
      onodes = np.sort(np.array( zip(range(len(nodes)),nodes), dtype=[ ('0',int),('1',int) ] ),order='1')
      # ~~ Extract time profiles ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      z = np.zeros((len(varsIndexes),len(nodes),len(self.tags['cores'])))
      f.seek(self.tags['cores'][0])
      if showbar: pbar = ProgressBar(maxval=len(self.tags['cores'])).start()
      for t in range(len(self.tags['cores'])):
         f.seek(self.tags['cores'][t])
         f.seek(4+fsize+4,1)
         if showbar: pbar.update(t)
         for ivar in range(self.NVAR):
            f.seek(4,1)
            if ivar in varsIndexes:
               jnod = onodes[0]
               f.seek(fsize*(jnod[1]-1),1)
               z[varsIndexes.index(ivar),jnod[0],t] = unpack(endian+ftype,f.read(fsize))[0]
               for inod in onodes[1:]:
                  f.seek(fsize*(inod[1]-jnod[1]-1),1)
                  z[varsIndexes.index(ivar),inod[0],t] = unpack(endian+ftype,f.read(fsize))[0]
                  jnod = inod
               f.seek(fsize*self.NPOIN3-fsize*jnod[1],1)
            else:
               f.seek(fsize*self.NPOIN3,1)
            f.seek(4,1)
      if showbar: pbar.finish()
      return z

   def __del__(self):
      if self.file['name'] != '': self.file['hook'].close()
