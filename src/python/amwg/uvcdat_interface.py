#!/usr/local/uvcdat/1.3.1/bin/python

# Functions callable from the UV-CDAT GUI.

import hashlib, os, pickle, sys, os
import cdutil.times
from filetable import *
from findfiles import *
from reductions import *
from vertical import *
from plot_data import plotspec, derived_var
from pprint import pprint

def setup_filetable( search_path, cache_path, ftid=None, search_filter=None ):
    """Returns a file table (an index which says where you can find a variable) for files in the
    supplied search path, satisfying the optional filter.  It will be useful if you provide a name
    for the file table, the string ftid.  For example, this may appear in names of variables to be
    plotted.  This function will cache the file table and
    use it if possible.  If the cache be stale, call clear_filetable()."""
    search_path = os.path.abspath(search_path)
    cache_path = os.path.abspath(cache_path)
    if ftid is None:
        ftid = os.path.basename(search_path)
    csum = hashlib.md5(search_path+cache_path).hexdigest()  #later will have to add search_filter
    cachefilename = csum+'.cache'
    cachefile=os.path.normpath( cache_path+'/'+cachefilename )

    if os.path.isfile(cachefile):
        f = open(cachefile,'rb')
        filetable = pickle.load(f)
        f.close()
    else:
        datafiles = treeof_datafiles( search_path, search_filter )
        filetable = basic_filetable( datafiles, ftid )
        f = open(cachefile,'wb')
        pickle.dump( filetable, f )
        f.close()
    return filetable

def clear_filetable( search_path, cache_path, search_filter=None ):
    """Deletes (clears) the cached file table created by the corresponding call of setup_filetable"""
    search_path = os.path.abspath(search_path)
    cache_path = os.path.abspath(cache_path)
    csum = hashlib.md5(search_path+cache_path).hexdigest()  #later will have to add search_filter
    cachefilename = csum+'.cache'
    cachefile=os.path.normpath( cache_path+'/'+cachefilename )

    if os.path.isfile(cache_path):
        os.remove(cache_path)

class uvc_plotspec():
    """This is a simplified version of the plotspec class, intended for the UV-CDAT GUI.
    Once it stabilizes, I may replace the plotspec class with this one.
    The plots will be of the type specified by presentation.  The data will be the
    variable(s) supplied, and their axes.  Optionally one may specify a list of labels
    for the variables, and a title for the whole plot."""
    # re prsentation (plottype): Yvsx is a line plot, for Y=Y(X).  It can have one or several lines.
    # Isofill is a contour plot.  To make it polar, set projection=polar.  I'll
    # probably communicate that by passing a name "Isofill_polar".
    def __init__( self, vars, presentation, labels=[], title='' ):
        self.presentation = presentation
        self.vars = vars
        self.labels = labels
        self.title = title
    def __repr__(self):
        return ("uvc_plotspec %s: %s\n" % (self.presentation,self.title))

def get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """returns a list of uvc_plotspec objects to be plotted.  The plot_set is a string from
    1,2,3,4,4a,5,...,16.  Usually filetable1 indexes model data and filetable2 obs data,  but
    anything generated by setup_filetable() is ok.  The variable is a string - it can be a data
    variable from the indexed data sets, or a derived variable.  The season is a 3-letter code,
    e.g. 'DJF','ANN','MAR'."""
    if plot_set=='3':
        return plot_set3( filetable1, filetable2, variable, season )
    else:
        print "ERROR, plot set",plot_set," not implemented yet!"
        return None

class one_line_plot( plotspec ):
    def __init__( self, yvar, xvar=None ):
        # xvar, yvar should be the actual x,y of the plot.
        # xvar, yvar should already have been reduced to 1-D variables.
        # Normally y=y(x), x is the axis of y.
        if xvar is None:
            xvar = yvar.getAxisList()[0]
        plotspec.__init__( self, xvars=[xvar], yvars=[yvar],
                           vid = yvar.id+" line plot", plottype='Yvsx' )

class two_line_plot( plotspec ):
    def __init__( self, y1var, y2var, x1var=None, x2var=None ):
        """x?var, y?var should be the actual x,y of the plots.
        x?var, y?var should already have been reduced to 1-D variables.
        Normally y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self, y1vars=[y1var], y2vars=[y2var],
                           vid = y1var.variableid+y2var.variableid+" line plot", plottype='Yvsx' )

class one_line_diff_plot( plotspec ):
    def __init__( self, y1var, y2var, vid ):
        """y?var should be the actual y of the plots.
        y?var should already have been reduced to 1-D variables.
        y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self,
            xvars=[y1var,y2var], xfunc = latvar_min,
            yvars=[y1var,y2var],
            yfunc=aminusb_1ax,   # aminusb_1ax(y1,y2)=y1-y2; each y has 1 axis, use min axis
            vid=vid,
            plottype='Yvsx' )

