#!/usr/local/uvcdat/1.3.1/bin/python


# TODO List
# DONE 1) Fix up set6b level plots (need one more level of lambda abstraction?) 
# DONE 2) Finish 6b soil ice/water (need clean way to sum levels 1:10) 
# DONE 3) Redo derived vars in 1,2,3, and 6 (given DUVs functionality, revisit things like evapfrac) 
# 4) Fix obs vs model variable name issues (requires lots of framework changes, probably need Jeff to poke at it)
# 5) Merge set3b and 6b code since it is very similar
# 6) Further code clean up IN PROGRESS
# 7) Work on set 5 IN PROGRESS

from metrics.packages.diagnostic_groups import *
#from metrics.packages.common.diagnostic_groups import *
from metrics.computation.reductions import *
from metrics.frontend.uvcdat import *
from metrics.computation.plotspec import *
import metrics.frontend.defines as defines


### Derived unreduced variables (DUV) definitions
### These are variables that are nonlinear or require 2 passes to get a final
### result. 

# Probably could pass the reduction_function for all of these instead of a flag, but this puts
# all of the reduction functions in the same place in case they need to change or something.
class evapfrac_redvar ( reduced_variable ):
   def __init__(self, filetable, fn, season=None, region=None, flag=None):
      duv = derived_var('EVAPFRAC_A', inputs=['FCTR', 'FCEV', 'FGEV', 'FSH'], func=evapfrac_special)
      if fn == 'SEASONAL':
         reduced_variable.__init__(
            self, variableid='EVAPFRAC_A',
            filetable=filetable,
            reduction_function=(lambda x, vid=None: reduce2latlon_seasonal(x, season, vid=vid)),
            duvs={'EVAPFRAC_A':duv})
      if fn == 'TREND':
         if flag == 'MONTHLY':
            reduced_variable.__init__(
               self, variableid='EVAPFRAC_A', 
               filetable=filetable, 
               reduction_function=(lambda x, vid=None: reduceMonthlyTrendRegion(x, region, vid=vid)),
               duvs={'EVAPFRAC_A':duv})
         else:
            reduced_variable.__init__(
               self, variableid='EVAPFRAC_A', 
               filetable=filetable, 
               reduction_function=(lambda x, vid=None: reduceAnnTrendRegion(x, region, vid=vid)),
               duvs={'EVAPFRAC_A':duv})
         
class rnet_redvar( reduced_variable ):
   def __init__(self, filetable, fn, season=None, region=None, flag=None):
      duv = derived_var('RNET_A', inputs=['FSA', 'FIRA'], func=aminusb)
      if fn == 'SEASONAL':
         reduced_variable.__init__(
            self, variableid='RNET_A',
            filetable=filetable,
            reduction_function=(lambda x, vid=None: reduce2latlon_seasonal(x, season, vid=vid)),
            duvs={'RNET_A': duv})
      if fn == 'TREND':
         if flag == 'MONTHLY':
            reduced_variable.__init__(
               self, variableid='RNET_A',
               filetable=filetable,
               reduction_function=(lambda x, vid=None: reduceMonthlyTrendRegion(x, region, vid=vid)),
               duvs={'RNET_A':duv})
         else:
            reduced_variable.__init__(
               self, variableid='RNET_A',
               filetable=filetable,
               reduction_function=(lambda x, vid=None: reduceAnnTrendRegion(x, region, vid=vid)),
               duvs={'RNET_A':duv})
      if fn == 'SINGLE':
         reduced_variable.__init__(
            self, variableid='RNET_A',
            filetable=filetable,
            reduction_function=(lambda x, vid=None: reduceAnnTrendRegionSingle(x, region, vid=vid)),
            duvs={'RNET_A':duv})

class albedos_redvar( reduced_variable ):
   def __init__(self, filetable, fn, varlist, season=None, region=None, flag=None):
      vname = varlist[0]+'_'+varlist[1]
      duv = derived_var(vname, inputs=varlist, func=ab_ratio)
      if fn == 'SEASONAL':
         reduced_variable.__init__(
            self, variableid=vname,
            filetable=filetable,
            reduction_function=(lambda x, vid=None: reduce2latlon_seasonal(x, season, vid=vid)),
            duvs={vname: duv})
      if fn == 'TREND':
         if flag == 'MONTHLY':
            reduced_variable.__init__(
               self, variableid=vname,
               filetable=filetable,
               reduction_function=(lambda x, vid=None: reduceMonthlyTrendRegion(x, region, vid=vid)),
               duvs={vname: duv})
         else:
            reduced_variable.__init__(
               self, variableid=vname,
               filetable=filetable,
               reduction_function=(lambda x, vid=None: reduceAnnTrendRegion(x, region, vid=vid)),
               duvs={vname: duv})
      if fn == 'SINGLE':
         reduced_variable.__init__(
            self, variableid=vname,
            filetable=filetable1,
            reduction_function=(lambda x, vid: reduceAnnTrendRegionSingle(x, region, vid=vid)),
            duvs={vname:duv})

# A couple only used for one set, so don't need more generalized.
class pminuse_seasonal( reduced_variable ):
   def __init__(self, filetable, season):
      duv = derived_var('P-E_A', inputs=['RAIN', 'SNOW', 'QSOIL', 'QVEGE', 'QVEGT'], func=pminuse)
      reduced_variable.__init__(
         self, variableid='P-E_A',
         filetable=filetable,
         reduction_function=(lambda x, vid=None: reduce2latlon_seasonal(x, season, vid=vid)),
         duvs={'P-E_A':duv})

class qvegepTrendRegionSingle( reduced_variable ):
   def __init__(self, filetable, region):
      duv = derived_var('QVEGEP_A', inputs=['QVEGE', 'RAIN',' SNOW'], func=qvegep_special)
      reduced_variable.__init__(
         self, variableid='QVEGEP_A',
         filetable=filetable,
         reduction_function=(lambda x, vid: reduceAnnTrendRegionSingle(x, region, vid=vid)),
         duvs={'QVEGEP_A':duv})

class LMWG(BasicDiagnosticGroup):
    #This class defines features unique to the LMWG Diagnostics.
    #This is basically a copy and stripping of amwg.py since I can't
    #figure out the code any other way. I am hoping to simplify this
    #at some point. I would very much like to drop the "sets" baggage 
    #from NCAR and define properties of diags. Then, "sets" could be
    #very simple descriptions involving highly reusable components.
    
    def __init__(self):
        pass
      
    def list_variables( self, filetable1, filetable2=None, diagnostic_set_name="" ):
        if diagnostic_set_name!="":
            dset = self.list_diagnostic_sets().get( str(diagnostic_set_name), None )
            if dset is None:
                return self._list_variables( filetable1, filetable2 )
            else:   # Note that dset is a class not an object.
                return dset._list_variables( filetable1, filetable2 )
        else:
            return self._list_variables( filetable1, filetable2 )
    @staticmethod
    def _list_variables( filetable1, filetable2=None, diagnostic_set_name="" ):
        return BasicDiagnosticGroup._list_variables( filetable1, filetable2, diagnostic_set_name )

    @staticmethod
    def _all_variables( filetable1, filetable2, diagnostic_set_name ):
        return BasicDiagnosticGroup._all_variables( filetable1, filetable2, diagnostic_set_name )

    def list_diagnostic_sets( self ):
        psets = lmwg_plot_spec.__subclasses__()
        plot_sets = psets
        for cl in psets:
            plot_sets = plot_sets + cl.__subclasses__()
        foo2 = {}
        for aps in plot_sets:
         if hasattr(aps, 'name'):
            foo2[aps.name] = aps

#        foo = { aps.name:aps for aps in plot_sets if hasattr(aps,'name') }
        return foo2
        #return { aps.name:(lambda ft1, ft2, var, seas: aps(ft1,ft2,var,seas,self))
        #         for aps in plot_sets if hasattr(aps,'name') }

class lmwg_plot_spec(plot_spec):
    package = LMWG  # Note that this is a class not an object.. 
    albedos = {'VBSA':['FSRVDLN', 'FSDSVDLN'], 'NBSA':['FSRNDLN', 'FSDSNDLN'], 'VWSA':['FSRVI', 'FSDSVI'], 'NWSA':['FSRNI', 'FSDSNI'], 'ASA':['FSR', 'FSDS']}
    @staticmethod
    def _list_variables( filetable1, filetable2=None ):
        return lmwg_plot_spec.package._list_variables( filetable1, filetable2, "lmwg_plot_spec" )
    @staticmethod
    def _all_variables( filetable1, filetable2=None ):
        return lmwg_plot_spec.package._all_variables( filetable1, filetable2, "lmwg_plot_spec" )


###############################################################################
###############################################################################
### Set 1 - Line plots of annual trends in energy balance, soil water/ice   ###
### and temperature, runoff, snow water/ice, photosynthesis                 ### 
###                                                                         ###
### Set 1 supports model vs model comparisons, but does not require model   ###
###  vs obs comparisons. so ft2 is always a model and can be treated the    ###
###  same as ft1 and will need no variable name translations. This assumes  ###
###  both models have the same variables as well.                           ###
###############################################################################
###############################################################################