class contour_plot( plotspec ):
    def __init__( self, zvar, xvar=None, yvar=None, ya1var=None,
                  xfunc=None, yfunc=None, ya1func=None ):
        """ zvar is the variable to be plotted.  xvar,yvar are the x,y of the plot,
        normally the axes of zvar.  If you don't specify, a x=lon,y=lat plot will be preferred.
        xvar, yvar, zvar should already have been reduced; x,y to 1-D and z to 2-D."""
        if xvar is None:
            xvar = zvar
        if yvar is None:
            yvar = zvar
        if ya1var is None:
            ya1var = zvar
        if xfunc==None: xfunc=lonvar
        if yfunc==None: yfunc=latvar
        vid = ''
        if hasattr(zvar,'vid'): vid = zvar.vid
        if hasattr(zvar,'id'): vid = zvar.id
        plotspec.__init__(
            self, vid+'_contour', xvars=[xvar], xfunc=xfunc,
            yvars=[yvar], yfunc=yfunc, ya1vars=[ya1var], ya1func=ya1func,
            zvars=[zvar], plottype='Isofill' )

class contour_diff_plot( plotspec ):
    def __init__( self, z1var, z2var, plotid, x1var=None, x2var=None, y1var=None, y2var=None,
                   ya1var=None,  ya2var=None, xfunc=None, yfunc=None, ya1func=None ):
        """We will plot the difference of the two z variables, z1var-z2var.
        See the notes on contour_plot"""
        if x1var is None:
            x1var = z1var
        if y1var is None:
            y1var = z1var
        if ya1var is None:
            ya1var = z1var
        if x2var is None:
            x2var = z2var
        if y2var is None:
            y2var = z2var
        if ya2var is None:
            ya2var = z2var
        if xfunc==None: xfunc=lonvar_min
        if yfunc==None: yfunc=latvar_min
        plotspec.__init__(
            self, plotid, xvars=[x1var,x2var], xfunc=xfunc,
            yvars=[y1var,y2var], yfunc=yfunc, ya1vars=[ya1var,ya2var], ya1func=ya1func,
            zvars=[z1var,z2var], zfunc=aminusb_ax2, plottype='Isofill' )

class plot_set():
    def __init__(self):
        self.reduced_variables = {}
        self.derived_variables = {}
        self.variable_values = {}
    def results(self):
        for v in self.reduced_variables.keys():
            self.variable_values[v] = self.reduced_variables[v].reduce()
        for v in self.derived_variables.keys():
            self.variable_values[v] = self.derived_variables[v].derive(self.variable_values)
    