### TODO: Fix up plots when 2 model runs are available. Should show ft1 and ft2
### on a single plot, then show difference of ft1 and ft2 below OR as a separate
### option. Today it is a seperate option, but that might complicate things too
### much.
### However, the level_vars should *probably* have a separate option for 
### difference plots because there would be 20 plots otherwise. 
### Perhaps this needs to be a command line option or GUI check box?
class lmwg_plot_set1(lmwg_plot_spec):
   varlist = []
   name = '1 - Line plots of annual trends in energy balance, soil water/ice and temperature, runoff, snow water/ice, photosynthesis '
   _derived_varnames = ['PREC', 'TOTRUNOFF', 'TOTSOILICE', 'TOTSOILLIQ']

   ### These are special cased since they have 10 levels plotted. However, they are not "derived" per se.
   _level_vars = ['SOILLIQ', 'SOILICE', 'SOILPSI', 'TSOI']

   def __init__(self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      plot_spec.__init__(self,seasonid)
      self.plottype = 'Yxvsx'

      self._var_baseid = '_'.join([varid, 'set1'])
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid
      if filetable2 is not None:
         self.plot2_id = ft2id+'_'+varid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid
      else:
         self.plotall_id = filetable1._strid+'_'+varid

      if not self.computation_planned:
         self.plan_computation(filetable1, filetable2, varid, seasonid, region, aux)

   @staticmethod
   def _list_variables(filetable1, filetable2=None):
      filevars = lmwg_plot_set1._all_variables(filetable1, filetable2)
      allvars = filevars
      listvars = allvars.keys()
      listvars.sort()
      return listvars

   @staticmethod
   def _all_variables(filetable1, filetable2=None):
      allvars = lmwg_plot_spec.package._all_variables(filetable1, filetable2, "lmwg_plot_spec")
      for dv in lmwg_plot_set1._derived_varnames:
         allvars[dv] = basic_plot_variable
         if filetable2 != None:
            if dv not in filetable2.list_variables():
               del allvars[dv]
      return allvars

   def plan_computation(self, filetable1, filetable2, varid, seasonid, region=None, aux=None):
      self.reduced_variables = {}
      self.derived_variables = {}
      # No need for a separate function just use global. 
      region = defines.all_regions['Global']

      # Take care of the oddballs first.
      if varid in lmwg_plot_set1._level_vars:
      # TODO: These should be combined plots for _1 and _2, and split off _3 into a separate thing somehow
         vbase=varid
         self.composite_plotspecs[self.plotall_id] = []
         for i in range(0,10):
            vn = vbase+str(i+1)+'_1'
            self.reduced_variables[vn] = reduced_variable(
               variableid = vbase, filetable=filetable1, reduced_var_id=vn,
               reduction_function=(lambda x, vid, i=i: reduceAnnTrendRegionLevel(x, region, i, vid))) 
            self.single_plotspecs[vn] = plotspec(vid=vn,
               zvars = [vn], zfunc=(lambda z:z),
               # z2, # z3,
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(vn)
         if filetable2 != None:
            for i in range(0,10):
               vn = vbase+str(i+1)
               self.reduced_variables[vn+'_2'] = reduced_variable(
                  variableid = vbase, filetable=filetable2, reduced_var_id=vn+'_2',
                  reduction_function=(lambda x, vid, i=i: reduceAnnTrendRegionLevel(x, region, i, vid)))
               self.single_plotspec[vn+'_2'] = plotspec(vid=vn+'_2',
                  zvars = [vn+'_2'], zfunc=(lambda z:z),
                  plottype = self.plottype)
               self.single_plotspec[vn+'_3'] = plotspec(
                  vid=vn+'_3', zvars = [vn+'_1', vn+'_2'],
                  zfunc=aminusb,
                  plottype = self.plottype)
               self.composite_plotspecs[self.plotall_id].append(vn+'_2')
               self.composite_plotspecs[self.plotall_id].append(vn+'_3')
               
      else: # Now everything else.
         # Get the easy ones first
         if varid not in lmwg_plot_set1._derived_varnames and varid not in lmwg_plot_set1._level_vars:
            self.reduced_variables[varid+'_1'] = reduced_variable(variableid = varid,
               filetable=filetable1, reduced_var_id = varid+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
   
            if(filetable2 != None):
               self.reduced_variables[varid+'_2'] = reduced_variable(variableid = varid,
                  filetable=filetable2, reduced_var_id = varid+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))

         # Now some derived variables.
         if varid == 'PREC' or varid == 'TOTRUNOFF':
            if varid == 'PREC':
               red_vars = ['RAIN', 'SNOW']
               myfunc = aplusb
            elif varid == 'TOTRUNOFF':
               red_vars = ['QSOIL', 'QVEGE', 'QVEGT']
               myfunc = sum3
            in1 = [x+'_1' for x in red_vars]
            in2 = [x+'_2' for x in red_vars]

            for v in red_vars:
               self.reduced_variables[v+'_1'] = reduced_variable(
                  variableid = v, filetable=filetable1, reduced_var_id = v+'_1',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            self.derived_variables[varid+'_1'] = derived_var(
               vid=varid+'_1', inputs=in1, func=myfunc)

            if filetable2 != None: ### Assume ft2 is 2nd model
               #print 'This is assuming 2nd dataset is also model output'
               for v in red_vars:
                  self.reduced_variables[v+'_2'] = reduced_variable(
                     variableid = v, filetable=filetable2, reduced_var_id = v+'_2',
                     reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
               self.derived_variables[varid+'_2'] = derived_var(
                  vid=varid+'_2', inputs=in2, func=myfunc)

               # This code would be for when ft2 is obs data
               #            print 'This is assuming FT2 is observation data'
               #            if varid == 'TOTRUNOFF':
               #               v='RUNOFF' ### Obs set names it such
               #            else:
               #               v='PREC'
               #            self.reduced_variables[v+'_2'] = reduced_variable(
               #               variableid = v, filetable=filetable2, reduced_var_id = v+'_2',
               #               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
               #
               #            self.single_plotspecs[varid+'_2'] = plotspec(vid=varid+'_2',
               #               zvars=[varid+'_2'], zfunc=(lambda z:z),
               #               plottype = self.plottype)
               #            self.single_plotspecs[varid+'_3'] = plotspec(vid=varid+'_3',
               #               zvars=[varid+'_1', v+'_2'], zfunc=aminusb,
               #               plottype = self.plottype)

         # Now some derived variables that are sums over a level dimension
         if varid == 'TOTSOILICE' or varid=='TOTSOILLIQ':
            self.composite_plotspecs[self.plotall_id] = []
            region = defines.all_regions['Global']
            if varid == 'TOTSOILICE':
               vname = 'SOILICE'
            else:
               vname = 'SOILLIQ'
            self.reduced_variables[varid+'_1'] = reduced_variable(
               variableid = vname, filetable=filetable1, reduced_var_id=varid+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))

            if filetable2 != None:
               self.reduced_variables[varid+'_2'] = reduced_variable(
                  variableid = vname, filetable=filetable2, reduced_var_id=varid+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))

         # set up the plots
         self.single_plotspecs = {
            self.plot1_id: plotspec(
               vid=varid+'_1',
               zvars = [varid+'_1'], zfunc=(lambda z: z),
               plottype = self.plottype) } 
         self.composite_plotspecs[self.plotall_id] = [self.plot1_id]

         if filetable2 != None:
            self.single_plotspecs[self.plot2_id] = plotspec(
               vid=varid+'_2',
               zvars = [varid+'_2'], zfunc=(lambda z: z),
               plottype = self.plottype)
            self.single_plotspecs[self.plot3_id] = plotspec(
               vid=varid+'_1-'+varid+'_2',
               zvars = [varid+'_1', varid+'_2'], zfunc=aminusb,
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(self.plot2_id)
            self.composite_plotspecs[self.plotall_id].append(self.plot3_id)
   
      self.computation_planned = True

   def _results(self,newgrid=0):
      results = plot_spec._results(self,newgrid)
      #print 'results: ', results
      if results is None: return None
      return self.plotspec_values[self.plotall_id]
         

###############################################################################
###############################################################################
### Set 2 - Horizontal contour plots of DJF, MAM, JJA, SON, and ANN means   ###
###                                                                         ###
### This set can take up to 2 datasets and 1 obs set.                       ###
### In that case, 8 graphs should be drawn:                                 ###
###   set1, set2, obs1, set1-obs, set2-obs, set1-set2, T-tests              ###
### If there is only 1 dataset and 1 obs set, 3 graphs are drawn.           ###
###   set1, obs, set1-obs                                                   ###
###############################################################################
###############################################################################

class lmwg_plot_set2(lmwg_plot_spec):
   varlist = []
   name = '2 - Horizontal contour plots of DJF, MAM, JJA, SON, and ANN means'
   _derived_varnames = ['EVAPFRAC', 'PREC', 'TOTRUNOFF', 'LHEAT', 'P-E', 'ASA', 'VBSA', 'NBSA', 'VWSA', 'NWSA', 'RNET']
   _level_vars = ['TLAKE', 'SOILLIQ', 'SOILICE', 'H2OSOI', 'TSOI']
   _level_varnames = [x+y for y in ['(1)', '(5)', '(10)'] for x in _level_vars]
   def __init__( self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      """filetable1, filetable2 should be filetables for two datasets for now. Need to figure
      out obs data stuff for lmwg at some point
      varid is a string identifying the variable to be plotted, e.g. 'TREFHT'.
      seasonid is a string such as 'DJF'."""
      plot_spec.__init__(self,seasonid)
      self.plottype = 'Isofill'
      if self._seasonid == 'ANN':
         self.season = cdutil.times.Seasons('JFMAMJJASOND')
      else:
         self.season = cdutil.times.Seasons(self._seasonid)

      self._var_baseid = '_'.join([varid,'set2'])   # e.g. TREFHT_set2
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid+'_'+seasonid
      if(filetable2 != None):
         self.plot2_id = ft2id+'_'+varid+'_'+seasonid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid+'_'+seasonid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid+'_'+seasonid
      else:
         self.plotall_id = filetable1._strid+'_'+varid+'_'+seasonid

      if not self.computation_planned:
         self.plan_computation( filetable1, filetable2, varid, seasonid, region, aux )

   @staticmethod
   def _list_variables( filetable1, filetable2=None ):
      filevars = lmwg_plot_set2._all_variables( filetable1, filetable2 )
      allvars = filevars
      listvars = allvars.keys()
      listvars.sort()
      return listvars

   @staticmethod
   def _all_variables( filetable1, filetable2=None ):
      allvars = lmwg_plot_spec.package._all_variables( filetable1, filetable2, "lmwg_plot_spec" )

      ### TODO: Fix variable list based on filetable2 after adding derived/level vars
      for dv in lmwg_plot_set2._derived_varnames:
         allvars[dv] = basic_plot_variable
         if filetable2 != None:
            if dv not in filetable2.list_variables():
               del allvars[dv]

      for dv in lmwg_plot_set2._level_varnames:
         allvars[dv] = basic_plot_variable
         if filetable2 != None:
            if dv not in filetable2.list_variables():
               del allvars[dv]

      # Only the 1/5/10 levels are in the varlist, so remove the levelvars
      # (regardless of filetable2 status, this shouldn't be there
      for dv in lmwg_plot_set2._level_vars:
         if dv in allvars:
            del allvars[dv]
      return allvars

   # This seems like variables should be a dictionary... Varname, components, operation, units, etc
   def plan_computation( self, filetable1, filetable2, varid, seasonid, region=None, aux=None):
#      if filetable2 != None:
#         print 'SET 2 ASSUMES SECOND DATASET IS OBSERVATION FOR NOW'
      self.reduced_variables = {}
      self.derived_variables = {}
      self.single_plotspecs = None
      self.composite_plotspecs = None
      if varid not in lmwg_plot_set2._derived_varnames and varid not in lmwg_plot_set2._level_varnames:
          self.reduced_variables[varid+'_1'] = reduced_variable(variableid = varid, 
             filetable=filetable1, 
             reduced_var_id=varid+'_1',
             reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))

      # The simple, linear derived variables
      if varid == 'PREC' or varid == 'TOTRUNOFF' or varid == 'LHEAT':
         self.composite_plotspecs = {}
         if varid == 'PREC':
            red_vars = ['RAIN', 'SNOW']
            myfunc = aplusb
         elif varid == 'TOTRUNOFF':
            red_vars = ['QOVER', 'QDRAI', 'QRGWL']
            myfunc = sum3
         # LHEAT is model or model vs model only
         elif varid == 'LHEAT':
            red_vars = ['FCTR', 'FCEV', 'FGEV']
            myfunc = sum3

         in1 = [x+'_1' for x in red_vars]
         in2 = [x+'_2' for x in red_vars]
         for v in red_vars:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id = v+'_1',
               reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
            if filetable2 != None and varid is 'LHEAT':
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id = v+'_2',
                  reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))

         self.derived_variables[varid+'_1'] = derived_var(
               vid=varid+'_1', inputs=in1, func = myfunc)
         if filetable2 != None and varid is 'LHEAT':
            self.derived_variables[varid+'_2'] = derived_var(
                  vid=varid+'_2', inputs=in2, func = myfunc)

         self.single_plotspecs[varid+'_1'] = plotspec(
            vid = varid+'_1',
            zvars = [varid+'_1'], zfunc = (lambda z: z),
            plottype = self.plottype)

         self.composite_plotspecs[self.plotall_id] = [varid+'_1']

         if filetable2 != None and varid is 'LHEAT':
            self.single_plotspecs[varid+'_2'] = plotspec(
               vid = varid+'_2',
               zvars = [varid+'_2'], zfunc = (lambda z: z),
               plottype = self.plottype)
            self.single_plotspecs[varid+'_3'] = plotspec(
               vid=varid+'_3',
               zvars = [varid+'_1', varid+'_2'], zfunc=aminusb,
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(varid+'_2')
            self.composite_plotspecs[self.plotall_id].append(varid+'_3')


         if filetable2 != None and (varid is 'PREC' or varid is 'TOTRUNOFF'):
            if 'PREC' in filetable2.list_variables() and varid == 'PREC':
               v = 'PREC'
            if 'PRECIP_LAND' in filetable2.list_variables() and varid == 'PREC':
               v = 'PRECIP_LAND'
            if 'RUNOFF' in filetable2.list_variables() and varid == 'TOTRUNOFF':
               v = 'RUNOFF'
            self.reduced_variables[v+'_2'] = reduced_variable(
               variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
               reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
            self.single_plotspecs[v+'_2'] = plotspec(
               vid=v+'_2', zvars = [v+'_2'], zfunc = (lambda z: z),
               plottype = self.plottype)
            self.single_plotspecs[varid+'_3'] = plotspec(
               vid=varid+'_3', zvars = [varid+'_1', v+'_2'], zfunc = aminusb,
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(v+'_2')
            self.composite_plotspecs[self.plotall_id].append(varid+'_3')

      if varid == 'VBSA' or varid == 'NBSA' or varid == 'VWSA' or varid == 'NWSA' or varid == 'ASA':
         self.reduced_variables[varid+'_1'] = albedos_redvar(filetable1, 'SEASONAL', self.albedos[varid], season=self.season)
         if filetable2 != None:
            self.reduced_variables[varid+'_2'] = reduced_variable(
               variableid = varid, filetable=filetable2, reduced_var_id = varid+'_2',
               reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
# For comparison with a dataset instead of obs, use this.
#            self.reduced_variables[varid+'_2'] = albedos_redvar(filetable2, 'SEASONAL', self.albedos[varid], season=self.season)

      # These 3 only exist as model vs model (no model vs obs) comparisons, so ft2 is not special cased
      if varid == 'RNET':
         self.reduced_variables['RNET_1'] = rnet_seasonal(filetable1, self.season)
         if filetable2 != None:
            self.reduced_variables['RNET_2'] = rnet_seasonal(filetable2, self.season)

      if varid == 'EVAPFRAC':
         self.reduced_variables['EVAPFRAC_1'] = evapfrac_redvar(filetable1, 'SEASONAL', season=self.season)
         if filetable2 != None:
            self.reduced_variables['EVAPFRAC_2'] = evapfrac_redvar(filetable2, 'SEASONAL', season=self.season)

      if varid == 'P-E':
         self.reduced_variables['P-E_1'] = pminuse_seasonal(filetable1, self.season)
         if filetable2 != None:
            self.reduced_variables['P-E_2'] = pminuse_seasonal(filetable2, self.season)

      if varid in lmwg_plot_set2._level_varnames:
         # split into varname and level. kinda icky but it works.
         # TODO Offer a level drop down in the GUI/command line
         vbase = varid.split('(')[0]
         num = int(varid.split('(')[1].split(')')[0])
         self.reduced_variables[varid+'_1'] = reduced_variable(
            variableid = vbase, filetable=filetable1, reduced_var_id = varid+'_1',
            reduction_function=(lambda x, vid: reduce2latlon_seasonal_level(x, self.season, num, vid)))
         # Only compared vs 2nd dataset
         if filetable2 != None:
            self.reduced_variables[varid+'_2'] = reduced_variable(
               variableid = vbase, filetable=filetable2, reduced_var_id = varid+'_2',
               reduction_function=(lambda x, vid: reduce2latlon_seasonal_level(x, self.season, num, vid)))

         self.composite_plotspecs = {}
         self.single_plotspecs={}
         self.single_plotspecs[self.plot1_id] = plotspec(
            vid=varid+'_1',
            zvars = [varid+'_1'], zfunc = (lambda z:z),
            plottype = self.plottype)
         self.composite_plotspecs[self.plotall_id] = [self.plot1_id]
         if filetable2 != None:
            self.single_plotspecs[self.plot2_id] = plotspec(
               vid=varid+'_2',
               zvars = [varid+'_1'], zfunc = (lambda z:z),
               plottype = self.plottype)
            self.single_plotspecs[self.plot3_id] = plotspec(
               vid=varid+'_3',
               zvars = [varid+'_1', varid+'_2'], zfunc = (lambda z:z),
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(self.plot2_id)
            self.composite_plotspecs[self.plotall_id].append(self.plot3_id)

      if(filetable2 != None):
          if varid not in lmwg_plot_set2._derived_varnames and varid not in lmwg_plot_set2._level_varnames:
             self.reduced_variables[varid+'_2'] = reduced_variable(variableid = varid, 
                filetable=filetable2, 
                reduced_var_id=varid+'_2',
                reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
#          else:
#              self.reduced_variables['RAIN_2'] = reduced_variable(
#                  variableid = 'RAIN',  filetable = filetable2, reduced_var_id = varid+'_2',
#                  reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
#              self.reduced_variables['SNOW_2'] = reduced_variable(
#                  variableid = 'SNOW',  filetable = filetable2, reduced_var_id = varid+'_2',
#                  reduction_function=(lambda x, vid: reduce2latlon_seasonal(x, self.season, vid)))
#              self.derived_variables['PREC_2'] = derived_var(
#                  vid='PREC_2', inputs=['RAIN_2', 'SNOW_2'], func=aplusb)
   
      # level_varnames already did their plots
      if self.single_plotspecs == None:
         self.single_plotspecs = {}
         self.composite_plotspecs = {}
         self.single_plotspecs[self.plot1_id] = plotspec(
            vid = varid+'_1',
            zvars = [varid+'_1'], zfunc = (lambda z: z),
            plottype = self.plottype)

         self.composite_plotspecs[self.plotall_id] = [self.plot1_id]

         if(filetable2 != None):
            self.single_plotspecs[self.plot2_id] = plotspec(
               vid = varid+'_2',
               zvars = [varid+'_2'], zfunc = (lambda z: z),
               plottype = self.plottype)
            self.single_plotspecs[self.plot3_id] = plotspec(
               vid = varid+'_diff',
               zvars = [varid+'_1', varid+'_2'], zfunc = aminusb_2ax,
               plottype = self.plottype)
            self.composite_plotspecs[self.plotall_id].append(self.plot2_id)
            self.composite_plotspecs[self.plotall_id].append(self.plot3_id)

      self.computation_planned = True

   def _results(self,newgrid=0):
      results = plot_spec._results(self,newgrid)
      if results is None: return None
      return self.plotspec_values[self.plotall_id]

###############################################################################
###############################################################################
### Set 3 - Grouped Line plots of monthly climatology: regional air         ###
### temperature, precipitation, runoff, snow depth, radiative fluxes, and   ###
### turbulent fluxes                                                        ###
###############################################################################
###############################################################################
### This should be combined with set6. They share lots of common code.
class lmwg_plot_set3(lmwg_plot_spec):
   name = '3 - Grouped Line plots of monthly climatology: regional air temperature, precipitation, runoff, snow depth, radiative fluxes, and turbulent fluxes'
   def __init__(self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      plot_spec.__init__(self, seasonid)
      self.plottype = 'Yxvsx'

      self._var_baseid = '_'.join([varid, 'set3'])
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid
      if filetable2 is not None:
         self.plot2_id = ft2id+'_'+varid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid
      else:
         self.plot2_id = None
         self.plot3_id = None
         self.plotall_id = None
      if not self.computation_planned:
         self.plan_computation(filetable1, filetable2, varid, seasonid, region, aux)
   @staticmethod
   def _list_variables(filetable1=None, filetable2 = None):
      # conceivably these could be the same names as the composite plot IDs but this is not a problem now.
      # see _results() for what I'm getting at
      varlist = ['Total Precip/Runoff/SnowDepth', 'Radiative Fluxes', 'Turbulent Fluxes', 'Carbon/Nitrogen Fluxes',
                 'Fire Fluxes', 'Energy/Moist Control of Evap', 'Snow vs Obs', 'Albedo vs Obs', 'Hydrology']
      return varlist

   @staticmethod
   # given the list_vars list above, I don't understand why this is here, or why it is listing what it is....
   # but, being consistent with amwg2
   def _all_variables(filetable1=None,filetable2=None):
      vlist = {vn:basic_plot_variable for vn in lmwg_plot_set3._list_variables(filetable1, filetable2) }
      return vlist

   def plan_computation(self, filetable1, filetable2, varid, seasonid, region, aux):
      # This is not scalable, but apparently is the way to do things. Fortunately, we only have 9 variables to deal with
      if 'Albedo' in varid:
         self.composite_plotspecs['Albedo_vs_Obs'] = []

         for v in self.albedos.keys():
            self.reduced_variables[v+'_1'] = albedos_redvar(filetable1, 'TREND', self.albedos[v], region=region, flag='MONTHLY')

         vlist = ['ASA', 'VBSA', 'NBSA', 'VWSA', 'NWSA']
#         vlist = ['ASA', 'VBSA', 'NBSA', 'VWSA', 'NWSA']
         # This assumes FT2 is obs. Needs some way to determine if that is true
         # TODO: ASA is much more complicated than the others.
         if filetable2 != None:
            for v in vlist:
               if v == 'ASA':
                  pass
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceRegion(x, region, vid=vid)))

         for v in vlist:
            self.single_plotspecs[v+'_1'] = plotspec(vid=v+'_1', zvars=[v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               if v == 'ASA':
                  pass
               self.single_plotspecs[v+'_1'].z2vars=[v+'_2']
               self.single_plotspecs[v+'_1'].z2func=(lambda z:z)

            self.composite_plotspecs['Albedo_vs_Obs'].append(v+'_1')

         ### TODO Figure out how to generate Obs ASA
#         if filetable2 == None:
#            self.single_plotspecs['ASA_1'] = plotspec(vid='ASA_1', zvars=['ASA_1'], zfunc=(lambda z:z),
#               plottype = self.plottype)
#            self.composite_plotspecs['Albedo_vs_Obs'].append('ASA_1')
         if filetable2 != None:
            print "NOTE: TODO - NEED TO CALCULATE ASA FROM OBS DATA"

      # No obs, so second DS is models
      # Plots are RNET and PREC and ET? on same graph
      if 'Moist' in varid:
         red_varlist = ['QVEGE', 'QVEGT', 'QSOIL', 'RAIN', 'SNOW']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
         self.reduced_variables['RNET_1'] = rnet_redvar(filetable1, 'TREND', region=region, flag='MONTHLY')
         self.derived_variables['ET_1'] = derived_var(
            vid='ET_1', inputs=['QVEGE_1', 'QVEGT_1', 'QSOIL_1'], func=sum3)
         self.derived_variables['PREC_1'] = derived_var(
            vid='PREC_1', inputs=['RAIN_1', 'SNOW_1'], func=aplusb)
         if filetable2 != None:
            self.reduced_variables['RNET_2'] = rnet_redvar(filetable2, 'TREND', region=region, flag='MONTHLY')
            self.derived_variables['ET_2'] = derived_var(
               vid='ET_2', inputs=['QVEGE_2', 'QVEGT_2', 'QSOIL_2'], func=sum3)
            self.derived_variables['PREC_2'] = derived_var(
               vid='PREC_2', inputs=['RAIN_2', 'SNOW_2'], func=aplusb)

# The NCAR plots do something like this; we don't support z3vars yet though, so making it separate plots
#         self.single_plotspecs['DS_1'] = plotspec(vid='DS_1',
#            zvars=['ET_1'], zfunc=(lambda z:z),
#            z2vars=['PREC_1'], z2func=(lambda z:z),
#            z3vars=['RNET_1'], z3func=(lambda z:z),
#            plottype = self.plottype)
         self.single_plotspecs['ET_1'] = plotspec(vid='ET_1',
            zvars=['ET_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['PREC_1'] = plotspec(vid='PREC_1',
            zvars=['PREC_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['RNET_1'] = plotspec(vid='RNET_1',
            zvars=['RNET_1'], zfunc=(lambda z:z),
            plottype = self.plottype)

         if filetable2 != None:
            self.single_plotspecs['ET_2'] = plotspec(vid='ET_2',
               zvars=['ET_2'], zfunc=(lambda z:z),
               plottype = self.plottype)
            self.single_plotspecs['PREC_2'] = plotspec(vid='PREC_2',
               zvars=['PREC_2'], zfunc=(lambda z:z),
               plottype = self.plottype)
            self.single_plotspecs['RNET_2'] = plotspec(vid='RNET_2',
               zvars=['RNET_2'], zfunc=(lambda z:z),
               plottype = self.plottype)
         self.composite_plotspecs = {
#            'Energy_Moisture' : ['DS_1']
            'Energy_Moisture' : ['ET_1', 'RNET_1', 'PREC_1']
         }
         if filetable2 != None:
            self.composite_plotspecs['Energy_Moisture'].append('ET_2')
            self.composite_plotspecs['Energy_Moisture'].append('PREC_2')
            self.composite_plotspecs['Energy_Moisture'].append('RNET_2')

      # No obs for this, so FT2 should be a 2nd model
      if 'Radiative' in varid:
         self.composite_plotspecs['Radiative_Fluxes'] = []

         red_varlist = ['FSDS', 'FSA', 'FLDS', 'FIRE', 'FIRA']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1', 
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)
               
            self.composite_plotspecs['Radiative_Fluxes'].append(v)

         self.reduced_variables['ASA_1'] =  albedos_redvar(filetable1, 'TREND', ['FSR', 'FSDS'], region=region, flag='MONTHLY')
         self.reduced_variables['RNET_1' ] = rnet_redvar(filetable1, 'TREND', region=region, flag='MONTHLY')
         if filetable2 != None:
            self.reduced_variables['ASA_2'] =  albedos_redvar(filetable2, 'TREND', ['FSR', 'FSDS'], region=region, flag='MONTHLY')
            self.reduced_variables['RNET_2' ] = rnet_redvar(filetable2, 'TREND', region=region, flag='MONTHLY')

         self.single_plotspecs['Albedo'] = plotspec(vid='ASA_1',
            zvars = ['ASA_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['NetRadiation'] = plotspec(vid='RNET_1',
            zvars = ['RNET_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         if filetable2 != None:
            self.single_plotspecs['Albedo'].z2vars = ['ASA_2']
            self.single_plotspecs['Albedo'].z2func = (lambda z:z)
            self.single_plotspecs['NetRadiation'].z2vars = ['RNET_2']
            self.single_plotspecs['NetRadiation'].z2func = (lambda z:z)

         self.composite_plotspecs['Radiative_Fluxes'].append('Albedo')
         self.composite_plotspecs['Radiative_Fluxes'].append('NetRadiation')

      # No obs for this, so FT2 should be a 2nd model
      if 'Turbulent' in varid:
         self.composite_plotspecs['Turbulent_Fluxes'] = []

         red_varlist = ['FSH', 'FCTR', 'FCEV', 'FGEV', 'FGR', 'BTRAN', 'TLAI']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1', 
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)

            self.composite_plotspecs['Turbulent_Fluxes'].append(v)

         sub_varlist = ['FCTR', 'FGEV', 'FCEV']
         for v in sub_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
         ### Can we do these with reduceMonthlyTrendRegion? Needs investigation
         self.derived_variables['LHEAT_1'] = derived_var(
               vid='LHEAT_1', inputs=['FCTR_1', 'FGEV_1', 'FCEV_1'], func=sum3)
         self.reduced_variables['EVAPFRAC_1'] = evapfrac_redvar(filetable1, 'TREND', region=region, flag='MONTHLY')
         self.reduced_variables['RNET_1'] = rnet_redvar(filetable1, 'TREND', region=region, flag='MONTHLY')
         if filetable2 != None:
            self.derived_variables['LHEAT_2'] = derived_var(
               vid='LHEAT_2', inputs=['FCTR_2', 'FGEV_2', 'FCEV_2'], func=sum3)
            self.reduced_variables['EVAPFRAC_2'] = evapfrac_redvar(filetable2, 'TREND', region=region, flag='MONTHLY')
            self.reduced_variables['RNET_2'] = rnet_redvar(filetable2, 'TREND', region=region, flag='MONTHLY')


         self.single_plotspecs['LatentHeat'] = plotspec(vid='LHEAT_1', 
            zvars = ['LHEAT_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['EvaporativeFraction'] = plotspec(vid='EVAPFRAC_1',
            zvars=['EVAPFRAC_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['NetRadiation'] = plotspec(vid='RNET_1',
            zvars=['RNET_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         if filetable2 != None:
            self.single_plotspecs['NetRadiation'].z2vars = ['RNET_2']
            self.single_plotspecs['NetRadiation'].z2func = (lambda z:z)
            self.single_plotspecs['LatentHeat'].z2vars = ['LHEAT_2']
            self.single_plotspecs['LatentHeat'].z2func = (lambda z:z)
            self.single_plotspecs['EvaporativeFraction'].z2vars = ['EVAPFRAC_2']
            self.single_plotspecs['EvaporativeFraction'].z2func = (lambda z:z)

         self.composite_plotspecs['Turbulent_Fluxes'].append('EvaporativeFraction')
         self.composite_plotspecs['Turbulent_Fluxes'].append('LatentHeat')
         self.composite_plotspecs['Turbulent_Fluxes'].append('NetRadiation')

      ### TODO This requires 2 obs sets, so not supported entirely yet.
      if 'Precip' in varid:
         print '********************************************************************************************'
         print '** This requires 2 observation sets to recreate the NCAR plots. That is not supported yet **'
         print '********************************************************************************************'
         red_varlist = ['SNOWDP', 'TSA', 'SNOW', 'RAIN', 'QOVER', 'QDRAI', 'QRGWL']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
            variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
            reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))

         # These are all linaer, so we can take reduced vars and add them together. I think that is the VAR_1 variables
         self.derived_variables = {
            'PREC_1': derived_var(
            vid='PREC_1', inputs=['SNOW_1', 'RAIN_1'], func=aplusb),
            'TOTRUNOFF_1': derived_var(
            vid='TOTRUNOFF_1', inputs=['QOVER_1', 'QDRAI_1', 'QRGWL_1'], func=sum3)
         }
         if filetable2 != None:
            if 'PREC' in filetable2.list_variables():
               self.reduced_variables['PREC_2'] = reduced_variable(
                  varialeid = 'PREC', filetable=filetable2, reduced_var_id='PREC_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if 'PRECIP_LAND' in filetable2.list_variables():
               self.reduced_variables['PREC_2'] = reduced_variable(
                  varialeid = 'PRECIP_LAND', filetable=filetable2, reduced_var_id='PREC_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if 'RUNOFF' in filetable2.list_variables():
               self.reduced_variables['TOTRUNOFF_2'] = reduced_variable(
                  varialeid = 'RUNOFF', filetable=filetable2, reduced_var_id='TOTRUNOFF_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if 'SNOWDP' in filetable2.list_varialbes():
               self.reduced_variables['SNOWDP_2'] = reduced_variable(
                  variableid = 'SNOWDP', filetable=filetable2, reduced_var_id='SNOWDP_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if 'TSA' in filetable2.list_variables():
               self.reduced_variables['TSA_2'] = reduced_variable(
                  variableid = 'TSA', filetable=filetable2, reduced_var_id='TSA_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))


         # Now, define the individual plots.
         self.single_plotspecs = {
            '2mAir_1': plotspec(vid='2mAir_1', 
               zvars=['TSA_1'], zfunc=(lambda z:z),
               #z2vars = obs
               #z3vars = obs2
               plottype = self.plottype),
            'Prec_1': plotspec(vid='Prec_1',
               zvars=['PREC_1'], zfunc=(lambda z:z),
               #z2vars = obs
               #z3vars = obs2
               plottype = self.plottype),
            'Runoff_1': plotspec(vid='Runoff_1',
               zvars=['TOTRUNOFF_1'], zfunc=(lambda z:z),
               #z2vars = obs
               #z3vars = obs2
               plottype = self.plottype),
            'SnowDepth_1': plotspec(vid='SnowDepth_1',
               zvars=['SNOWDP_1'], zfunc=(lambda z:z),
               #z2vars = obs
               #z3vars = obs2
               plottype = self.plottype)
         }
         if filetable2 != None:
            self.single_plotspecs['2mAir_1'].z2vars = ['TSA_2']
            self.single_plotspecs['2mAir_1'].z2func = (lambda z:z)

         self.composite_plotspecs={
            'Total_Precipitation':
               ['2mAir_1', 'Prec_1', 'Runoff_1', 'SnowDepth_1']
         }
      if 'Snow' in varid:
         print '********************************************************************************************'
         print '** This requires 2 observation sets to recreate the NCAR plots. That is not supported yet **'
         print '********************************************************************************************'
         red_varlist = ['SNOWDP', 'FSNO', 'H2OSNO']
         pspec_name = 'Snow_vs_Obs'
         self.composite_plotspecs[pspec_name] = []
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1', 
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)

            if filetable2 != None and v in filetable2.list_variables():
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)

            self.composite_plotspecs[pspec_name].append(v)
            
      # No obs sets for these 3
      if 'Carbon' in varid or 'Fire' in varid or 'Hydrology' in varid:
         if 'Carbon' in varid:
            red_varlist = ['NEE', 'GPP', 'NPP', 'AR', 'HR', 'ER', 'SUPPLEMENT_TO_SMINN', 'SMINN_LEACHED']
            pspec_name = 'Carbon_Nitrogen_Fluxes'
         if 'Fire' in varid:
            red_varlist = ['COL_FIRE_CLOSS', 'COL_FIRE_NLOSS', 'PFT_FIRE_CLOSS', 'PFT_FIRE_NLOSS', 'FIRESEASONL', 'ANN_FAREA_BURNED', 'MEAN_FIRE_PROB']
            pspec_name = 'Fire_Fluxes'
         if 'Hydrology' in varid:
            red_varlist = ['WA', 'WT', 'ZWT', 'QCHARGE','FCOV']
            pspec_name = 'Hydrology'

         self.composite_plotspecs[pspec_name] = []

         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1', 
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)

            self.composite_plotspecs[pspec_name].append(v)


      self.computation_planned = True
      
   def _results(self, newgrid = 0):
      results = plot_spec._results(self, newgrid)
      if results is None:
         print 'No results'
         return None
      psv = self.plotspec_values
      composite_names = ['Total_Precipitation', 'Carbon_Nitrogen_Fluxes', 
            'Fire_Fluxes',  'Hydrology', 'Turbulent_Fluxes', 
            'Radiative_Fluxes', 'Snow_vs_Obs', 'Energy_Moisture', 
            'Albedo_vs_Obs', ]

      for plot in composite_names:
         if plot in psv.keys():
            return self.plotspec_values[plot]


###############################################################################
###############################################################################
### Set 3b - Individual Line plots of monthly climatology: regional air     ###
### temperature, precipitation, runoff, snow depth, radiative fluxes, and   ###
### turbulent fluxes                                                        ###
###                                                                         ###
### This is primarily for things like EA that might want a single plot.     ###
### Plus, it is useful until UVCDAT supports >5 spreadsheet cells at a time ###
###                                                                         ###
### Currently disabled. Uncomment the name variable to re-enabled           ###
###############################################################################
###############################################################################

class lmwg_plot_set3b(lmwg_plot_spec):
   # These are individual line plots based on set 3. 3b is individual plots.
   # These are basically variable reduced to an annual trend line, over a specified region
   # If two filetables are specified, a 2nd graph is produced which is the difference graph. The
   # top graph would plot both models
   ### TODO: For now this is disabled. I think command line utils and backed vis tools will want this to work though.
#   name = '3b - Individual Line plots of monthly climatology: regional air temperature, precipitation, runoff, snow depth, radiative fluxes, and turbulent fluxes'
   _derived_varnames = ['EVAPFRAC', 'PREC', 'TOTRUNOFF', 'LHEAT', 'RNET', 'ASA'] #, 'P-E']
   def __init__(self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      plot_spec.__init__(self, seasonid)
      self.plottype = 'Yxvsx'

      self._var_baseid = '_'.join([varid, 'set3b'])
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid
      if filetable2 is not None:
         self.plot2_id = ft2id+'_'+varid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid
      else:
         self.plot2_id = None
         self.plot3_id = None
         self.plotall_id = None
      if not self.computation_planned:
         self.plan_computation(filetable1, filetable2, varid, seasonid, region, aux)

   @staticmethod
   def _list_variables(filetable1, filetable2 = None):
      allvars = lmwg_plot_set3b._all_variables(filetable1, filetable2)
      listvars = allvars.keys()
      listvars.sort()
      return listvars
   @staticmethod
   def _all_variables(filetable1, filetable2=None):
      allvars = lmwg_plot_spec.package._all_variables(filetable1, filetable2, "lmwg_plot_spec")
      # I guess this is where I need to add derived variables, ie, ones that do not exist in the dataset and need computed
      # and are not simply intermediate steps
      for dv in lmwg_plot_set3b._derived_varnames:
         allvars[dv] = basic_plot_variable
      return allvars

   def plan_computation(self, filetable1, filetable2, varid, seasonid, region, aux=None):
      self.reduced_variables = {}
      self.derived_variables = {}

      if varid not in lmwg_plot_set3b._derived_varnames:
         self.reduced_variables[varid+'_1'] = reduced_variable(variableid = varid,
            filetable=filetable1, reduced_var_id=varid+'_1', 
            reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
         if filetable2 != None:
            self.reduced_variables[varid+'_2'] = reduced_variable(variableid = varid,
               filetable=filetable2, reduced_var_id=varid+'_2',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
      else:
         # These can be reduced ahead of time; their derived variables are linear
         red_vars = ['RAIN', 'SNOW', 'QVEGE', 'QVEGT', 'QSOIL', 'FCTR', 'FCEV', 'FGEV']
         # These are required for nonlinear variables and can't be derived ahead of time. There is some redundancy
         # Could I fix LHEAT maybe? FCTR+FCEV+FGEV=LHEAT. 
         red_der_vars = ['FSA', 'FSDS', 'FCTR', 'FCEV', 'FGEV', 'FSH', 'FIRA']
         for k in red_vars:
            self.reduced_variables[k+'_1'] = reduced_variable(
               variableid = k, filetable=filetable1, reduced_var_id = k+'_1',
               reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[k+'_2'] = reduced_variable(
                  variableid = k, filetable=filetable2, reduced_var_id = k+'_2',
                  reduction_function=(lambda x, vid: reduceMonthlyTrendRegion(x, region, vid)))
         # This set isn't enabled by default, but when/if it is, these dummy functions() need removed
         # and this chunk needs rewritten to be like set 3.
         for k in red_der_vars:
            self.reduced_variables[k+'_A'] = reduced_variable(
               variableid = k, filetable=filetable1, reduced_var_id = k+'_A',
               reduction_function=(lambda x, vid: dummy(x, vid)))
            if filetable2 != None:
               self.reduced_variables[k+'_B'] = reduced_variable(
                  variableid = k, filetable=filetable2, reduced_var_id = k+'_B',
                  reduction_function=(lambda x, vid: dummy(x, vid)))

         self.derived_variables['PREC_1'] = derived_var(
            vid='PREC_1', inputs=['RAIN_1', 'SNOW_1'], func=aplusb) #verify this makes sense....
         self.derived_variables['TOTRUNOFF_1'] = derived_var(
            vid='TOTRUNOFF_1', inputs=['QSOIL_1', 'QVEGE_1', 'QVEGT_1'], func=sum3)
         self.derived_variables['RNET_1'] = derived_var(
            vid='RNET_1', inputs=['FSA_A', 'FIRA_A'], func=aminusb)
         self.derived_variables['EVAPFRAC_1'] = derived_var(
            vid='EVAPFRAC_1', inputs=['FCTR_A', 'FCEV_A', 'FGEV_A', 'FSH_A'], func=evapfrac_special)
         self.derived_variables['ASA_1'] = derived_var(
            vid='ASA_1', inputs=['FSR_A', 'FSDS_A'], func=adivb)
         self.derived_variables['LHEAT_1'] = derived_var(
            vid='LHEAT_1', inputs=['FCTR_1', 'FCEV_1', 'FGEV_1'], func=sum3)
            
      self.single_plotspecs = {
         self.plot1_id: plotspec(
            vid=varid+'_1',
            zvars = [varid+'_1'], zfunc=(lambda y: y),
            plottype = self.plottype) } #,
#            self.plot2_id: plotspec(
#               vid=varid+'_2',
#               zvars = [varid+'_2'], zfunc=(lambda z: z),
#               plottype = self.plottype) }
#            self.plot3_id: plotspec(
#               vid=varid+'_1',
#               zvars = [varid+'_1', varid+'_2'], zfunc=aminusb,
#               plottype = self.plottype) }
#            }
      self.composite_plotspecs = {
#               self.plotall_id: [self.plot1_id, self.plot2_id, self.plot3_id] 
         self.plotall_id: [self.plot1_id]
      }

      self.computation_planned = True

   def _results(self,newgrid=0):
      results = plot_spec._results(self,newgrid)
      if results is None: return None
      return self.plotspec_values[self.plotall_id]
         
         
###############################################################################
###############################################################################
### Set 5 - Tables of annual means                                          ###
### Set 5a - Regional Hydrologic Cycle                                      ###
### Set 5b - Global biogeophysics                                           ###
### Set 5c - Global Carbon/Nitrogen                                         ###
###############################################################################
###############################################################################

class lmwg_plot_set5(lmwg_plot_spec):
   varlist = []
# Temporarily disable since we don't process tables yet.
#   name = '5 - Tables of annual means'
   def __init__( self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      """filetable1, filetable2 should be filetables for two datasets for now. Need to figure
      out obs data stuff for lmwg at some point
      varid is a string identifying the variable to be plotted, e.g. 'TREFHT'.
      seasonid is a string such as 'DJF'."""
      plot_spec.__init__(self,seasonid)
      self.plottype = 'Isofill'
      if self._seasonid == 'ANN':
         self.season = cdutil.times.Seasons('JFMAMJJASOND')
      else:
         self.season = cdutil.times.Seasons(self._seasonid)

      self._var_baseid = '_'.join([varid,'set5'])   # e.g. TREFHT_set5
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid+'_'+seasonid
      if(filetable2 != None):
         self.plot2_id = ft2id+'_'+varid+'_'+seasonid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid+'_'+seasonid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid+'_'+seasonid
      else:
         self.plotall_id = filetable1._strid+'_'+varid+'_'+seasonid

      if not self.computation_planned:
         self.plan_computation( filetable1, filetable2, varid, seasonid, region, aux )

   @staticmethod
   def _list_variables( filetable1, filetable2=None ):
      varlist = ['Regional Hydrologic Cycle - Table', 'Global Biogeophysics - Table', 'Global Carbon/Nitrogen - Table',
                 'Regional Hydrologic Cycle - Difference', 'Global Biogeophysics - Difference', 
                 'Global Carbon/Nitrogen - Difference']
      return varlist

   @staticmethod
   def _all_variables( filetable1, filetable2=None ):
      vlist = {vn:basic_plot_variable for vn in lmwg_plot_set5._list_variables(filetable1, filetable2) }
      return vlist

   def plan_computation( self, filetable1, filetable2, varid, seasonid, region=None, aux=None):
      self.reduced_variables = {}
      self.derived_variables = {}
      if 'Regional' in varid and 'Table' in varid:
         print 'Not implemented yet'
         quit()
         # Basically need to do annual reductions, then for all regions, provide a single number
         # This should probably do the climatology first, then loop over the regions but that will
         # require some special casing.
#         _derived_varnames = ['PREC','QVEGEP', 'TOTRUNOFF']
#         _red_vars = ['FCEV', 'FCTR', 'FGEV', 'RAIN', 'SNOW', 'QOVER', 'QDRAI', 'QRGWL']
#
#         self.reduced_variables['FCEV_1'] = reduced_variable(variableid = 'FCEV',
#            filetable=filetable1, reduced_var_id='FCEV_1',
#            reduction_function=(lambda x, vid: reduceAnnTrendSingle(x, vid=vid)))
#         for r in defines.all_regions.keys():
#         print 'self var vals: ', self.variable_values
#         r = 'Global'
#         inp = ['FCEV_1', r ]
#         self.variable_values['region'] = r
#         self.derived_variables['FCEV_'+r+'_1'] = derived_var(vid='FCEV_'+r+'_1', inputs=inp, func=reduceRegion)

#         for v in _red_vars:
#            self.reduced_variables[v+'_1'] = reduced_variable(variableid = v,
#               filetable=filetable1, reduced_var_id=v+'_1', 
#               reduction_function=(lambda x, vid: reduceAnnTrendSingle(x, vid=vid)))
#            if filetable2 != None:
#               self.reduced_variables[v+'_2'] = reduced_variable(variableid = v,
#                  filetable=filetable2, reduced_var_id=v+'_2', 
#                  reduction_function=(lambda x, vid: reduceAnnTrendSingle(x, region, vid=vid)))
##         self.reduced_variables['QVEGEP_1'] = qvegepTrendSingle(filetable1)
#         self.reduced_variables['PREC_1'] = derived_var(vid='PREC_1', inputs=['RAIN_1', 'SNOW_1'], func=aplusb)
#         self.derived_variables['TOTRUNOFF_1'] = derived_var(vid='TOTRUNOFF_1', inputs=['QOVER_1', 'QDRAI_1',' QRGWL_1'], func=sum3)
#
#         for r in defines.all_regions.keys():
#            for v in _red_vars:
#               vname = v+'_'+r
#               self.reduced_variables[vname+'_1'] = reduced_variable(variableid = v+'_1',
#                  filetable=filetable1, reduced_var_id=vname+'_1',
#                  reduction_function=(lambda x, vid: reduceRegion(x, r, vid=vid)))

         self.computation_planned = True
         return

      if 'Biogeophysics' in varid and 'Table' in varid:
         region = defines.all_regions['Global']
         _derived_varnames = ['PREC', 'RNET', 'LHEAT']
         _red_vars = ['TSA', 'RAIN', 'SNOW', 'SNOWDP', 'FSNO', 'H2OSNO', 'FSH', 'FSDS', 'FSA', 'FLDS', 
                      'FIRE', 'FCTR', 'FCEV', 'FGEV', 'FGR', 'FSM', 'TLAI', 'LAISUN', 'LAISHA', 'QOVER', 
                      'QDRAI', 'QRGWL', 'WA', 'WT', 'ZWT', 'QCHARGE', 'FCOV', 'CO2_PPMV']
         for v in self.albedos.keys():
            self.reduced_variable[v+'_1'] = albedos_redvar(filetable1, 'SINGLE', self.albedos[v], region=region)
            if filetable2 != None:
               self.reduced_variable[v+'_2'] = albedos_redvar(filetable2, 'SINGLE', self.albedos[v], region=region)

         self.reduced_variables['RNET_1'] = rnet_redvar(filetable1, 'SINGLE', region=region)
         # Is this correct, or do these need to do the math in a different order?
         self.derived_variables['PREC_1'] = derived_var(vid='PREC_1', inputs=['RAIN_1', 'SNOW_1'], func=aplusb)
         self.derived_variables['LHEAT_1'] = derived_var(vid='LHEAT_1', inputs=['FCTR_1', 'FGEV_1', 'FCEV_1'], func=sum3)
         if filetable2 != None:
            self.reduced_variables['RNET_2'] = rnet_redvar(filetable2, 'SINGLE', region=region)
            # Is this correct, or do these need to do the math in a different order?
            self.derived_variables['PREC_2'] = derived_var(vid='PREC_2', inputs=['RAIN_2', 'SNOW_2'], func=aplusb)
            self.derived_variables['LHEAT_2'] = derived_var(vid='LHEAT_2', inputs=['FCTR_2', 'FGEV_2', 'FCEV_2'], func=sum3)


      if 'Carbon' in varid and 'Table' in varid:
         region = defines.all_regions['Global']
         _red_vars = ['NEE', 'NEP', 'GPP', 'PSNSUN_TO_CPOOL', 'PSNSHADE_TO_CPOOL', 'NPP', 'AGNPP', 'BGNPP', 
              'MR', 'GR', 'AR', 'LITHR', 'SOMHR', 'HR', 'RR', 'SR', 'ER', 'LEAFC', 'XSMRPOOL', 'SOIL3C', 'SOIL4C', 
              'FROOTC', 'LIVESTEMC', 'DEADSTEMC', 'LIVECROOTC', 'DEADCROOTC', 'CPOOL', 'TOTVEGC', 'CWDC', 'TOTLITC', 
              'TOTSOMC', 'TOTECOSYSC', 'TOTCOLC', 'FPG', 'FPI', 'NDEP_TO_SMINN', 'POTENTIAL_IMMOB', 'ACTUAL_IMMOB', 
              'GROSS_NMIN', 'NET_NMIN', 'NDEPLOY', 'RETRANSN_TO_NPOOL', 'SMINN_TO_NPOOL', 'DENIT', 'SOIL3N', 'SOIL4N', 
              'NFIX_TO_SMINN', 'SUPPLEMENT_TO_SMINN', 'SMINN_LEACHED', 'SMINN', 'RETRANSN', 'COL_CTRUNC', 'PFT_CTRUNC', 
              'COL_NTRUNC', 'PFT_NTRUNC', 'COL_FIRE_CLOSS', 'PFT_FIRE_CLOSS', 'COL_FIRE_NLOSS', 'PFT_FIRE_NLOSS', 
              'FIRESEASONL', 'FIRE_PROB', 'ANN_FAREA_BURNED', 'MEAN_FIRE_PROB', 'CWDC_HR', 'CWDC_LOSS', 'FROOTC_ALLOC', 
              'FROOTC_LOSS', 'LEAFC_ALLOC', 'LEAFC_LOSS', 'LITTERC', 'LITTERC_HR', 'LITTERC_LOSS', 'SOILC', 'SOILC_HR', 
              'SOILC_LOSS', 'WOODC', 'WOODC_ALLOC',  'WOODC_LOSS']

      for v in _red_vars:
         self.reduced_variables[v+'_1'] = reduced_variable(variableid = v,
            filetable=filetable1, reduced_var_id=v+'_1', 
            reduction_function=(lambda x, vid: reduceAnnTrendRegionSingle(x, region, vid=vid)))
         if filetable2 != None:
            self.reduced_variables[v+'_2'] = reduced_variable(variableid = v,
               filetable=filetable2, reduced_var_id=v+'_2', 
               reduction_function=(lambda x, vid: reduceAnnTrendRegionSingle(x, region, vid=vid)))

      
      self.computation_planned = True

   def _results(self,newgrid=0):
      #print 'red var keys:', self.reduced_variables.keys()
      for v in self.reduced_variables.keys():
         value = self.reduced_variables[v].reduce(None)
         self.variable_values[v] = value
      postponed = []
      #print 'derived var keys:', self.derived_variables.keys()
      for v in self.derived_variables.keys():
         value = self.derived_variables[v].derive(self.variable_values)
         if value is None:
            #print 'postponing ', v
            postponed.append(v)
         else:
            self.variable_values[v] = value
      for v in postponed:
         #print 'Working on postponed var', v
         value = self.derived_variables[v].derive(self.variable_values)
         self.variable_values[v] = value
      varvals = self.variable_values
      


###############################################################################
###############################################################################
### Set 6 - Group Line plots of annual trends in regional soil water/ice    ###
### and temperature, runoff, snow water/ice, photosynthesis                 ###
###                                                                         ###
### This should be combined with set3b. They share lots of common code.     ###
###############################################################################
###############################################################################
class lmwg_plot_set6(lmwg_plot_spec):
   varlist = []
   name = '6 - Group Line plots of annual trends in regional soil water/ice and temperature, runoff, snow water/ice, photosynthesis'
   def __init__(self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      plot_spec.__init__(self, seasonid)
      self.plottype = 'Yxvsx'

      self._var_baseid = '_'.join([varid, 'set6'])
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid
      if filetable2 is not None:
         self.plot2_id = ft2id+'_'+varid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid
      else:
         self.plot2_id = None
         self.plot3_id = None
         self.plotall_id = None
      if not self.computation_planned:
         self.plan_computation(filetable1, filetable2, varid, seasonid, region, aux)

   @staticmethod
   def _list_variables(filetable1, filetable2 = None):
      varlist = ['Total_Precip', 'Radiative_Fluxes', 'Turbulent_Fluxes', 'Carbon/Nitrogen_Fluxes',
                 'Fire_Fluxes', 'Soil_Temp', 'SoilLiq_Water', 'SoilIce', 'TotalSoilIce_TotalSoilH2O', 'TotalSnowH2O_TotalSnowIce', 'Hydrology']
      return varlist
   @staticmethod
   def _all_variables(filetable1, filetable2=None):
      vlist = {vn:basic_plot_variable for vn in lmwg_plot_set6._list_variables(filetable1, filetable2) }
      return vlist

   def plan_computation(self, filetable1, filetable2, varid, seasonid, region, aux=None):
      # None of set6 has obs, so ft2 is/should always be a model set

      if varid == 'SoilIce' or varid == 'Soil_Temp' or varid == 'SoilLiq_Water':
         if varid == 'SoilIce':
            vbase = 'SOILICE'
            pname = 'SoilIce'
         elif varid == 'Soil_Temp':
            vbase = 'TSOI'
            pname = 'Soil_Temp'
         else:
            vbase = 'SOILLIQ'
            pname = 'SoilLiq_Water'

         self.composite_plotspecs[pname] = []
         for i in range(0,10):
            vn = vbase+str(i+1)
            self.reduced_variables[vn+'_1'] = reduced_variable(
               variableid = vbase, filetable=filetable1, reduced_var_id=vn+'_1',
               # hackish to get around python scope pass by ref/value issues
               reduction_function=(lambda x, vid, i=i: reduceAnnTrendRegionLevel(x, region, i, vid))) 
            if filetable2 != None:
               self.reduced_variables[vn+'_2'] = reduced_variable(
                  variableid = vbase, filetable=filetable2, reduced_var_id=vn+'_2',
                  reduction_function=(lambda x, vid, i=i: reduceAnnTrendRegionLevel(x, region, i, vid))) 
               
            self.single_plotspecs[vn] = plotspec(vid=vn,
               zvars = [vn+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.single_plotspecs[vn].z2vars = [vn+'_2']
               self.single_plotspecs[vn].z2func = (lambda z:z)

            self.composite_plotspecs[pname].append(vn)
         
      if 'TotalSoil' in varid:
         self.composite_plotspecs['TotalSoilIce_TotalSoilH2O'] = []
         self.reduced_variables['TOTAL_SOIL_ICE_1'] = reduced_variable(
            variableid = 'SOILICE', filetable=filetable1, reduced_var_id='TOTAL_SOIL_ICE_1',
            reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))
         self.reduced_variables['TOTAL_SOIL_LIQ_1'] = reduced_variable(
            variableid = 'SOILLIQ', filetable=filetable1, reduced_var_id='TOTAL_SOIL_LIQ_1',
            reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))
         self.single_plotspecs['TOTAL_SOIL_ICE'] = plotspec(vid='TOTAL_SOIL_ICE_1',
            zvars = ['TOTAL_SOIL_ICE_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['TOTAL_SOIL_LIQ'] = plotspec(vid='TOTAL_SOIL_LIQ_1',
            zvars = ['TOTAL_SOIL_LIQ_1'], zfunc=(lambda z:z),
            plottype = self.plottype)

         if filetable2 != None:
            self.reduced_variables['TOTAL_SOIL_ICE_2'] = reduced_variable(
               variableid = 'SOILICE', filetable=filetable2, reduced_var_id='TOTAL_SOIL_ICE_2',
               reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))
            self.reduced_variables['TOTAL_SOIL_LIQ_2'] = reduced_variable(
               variableid = 'SOILLIQ', filetable=filetable2, reduced_var_id='TOTAL_SOIL_LIQ_2',
               reduction_function=(lambda x, vid: reduceAnnTrendRegionSumLevels(x, region, 1, 10, vid)))
            self.single_plotspecs['TOTAL_SOIL_LIQ'].z2vars = ['TOTAL_SOIL_LIQ_2']
            self.single_plotspecs['TOTAL_SOIL_LIQ'].z2func = (lambda z:z)
            self.single_plotspecs['TOTAL_SOIL_ICE'].z2vars = ['TOTAL_SOIL_ICE_2']
            self.single_plotspecs['TOTAL_SOIL_ICE'].z2func = (lambda z:z)

         self.composite_plotspecs['TotalSoilIce_TotalSoilH2O'].append('TOTAL_SOIL_LIQ')
         self.composite_plotspecs['TotalSoilIce_TotalSoilH2O'].append('TOTAL_SOIL_ICE')

      if 'Turbulent' in varid:
         self.composite_plotspecs['Turbulent_Fluxes'] = []
         red_varlist = ['FSH', 'FCTR', 'FCEV', 'FGEV', 'FGR', 'BTRAN', 'TLAI']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1',
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)

            self.composite_plotspecs['Turbulent_Fluxes'].append(v)
         sub_varlist = ['FCTR', 'FGEV', 'FCEV']
         for v in sub_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))

               ### Can we do these with reduceMonthlyTrendRegion? Needs investigation
         self.derived_variables['LHEAT_1'] = derived_var(
               vid='LHEAT_1', inputs=['FCTR_1', 'FGEV_1', 'FCEV_1'], func=sum3)
         self.reduced_variables['EVAPFRAC_1'] = evapfrac_redvar(filetable1, 'TREND', region=region, flag='ANN')
         self.reduced_variables['RNET_1'] = rnet_redvar(filetable1, 'TREND', region=region, flag='ANN')

         self.single_plotspecs['LatentHeat'] = plotspec(vid='LHEAT_1',
            zvars = ['LHEAT_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['EvaporativeFraction'] = plotspec(vid='EVAPFRAC_1',
            zvars=['EVAPFRAC_1'], zfunc=(lambda z:z),
            plottype = self.plottype)
         self.single_plotspecs['NetRadiation'] = plotspec(vid='RNET_1',
            zvars=['RNET_1'], zfunc=(lambda z:z),
            plottype = self.plottype)

         if filetable2 != None:
            self.derived_variables['LHEAT_2'] = derived_var(
                  vid='LHEAT_2', inputs=['FCTR_2', 'FGEV_2', 'FCEV_2'], func=sum3)
            self.reduced_variables['EVAPFRAC_2'] = evapfrac_redvar(filetable2, 'TREND', region=region, flag='ANN')
            self.reduced_variables['RNET_2'] = rnet_redvar(filetable2, 'TREND', region=region, flag='ANN')
            self.single_plotspecs['LatentHeat'].z2vars = ['LHEAT_2']
            self.single_plotspecs['LatentHeat'].z2func = (lambda z:z)
            self.single_plotspecs['EvaporativeFraction'].z2vars = ['EVAPFRAC_2']
            self.single_plotspecs['EvaporativeFraction'].z2func = (lambda z:z)
            self.single_plotspecs['NetRadiation'].z2vars = ['RNET_2']
            self.single_plotspecs['NetRadiation'].z2func = (lambda z:z)
   
         self.composite_plotspecs['Turbulent_Fluxes'].append('EvaporativeFraction')
         self.composite_plotspecs['Turbulent_Fluxes'].append('LatentHeat')
         self.composite_plotspecs['Turbulent_Fluxes'].append('NetRadiation')

      if 'Precip' in varid:
         self.composite_plotspecs['Total_Precipitation'] = []
         red_varlist=['SNOWDP', 'TSA', 'RAIN', 'SNOW', 'QOVER', 'QDRAI', 'QRGWL']
         plotnames = ['TSA', 'PREC', 'TOTRUNOFF', 'SNOWDP']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
         self.derived_variables['PREC_1'] = derived_var(vid='PREC_1', inputs=['SNOW_1', 'RAIN_1'], func=aplusb)
         self.derived_variables['TOTRUNOFF_1'] = derived_var(vid='TOTRUNOFF_1', inputs=['QOVER_1', 'QDRAI_1', 'QRGWL_1'], func=sum3)
         if filetable2 != None:
            self.derived_variables['PREC_2'] = derived_var(vid='PREC_2', inputs=['SNOW_2', 'RAIN_2'], func=aplusb)
            self.derived_variables['TOTRUNOFF_2'] = derived_var(vid='TOTRUNOFF_2', inputs=['QOVER_2', 'QDRAI_2', 'QRGWL_2'], func=sum3)

         for p in plotnames:
            self.single_plotspecs[p] = plotspec(vid=p+'_1', zvars=[p+'_1'], zfunc=(lambda z:z), plottype = self.plottype)
            self.composite_plotspecs['Total_Precipitation'].append(p)
            if filetable2 != None:
               self.single_plotspecs[p].z2vars = [p+'_2']
               self.single_plotspecs[p].z2func = (lambda z:z)

      if 'Radiative' in varid:
         self.composite_plotspecs['Radiative_Fluxes'] = []
         red_varlist = ['FSDS', 'FSA', 'FLDS', 'FIRE', 'FIRA']
         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1',
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)

            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)
               
            self.composite_plotspecs['Radiative_Fluxes'].append(v+'_1')

         self.reduced_variables['ASA_1'] =  albedos_redvar(filetable1, 'TREND', ['FSR', 'FSDS'], region=region, flag='ANN')
         self.reduced_variables['RNET_1' ] = rnet_redvar(filetable1, 'TREND', region=region, flag='ANN')
         if filetable2 != None:
            self.reduced_variables['ASA_2'] =  albedos_redvar(filetable2, 'TREND', ['FSR', 'FSDS'], region=region, flag='ANN')
            self.reduced_variables['RNET_2' ] = rnet_redvar(filetable2, 'TREND', region=region, flag='ANN')

         self.single_plotspecs['Albedo'] = plotspec(vid='ASA_1', zvars = ['ASA_1'], zfunc=(lambda z:z), plottype = self.plottype)
         self.single_plotspecs['NetRadiation'] = plotspec(vid='RNET_1', zvars = ['RNET_1'], zfunc=(lambda z:z), plottype = self.plottype)
         if filetable2 != None:
            self.single_plotspecs['Albedo'].z2vars = ['ASA_2']
            self.single_plotspecs['Albedo'].z2func = (lambda z:z)
            self.single_plotspecs['NetRadiation'].z2vars = ['RNET_2']
            self.single_plotspecs['NetRadiation'].z2func = (lambda z:z)

         self.composite_plotspecs['Radiative_Fluxes'].append('Albedo_1')
         self.composite_plotspecs['Radiative_Fluxes'].append('NetRadiation_1')
         
      if 'Carbon' in varid or 'Fire' in varid or 'Hydrology' in varid or 'TotalSnow' in varid:
         if 'TotalSnow' in varid:
            red_varlist = ['SOILICE', 'SOILLIQ']
            pspec_name = 'TotalSnowH2O_TotalSnowIce'
         if 'Carbon' in varid:
            red_varlist = ['NEE', 'GPP', 'NPP', 'AR', 'HR', 'ER', 'SUPPLEMENT_TO_SMINN', 'SMINN_LEACHED']
            pspec_name = 'Carbon_Nitrogen_Fluxes'
         if 'Fire' in varid:
            red_varlist = ['COL_FIRE_CLOSS', 'COL_FIRE_NLOSS', 'PFT_FIRE_CLOSS', 'PFT_FIRE_NLOSS', 'FIRESEASONL', 'ANN_FAREA_BURNED', 'MEAN_FIRE_PROB']
            pspec_name = 'Fire_Fluxes'
         if 'Hydrology' in varid:
            red_varlist = ['WA', 'WT', 'ZWT', 'QCHARGE','FCOV']
            pspec_name = 'Hydrology'

         self.composite_plotspecs[pspec_name] = []

         for v in red_varlist:
            self.reduced_variables[v+'_1'] = reduced_variable(
               variableid = v, filetable=filetable1, reduced_var_id=v+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            self.single_plotspecs[v] = plotspec(vid=v+'_1', 
               zvars = [v+'_1'], zfunc=(lambda z:z),
               plottype = self.plottype)
            if filetable2 != None:
               self.reduced_variables[v+'_2'] = reduced_variable(
                  variableid = v, filetable=filetable2, reduced_var_id=v+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
               self.single_plotspecs[v].z2vars = [v+'_2']
               self.single_plotspecs[v].z2func = (lambda z:z)
               
            self.composite_plotspecs[pspec_name].append(v)


      self.computation_planned = True


   def _results(self,newgrid=0):
      results = plot_spec._results(self,newgrid)
      if results is None: 
         print 'No results to plot. This is probably bad'
         return None
      psv = self.plotspec_values

      composite_names = ['Total_Precipitation','Hydrology', 'Carbon_Nitrogen_Fluxes', 
         'Fire_Fluxes', 'Radiative_Fluxes', 'Turbulent_Fluxes', 'SoilIce', 
         'SoilLiq_Water', 'Soil_Temp', 'TotalSnowH2O_TotalSnowIce', 'TotalSoilIce_TotalSoilH2O']

      for plot in composite_names:
         if plot in psv.keys():
            return self.plotspec_values[plot]


###############################################################################
###############################################################################
### Set 6b - Individual Line plots of annual trends in regional soil        ###
### water/ice and temperature, runoff, snow water/ice, photosynthesis       ###
###                                                                         ###
### This is primarily for things like EA that might want a single plot.     ###
### Plus, it is useful until UVCDAT supports >5 spreadsheet cells at a time ###
###                                                                         ###
### Currently disabled. Uncomment the name variable to re-enabled           ###
###############################################################################
###############################################################################

class lmwg_plot_set6b(lmwg_plot_spec):
   varlist = []
#   name = '6b - Individual Line plots of annual trends in regional soil water/ice and temperature, runoff, snow water/ice, photosynthesis'
   _derived_varnames = ['LHEAT', 'PREC', 'TOTRUNOFF', 'ALBEDO', 'RNET']
   def __init__(self, filetable1, filetable2, varid, seasonid=None, region=None, aux=None):
      plot_spec.__init__(self, seasonid)
      self.plottype = 'Yxvsx'

      self._var_baseid = '_'.join([varid, 'set6b'])
      ft1id,ft2id = filetable_ids(filetable1,filetable2)
      self.plot1_id = ft1id+'_'+varid
      if filetable2 is not None:
         self.plot2_id = ft2id+'_'+varid
         self.plot3_id = ft1id+' - '+ft2id+'_'+varid
         self.plotall_id = ft1id+'_'+ft2id+'_'+varid
      else:
         self.plot2_id = None
         self.plot3_id = None
         self.plotall_id = None
      if not self.computation_planned:
         self.plan_computation(filetable1, filetable2, varid, seasonid, region, aux)

   @staticmethod
   def _list_variables(filetable1, filetable2 = None):
      allvars = lmwg_plot_set6b._all_variables(filetable1, filetable2)
      listvars = allvars.keys()
      listvars.sort()
      return listvars
   @staticmethod
   def _all_variables(filetable1, filetable2=None):
      allvars = lmwg_plot_spec.package._all_variables(filetable1, filetable2, "lmwg_plot_spec")
      for dv in lmwg_plot_set6b._derived_varnames:
         allvars[dv] = basic_plot_variable
      return allvars

   def plan_computation(self, filetable1, filetable2, varid, seasonid, region, aux=None):
      self.reduced_variables = {}
      self.derived_variables = {}

      if varid not in lmwg_plot_set6b._derived_varnames:
         self.reduced_variables[varid+'_1'] = reduced_variable(
               variableid = varid, filetable=filetable1, reduced_var_id=varid+'_1',
               reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
         if filetable2 != None:
            self.reduced_variables[varid+'_2'] = reduced_variable(
                  variableid = varid, filetable=filetable2, reduced_var_id=varid+'_2',
                  reduction_function=(lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
      else:
         red_vars = ['RAIN', 'PREC', 'QSOIL', 'QVEGE', 'QVEGT', 'FCTR', 'FCEV', 'FGEV', 'FSR', 'FSDS', 'FIRA', 'FSA']
         red_der_vars = ['FSR', 'FSDS', 'FSA', 'FIRA']
         for k in red_vars:
            self.reduced_variables[k+'_1'] = reduced_variable(
               variableid = k, filetable = filetable1, reduced_var_id = k+'_1',
               reduction_function = (lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
            if filetable2 != None:
               self.reduced_variables[k+'_2'] = reduced_variable(
                  variableid = k, filetable = filetable2, reduced_var_id = k+'_2',
                  reduction_function = (lambda x, vid: reduceAnnTrendRegion(x, region, vid)))
         # This set isn't enabled by default, but when/if it is, these dummy functions() need removed
         # and this chunk needs rewritten to be like set 3.
         for k in red_der_vars:
            self.reduced_variables[k+'_A'] = reduced_variable(
               variableid = k, filetable = filetable1, reduced_var_id = k+'_A',
               reduction_function = (lambda x, vid: dummy(x, vid)))
            if filetable2 != None:
               self.reduced_variables[k+'_B'] = reduced_variable(
                  variableid = k, filetable = filetable2, reduced_var_id = k+'_B',
                  reduction_function = (lambda x, vid: dummy(x, vid)))

         self.derived_variables['PREC_1'] = derived_var(
            vid='PREC_1', inputs=['RAIN_1', 'SNOW_1'], func=aplusb)
         self.derived_variables['TOTRUNOFF_1'] = derived_var(
            vid='TOTRUNOFF_1', inputs=['QSOIL_1', 'QVEGE_1', 'QVEGT_1'], func=sum3)
         self.derived_variables['RNET_1'] = derived_var(
            vid='RNET_1', inputs=['FSA_A', 'FIRA_A'], func=aminusb)
         self.derived_variables['LHEAT_1'] = derived_var(
            vid='LHEAT_1', inputs=['FCTR_1', 'FCEV_1', 'FGEV_1'], func=sum3)
         # AKA ASA?
         self.derived_variables['ALBEDO_1'] = derived_var(
            vid='ALBEDO_1', inputs=['FSR_A', 'FSDS_A'], func=adivb)
         if filetable2 != None:
            self.derived_variables['PREC_2'] = derived_var(
               vid='PREC_2', inputs=['RAIN_2', 'SNOW_2'], func=aplusb)
            self.derived_variables['TOTRUNOFF_2'] = derived_var(
               vid='TOTRUNOFF_2', inputs=['QSOIL_2', 'QVEGE_2', 'QVEGT_2'], func=sum3)
            self.derived_variables['RNET_2'] = derived_var(
               vid='RNET_2', inputs=['FSA_B', 'FIRA_B'], func=aminusb)
            self.derived_variables['LHEAT_2'] = derived_var(
               vid='LHEAT_2', inputs=['FCTR_2', 'FCEV_2', 'FGEV_2'], func=sum3)
            # AKA ASA?
            self.derived_variables['ALBEDO_2'] = derived_var(
               vid='ALBEDO_2', inputs=['FSR_B', 'FSDS_B'], func=adivb)


      self.single_plotspecs = {
         self.plot1_id: plotspec(
            vid=varid+'_1',
            zvars = [varid+'_1'], zfunc=(lambda z: z),
            plottype = self.plottype) } #,
#            self.plot2_id: plotspec(
#               vid=varid+'_2',
#               zvars = [varid+'_2'], zfunc=(lambda z: z),
#               plottype = self.plottype) }
#            self.plot3_id: plotspec(
#               vid=varid+'_1',
#               zvars = [varid+'_1', varid+'_2'], zfunc=aminusb,
#               plottype = self.plottype) }
#            }
      self.composite_plotspecs = {
#               self.plotall_id: [self.plot1_id, self.plot2_id, self.plot3_id] 
         self.plotall_id: [self.plot1_id]
      }

      self.computation_planned = True

   def _results(self,newgrid=0):
      results = plot_spec._results(self,newgrid)
      if results is None: return None
      return self.plotspec_values[self.plotall_id]
         

###############################################################################
###############################################################################
### These are not implemented yet                                           ###
###############################################################################
###############################################################################
class lmwg_plot_set7(lmwg_plot_spec):
#   name = '7 - Line plots, tables, and maps of RTM river flow and discharge to oceans'
    pass

class lmwg_plot_set9(lmwg_plot_spec):
#   name = '9 - Contour plots and statistics for precipitation and temperature. Statistics include DJF, JJA, and ANN biases, and RMSE, correlation and standard deviation of the annual cycle relative to observations'
   _derived_varnames = ['PREC', 'ASA']
   pass

###############################################################################
###############################################################################
### These are marked inactive and won't be implemented                      ###
###############################################################################
###############################################################################

class lmwg_plot_set4(lmwg_plot_spec):
    pass
class lmwg_plot_set8(lmwg_plot_spec):
    pass