class plot_set3(plot_set):
    """represents one plot from AMWG Diagnostics Plot Set 3.
    Each such plot is a pair of plots: a 2-line plot comparing model with obs, and
    a 1-line plot of the model-obs difference.  A plot's x-axis is latitude, and
    its y-axis is the specified variable.  The data presented is a climatological mean - i.e.,
    time-averaged with times restricted to the specified season, DJF, JJA, or ANN."""
    # N.B. In plot_data.py, the plotspec contained keys identifying reduced variables.
    # Here, the plotspec contains the variables themselves.
    def __init__( self, filetable1, filetable2, varid, seasonid ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string, e.g. 'TREFHT'.  Seasonid is a string, e.g. 'DJF'."""
        season = cdutil.times.Seasons(seasonid)
        self._var_baseid = '_'.join([varid,seasonid,'set3'])   # e.g. CLT_DJF_set3
        y1var = reduced_variable(
            variableid=varid,
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,season,vid=vid)) )
        y2var = reduced_variable(
            variableid=varid,
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,season,vid=vid)) )
        self.plot_a = two_line_plot( y1var, y2var )
        vid = '_'.join([self._var_baseid,filetable1._id,filetable2._id,'diff'])
        # ... e.g. CLT_DJF_set3_CAM456_NCEP_diff
        self.plot_b = one_line_diff_plot( y1var, y2var, vid )
    def results(self):
        # At the moment this is very specific to plot set 3.  Maybe later I'll use a
        # more general method, to something like what's in plot_data.py, maybe not.
        # later this may be something more specific to the needs of the UV-CDAT GUI
        y1var = self.plot_a.y1vars[0]
        y2var = self.plot_a.y2vars[0]
        y1val = y1var.reduce()
        if y1val is None: return None
        y1unam = y1var._filetable._id  # unique part of name for y1, e.g. CAM456
        y1val.id = '_'.join([self._var_baseid,y1unam])  # e.g. CLT_DJF_set3_CAM456
        y2val = y2var.reduce()
        if y2val is None: return None
        y2unam = y2var._filetable._id  # unique part of name for y2, e.g. NCEP
        y2val.id = '_'.join([self._var_baseid,y2unam])  # e.g. CLT_DJF_set3_NCEP
        ydiffval = apply( self.plot_b.yfunc, [y1val,y2val] )
        ydiffval.id = '_'.join([self._var_baseid, y1var._filetable._id, y2var._filetable._id,
                                'diff'])
        # ... e.g. CLT_DJF_set3_CAM456_NCEP_diff
        plot_a_val = uvc_plotspec(
            [y1val,y2val],'Yvsx', labels=[y1unam,y2unam],
            title=' '.join([self._var_baseid,y1unam,'and',y2unam]) )
        plot_b_val = uvc_plotspec(
            [ydiffval],'Yvsx', labels=['difference'],
            title=' '.join([self._var_baseid,y1unam,'-',y2unam]))
        return [ plot_a_val, plot_b_val ]

class plot_set4(plot_set):
    """represents one plot from AMWG Diagnostics Plot Set 4.
    Each such plot is a set of three contour plots: one each for model output, observations, and
    the difference between the two.  A plot's x-axis is latitude and its y-axis is the level,
    measured as pressure.  The model and obs plots should have contours at the same values of
    their variable.  The data presented is a climatological mean - i.e.,
    time-averaged with times restricted to the specified season, DJF, JJA, or ANN."""
    # N.B. In plot_data.py, the plotspec contained keys identifying reduced variables.
    # Here, the plotspec contains the variables themselves.
    def __init__( self, filetable1, filetable2, varid, seasonid ):
        """filetable1, filetable2 should be filetables for model and obs.
        varid is a string, e.g. 'TREFHT'.  Seasonid is a string, e.g. 'DJF'.
        At the moment we assume that data from filetable1 has CAM hybrid levels,
        and data from filetable2 has pressure levels."""
        plot_set.__init__(self)
        season = cdutil.times.Seasons(seasonid)
        self._var_baseid = '_'.join([varid,seasonid,'set3'])   # e.g. CLT_DJF_set3
        rv1 = reduced_variable(
            variableid=varid,
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2levlat_seasonal(x,season,vid=vid)) )
        self.reduced_variables[varid+'_1'] = rv1
        rv2 = reduced_variable(
            variableid=varid,
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2levlat_seasonal(x,season,vid=vid)) )
        self.reduced_variables[varid+'_2'] = rv2
        hyam = reduced_variable(      # hyam=hyam(lev)
            variableid='hyam', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) )
        self.reduced_variables['hyam'] = hyam
        hybm = reduced_variable(      # hyab=hyab(lev)
            variableid='hybm', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) )
        self.reduced_variables['hybm'] = hybm
        ps = reduced_variable(
            variableid='PS', filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,season,vid=vid)) )
        self.reduced_variables['ps'] = ps
        vid1='_'.join([varid,seasonid,'levlat'])
        vv1 = derived_var(
            vid=vid1, inputs=[varid+'_1', 'hyam', 'hybm', 'ps', varid+'_2'], func=verticalize )
        vv1._filetable = filetable1  # so later we can extract the filetable id for labels
        self.derived_variables[vid1] = vv1
        vv2 = rv2
        vv2._vid = varid+'_2'        # for lookup conventience in results() method
        vv2._filetable = filetable2  # so later we can extract the filetable id for labels

        self.plot_a = contour_plot( vv1, xfunc=latvar, yfunc=levvar, ya1func=heightvar )
        self.plot_b = contour_plot( vv2, xfunc=latvar, yfunc=levvar, ya1func=heightvar )
        vid = '_'.join([self._var_baseid,filetable1._id,filetable2._id,'diff'])
        # ... e.g. CLT_DJF_set4_CAM456_NCEP_diff
        self.plot_c = contour_diff_plot( vv1, vv2, vid, xfunc=latvar_min, yfunc=levvar_min,
                                         ya1func=(lambda y1,y2: heightvar(levvar_min(y1,y2))))
    def results(self):
        # At the moment this is very specific to plot set 4.  Maybe later I'll use a
        # more general method, to something like what's in plot_data.py, maybe not.
        # later this may be something more specific to the needs of the UV-CDAT GUI
        plot_set.results(self)
        zavar = self.plot_a.zvars[0]
        zaval = self.variable_values[ zavar._vid ]
        if zaval is None: return None
        zaunam = zavar._filetable._id  # unique part of name for y1, e.g. CAM456
        zaval.id = '_'.join([self._var_baseid,zaunam])  # e.g. CLT_DJF_set3_CAM456

        zbvar = self.plot_b.zvars[0]
        #zbval = zbvar.reduce()
        zbval = self.variable_values[ zbvar._vid ]
        if zbval is None: return None
        zbunam = zbvar._filetable._id  # unique part of name for y1, e.g. OBS123
        zbval.id = '_'.join([self._var_baseid,zbunam])  # e.g. CLT_DJF_set3_OBS123

        z1var = self.plot_c.zvars[0]
        z2var = self.plot_c.zvars[1]
        z1val = self.variable_values[ z1var._vid ]
        z2val = self.variable_values[ z2var._vid ]
        z1unam = z1var._filetable._id  # unique part of name for y1, e.g. OBS123
        z1val.id = '_'.join([self._var_baseid,z1unam])  # e.g. CLT_DJF_set3_OBS123
        z2unam = z1var._filetable._id  # unique part of name for y1, e.g. OBS123
        z2val.id = '_'.join([self._var_baseid,z2unam])  # e.g. CLT_DJF_set3_OBS123
        zdiffval = apply( self.plot_c.zfunc, [z1val,z2val] )
        if zdiffval is None: return None
        zdiffval.id = '_'.join([self._var_baseid, z1var._filetable._id, z2var._filetable._id,
                                'diff'])
        # ... e.g. CLT_DJF_set3_CAM456_OBS123_diff
        plot_a_val = uvc_plotspec(
            [zaval],'Isofill', labels=[zaunam],
            title= zaunam ),
        plot_b_val = uvc_plotspec(
            [zbval],'Isofill', labels=[zbunam],
            title= zbunam ),
        plot_c_val = uvc_plotspec(
            [zdiffval],'Isofill', labels=['difference'],
            title=' '.join([self._var_baseid,z1unam,'-',z2unam]))
        return ( plot_a_val, plot_b_val, plot_c_val )


# TO DO: reset axes, set 'x' or 'y' attributes, etc., as needed
# C. Doutriaux commeting bellow seems to break import system, should be moved to script directory anyway
if __name__ == '__main__':
   if len( sys.argv ) > 1:
      from findfiles import *
      path1 = sys.argv[1]
      filetable1 = setup_filetable(path1,os.environ['PWD'])
      if len( sys.argv ) > 2:
          path2 = sys.argv[2]
      else:
          path2 = None
      if len(sys.argv)>3 and sys.argv[3].find('filt=')==0:  # need to use getopt to parse args
          filt2 = sys.argv[3]
          filetable2 = setup_filetable(path2,os.environ['PWD'],search_filter=filt2)
      else:
          filetable2 = setup_filetable(path2,os.environ['PWD'])
#      ps3 = plot_set3( filetable1, filetable2, 'TREFHT', 'DJF' )
#      print "ps3=",ps3
#      pprint( ps3.results() )
      ps4 = plot_set4( filetable1, filetable2, 'T', 'DJF' )
      print "ps4=",ps4
      pprint( ps4.results() )
   else:
      print "usage: plot_data.py root"
""" for testing...
else:
    # My usual command-line test is:
    # ./uvcdat_interface.py /export/painter1/cam_output/*.xml ./obs_data/ filt="f_startswith('LEGATES')"
    # ...That's for plot set 3; it has no levels so it's a bad test for plot set 4.  Here's another:
    # ./uvcdat_interface.py /export/painter1/cam_output/*.xml ./obs_data/ filt="f_startswith('NCEP')"
    path1 = '/export/painter1/cam_output/b30.009.cam2.h0.06.xml'
    path2 = '/export/painter1/metrics/src/python/obs_data/'
#    filt2="filt=f_startswith('LEGATES')"
    filt2="filt=f_startswith('NCEP')"
    filetable1 = setup_filetable(path1,os.environ['PWD'])
    filetable2 = setup_filetable(path2,os.environ['PWD'],search_filter=filt2)
#    ps3 = plot_set3( filetable1, filetable2, 'TREFHT', 'DJF' )
#    res3 = ps3.results()
    ps4 = plot_set4( filetable1, filetable2, 'T', 'DJF' )
    res4 = ps4.results()
"""
