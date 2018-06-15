# coding: UTF-8
'''
Created on 2016年7月3日

@author: taoqu_000
'''
import datetime, calendar
import math
import os, sys, time
from posixpath import join as urljoin
from configobj import ConfigObj
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset, stringtoarr
from numpy.lib.polynomial import polyfit
from numpy.ma.core import std, mean
from numpy.ma.extras import corrcoef
from scipy.interpolate.fitpack2 import InterpolatedUnivariateSpline
from PB import pb_time
from PB.CSC.pb_csc_console import LogServer
import numpy as np
from multiprocessing import Pool , Lock

def run(matching, ymd):
    part1 = matching.split('_')[0]
    if 'FY2' in part1:
        run_GEO_LEO(matching, ymd)

def run_GEO_LEO(matching, ymd):
    Log.info(u'[%s] [%s]' % (matching, ymd))
    # 解析配置文件

    opath = inCfg['PATH']['OUT']['ISN']

    nc = GSICS_NC_NRTC(ymd, matching, opath)
    nc.loadMatchedPointNc()
    nc.calculate_LUT()  # zt add 20160825
    if nc.error == False:
        nc.create()
        nc.write()
        nc.close()
        Log.info(u'Success')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getTime_Now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

#==============================================================================
# 计算斜率和截距
#==============================================================================
def G_reg1d(xx, yy, ww=None):
    ''' 
    计算斜率和截距 
    ww: weights
    '''
    rtn = []
    ab = polyfit(xx, yy, 1, w=ww)
    rtn.append(ab[0])
    rtn.append(ab[1])
    rtn.append(std(yy) / std(xx))
    rtn.append(mean(yy) - rtn[2] * mean(xx))
    r = corrcoef(xx, yy)
    rr = r[0, 1] * r[0, 1]
    rtn.append(rr)
    return rtn

def cal_RAC(x_leo, y_geo, delta):

    x = np.array(x_leo)
    y = np.array(y_geo)
    dt = np.array(delta)

    a1 = np.sum(np.square(x) / np.square(dt))
    a2 = np.sum(y / np.square(dt))
    b1 = np.sum(x / np.square(dt))
    b2 = np.sum(x * y / np.square(dt))
    c1 = np.sum(1 / np.square(dt))

    d1 = (c1 * a1 - b1 * b1)

    a = (a1 * a2 - b1 * b2) / d1
    b = (c1 * b2 - b1 * a2) / d1

    offset_se = a1 / d1
    slope_se = c1 / d1
    cov_ab = -b1 / d1

    return a, b, offset_se, slope_se, cov_ab

FV = -999
class GSICS_NC_NRTC(object):
    def __init__(self, ymd, matching, output_root_dir):

        self.error = False
        self.matching = matching
        part1, part2 = matching.split('_')
        self.sat1 , self.sen1 = part1.split("+")
        self.sat2 , self.sen2 = part2.split("+")

        # 命名转成国际规则
        if self.sat1.startswith("FY2"): self.sen1 = "SVISSR"  # VISSR -> SVISSR
        if self.sat2.startswith("METOP"): self.sat2 = self.sat2.replace("METOP-", "MetOp")  # METOP -> MetOp

        self.ymd = ymd
        self.hms = "000000"
        self.y_m_d = "%s-%s-%s" % (ymd[:4], ymd[4:6], ymd[6:])

        self.nc_dir = os.path.join(output_root_dir, self.matching)
        self.nc_name = 'W_CN-CMA-NSMC,SATCAL+%s+GEOLEOIR,%s+%s-%s+%s_C_BABJ_%s%s_demo_01.nc' % \
                        ('NRTC', self.sat1, self.sen1, self.sat2, self.sen2, self.ymd, self.hms)
        self.nc_path = os.path.join(self.nc_dir, self.nc_name)

        Tbb2Rad_filename = '%s_RADA_TBB.txt' % self.sat1
        Tbb2Rad_fp = os.path.join(PARAM_DIR, Tbb2Rad_filename)
        self.Rad_Tbb_data = np.loadtxt(Tbb2Rad_fp, ndmin=2)

        self.conf = nrtcCfg
        self.ndays = int(self.conf['%s+%s' % (self.sat1, self.sen1)]['_ndays'])
        self.changeYMD = self.conf['%s+%s' % (self.sat1, self.sen1)]["_change"]

        self.Custom_Global_Attrs = {}
        self.set_Custom_Global_Attrs()
        self.set_history()

        # init
        self.std_scene_tb = [float (e) for e in self.conf['%s+%s' % (self.sat1, self.sen1)]['std_scene_tb']['std_scene_tb'] ]
        self.Tb_bias = [FV, FV, FV, FV]
        self.slope = [FV, FV, FV, FV]
        self.slope_se = [FV, FV, FV, FV]
        self.offset = [FV, FV, FV, FV]
        self.offset_se = [FV, FV, FV, FV]
        self.std_scene_tb_bias_se = [FV, FV, FV, FV]
        self.covariance = [FV, FV, FV, FV]
        self.number_of_collocations = [FV, FV, FV, FV]

        self.cal_lut = None
        self.a_lut = [FV, FV, FV, FV]
        self.b_lut = [FV, FV, FV, FV]

    def loadMatchedPointNc(self):
        '''
        读取匹配点NC文件
        '''
        for ib in xrange(1, 5):
            x_leo = None
            y_geo = None
            weight = None

            x_dn = None
            y_rad = None
            weight_dn = None

            for n in range(self.ndays):
                nc_dt = datetime.date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8])) + \
                        datetime.timedelta(days=n * -1)
                nc_ymd = nc_dt.strftime("%Y%m%d")
                oname = 'COLLOC+GEOLEOIR,%s_C_BABJ_%s.NC' % (self.matching, nc_ymd)
                # read matchedpoint from NC
#                 matchedpoint_nc = urljoin(MATCH_DIR, self.matching, nc_ymd + '.NC')
                matchedpoint_nc = urljoin(MATCH_DIR, self.matching, oname)

                if not os.path.isfile(matchedpoint_nc):
                    continue
                ncFile = Dataset(matchedpoint_nc, 'r', format='NCETCDF4_CLASSIC')  # 'NCETCDF4'

                chan = 'CH_%02d' % ib

                GeoRADFov = ncFile.groups[chan].variables['GeoRADFov'][:]
                geoRad = GeoRADFov[:, 0]
                geoRadStd = GeoRADFov[:, 1]
                GeoDNFov = ncFile.groups[chan].variables['GeoDNFov'][:]
                geoDN = GeoDNFov[:, 0]
                geoDNStd = GeoDNFov[:, 1]
                leoRad = ncFile.groups[chan].variables['SimGeoRad'][:, 0]
                GeoTime = ncFile.groups[chan].variables['GeoTime'][:, 0]

                # 时间过滤: band1-3保留白天  band4保留晚上
                jd = GeoTime / 24. / 3600.
                hour = ((jd - jd.astype('int8')) * 24).astype('int8')
                if ib <= 3:
                    # 2018/06/15 anning 修改: IASI 所有通道只要晚上数据，不要白天数据
                    if "IASI" in self.matching:
                        index = hour >= 10
                    else:
                        index = (hour < 10)  # utc hour < 10 is day
                else:
                    index = (hour >= 10)
                index = np.logical_and(index, geoRadStd > 0)

                if x_leo is None:
                    x_leo = leoRad[index]
                    y_geo = geoRad[index]
                    weight = geoRadStd[index]
                else:
                    x_leo = np.concatenate((x_leo, leoRad[index]))
                    y_geo = np.concatenate((y_geo, geoRad[index]))
                    weight = np.concatenate((weight, geoRadStd[index]))

                if x_dn is None:
                    x_dn = geoDN[index]
                    y_rad = leoRad[index]
                    weight_dn = geoDNStd[index]
                else:
                    x_dn = np.concatenate((x_dn, geoDN[index]))
                    y_rad = np.concatenate((y_rad, leoRad[index]))
                    weight_dn = np.concatenate((weight_dn, geoRadStd[index]))

                if nc_ymd in self.changeYMD:
                    break

            if x_leo is not None and len(x_leo) > 10:
                self.calculate(ib, x_leo, y_geo, weight)
            else:
                self.error = True

            if x_dn is not None and len(x_dn) > 10:
                self.calculate_ab_LUT(ib, x_dn, y_rad, weight)

    def calculate(self, ib, x_leo, y_geo, weight):

        Tb_reference = self.std_scene_tb[ib - 1]  # 标准温度
        # 业务的辐射比对回归系数，自变量（横轴是FY2_RAD)
        RadCompare_coeff = G_reg1d(y_geo, x_leo, 1.0 / weight)

        # 相关性太低的结果不要输出，IR1~3>0.9，IR4>0.7
        if ib <= 3 and RadCompare_coeff[4] < 0.9:
            return
        elif ib == 4 and RadCompare_coeff[4] < 0.7:
            return
        # Equation 7~11
        aa, bb, offset_se, slope_se, cov_ab = cal_RAC(x_leo, y_geo, weight)
        dta = math.sqrt(offset_se)
        dtb = math.sqrt(slope_se)

        # 标准温度 -> RAD
        LGEO = InterpolatedUnivariateSpline(self.Rad_Tbb_data[:, 0], self.Rad_Tbb_data[:, ib])(Tb_reference)

        # 计算 std_scene_tb_bias_se
        delta_leo = math.sqrt((dta / bb) ** 2 + ((LGEO - aa) * dtb) ** 2 - 2 * (LGEO - aa) / bb * cov_ab)  # Equation 3
        Tb_plus_delta = InterpolatedUnivariateSpline(self.Rad_Tbb_data[:, ib], self.Rad_Tbb_data[:, 0])(LGEO + delta_leo)  # RAD -> TB
        std_scene_tb_bias_se = abs(Tb_reference - Tb_plus_delta)  # abs

        self.slope_se[ib - 1] = dtb
        self.offset_se[ib - 1] = dta
        self.std_scene_tb_bias_se[ib - 1] = std_scene_tb_bias_se
        self.covariance[ib - 1] = cov_ab

        # 业务的参考温度处的亮温偏差
        # because LGEO = b*LGEO_corrected + a, so LGEO_corrected = (LGEO - a) / b

        LGEO_corrected = (LGEO - aa) / bb
        Tb_corrected = InterpolatedUnivariateSpline(self.Rad_Tbb_data[:, ib], self.Rad_Tbb_data[:, 0])(LGEO_corrected)
        Tb_bias = Tb_reference - Tb_corrected  # FY2 - 标准
        self.Tb_bias[ib - 1] = Tb_bias

        self.slope[ib - 1] = RadCompare_coeff[0]
        self.offset[ib - 1] = RadCompare_coeff[1]
        self.number_of_collocations[ib - 1] = y_geo.size

    def calculate_ab_LUT(self, ib, x_dn, y_rad, weight):
        # X轴 FY2_DN; Y轴 leoRad
        coeff = G_reg1d(x_dn, y_rad, 1.0 / weight)
        # 相关性太低的结果不要输出，IR1~3>0.9，IR4>0.7
        if ib <= 3 and coeff[4] < 0.9:
            return
        elif ib == 4 and coeff[4] < 0.7:
            return
        self.a_lut[ib - 1] = coeff[0]
        self.b_lut[ib - 1] = coeff[1]

    def calculate_LUT(self):
        dn = np.arange(0, 1024, 1)
        lut = []
        for ib in xrange(1, 5):
            aa = self.a_lut[ib - 1]
            bb = self.b_lut[ib - 1]
            if aa == FV and bb == FV:
                tbb = np.full_like(dn, FV)
            else:
                rad = aa * dn + bb
                tbb = InterpolatedUnivariateSpline(self.Rad_Tbb_data[:, ib], self.Rad_Tbb_data[:, 0])(rad)

                # IR1\2\4 180~350K, IR3 180~300K
                if ib == 3:
                    idx = tbb > 300
                    tbb[idx] = 300.
                    idx = tbb < 180
                    tbb[idx] = 180.
                else:
                    idx = tbb > 350
                    tbb[idx] = 350.
                    idx = tbb < 180
                    tbb[idx] = 180.
            lut.append(tbb)

        self.cal_lut = np.array(lut).transpose()

    def create(self):
        if not os.path.isdir(self.nc_dir):
            os.makedirs(self.nc_dir)
        self.rootgrp = Dataset(self.nc_path, 'w', format='NETCDF3_CLASSIC')  # why not use "NETCDF4"

    def set_history(self):
        '''
        历史属性设定，提出来方便修改
        '''
        self.Custom_Global_Attrs["history"] = \
        """none"""

    def set_Custom_Global_Attrs(self):
        '''
        非固定不变的属性
        '''
        self.Custom_Global_Attrs["title"] = \
        "GSICS %s+%s vs %s+%s GSICS Near Real-Time Correction" % \
        (self.sat1, self.sen1, self.sat2, self.sen2)

        self.Custom_Global_Attrs["keywords"] = \
        "GSICS, satellite, remote sensing, inter-calibration, near real time correction, " + \
        "GEO-LEO-IR, %s+%s, %s+%s, infrared" % \
        (self.sat1, self.sen1, self.sat2, self.sen2)

        self.Custom_Global_Attrs["monitored_instrument"] = "%s %s" % (self.sat1, "S-VISSR")  # zt modified
        self.Custom_Global_Attrs["reference_instrument"] = "%s %s" % (self.sat2, self.sen2)

        str_now = getTime_Now()
        self.Custom_Global_Attrs["date_created"] = str_now
        self.Custom_Global_Attrs["date_modified"] = str_now

        self.Custom_Global_Attrs["id"] = self.nc_name

        # "time_coverage" same as "validity_period"
        date_1 = datetime.date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8])) + \
                datetime.timedelta(days=(self.ndays - 1) * -1)
        date_2 = datetime.date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8]))
        self.Custom_Global_Attrs["time_coverage_start"] = '%sT00:00:00Z' % date_1.strftime('%Y-%m-%d')
        self.Custom_Global_Attrs["time_coverage_end"] = '%sT23:59:59Z' % date_2.strftime('%Y-%m-%d')

    def write_Global_Attr(self):
        '''
        写全局属性
        '''
        attrs = self.conf['GLOBAL']
        for eachkey in attrs:
            if attrs[eachkey] == 'DUMMY':
                attrs[eachkey] = self.Custom_Global_Attrs[eachkey]
            if is_number(attrs[eachkey]):
                if '.' in attrs[eachkey]:
                    self.rootgrp.setncattr(eachkey, np.float32(attrs[eachkey]))
                else:
                    self.rootgrp.setncattr(eachkey, np.short(attrs[eachkey]))
            else:
                self.rootgrp.setncattr(eachkey, attrs[eachkey])

    def add_Dimensions(self):
        var_lst = self.conf['%s+%s' % (self.sat1, self.sen1)]
        self.rootgrp.createDimension('chan', int(var_lst['_chan']))  # band num
        self.rootgrp.createDimension('chan_strlen', int(var_lst['_chan_strlen']))  # band name length
        self.rootgrp.createDimension('date', None)  # None: UNLIMITED
        self.rootgrp.createDimension('validity', 2)
        self.rootgrp.createDimension('lut_row', int(var_lst['_lut_row']))

    def add_Variables(self):
        '''
        根据配置文件内容添加数据集
        '''
        var_lst = self.conf['%s+%s' % (self.sat1, self.sen1)]
        for eachVar in var_lst:
            if eachVar.startswith('_'): continue
            var_info = var_lst[eachVar]

            var = self.rootgrp.createVariable(eachVar, var_info['_fmt'], var_info['_dims'])
            for eachKey in var_info:
                if eachKey.startswith('_'): continue
                if eachKey == eachVar:
                    if var_info['_fmt'] == 'S1':
                        # 字符串
                        # 需要将字符串用stringtoarr转成char的数组，再写入NC !!!
                        char_len = 1
                        for each in var_info['_dims']:
                            char_len = char_len * int(var_lst['_%s' % each])  # 计算字符总个数
                        char_ary = stringtoarr(''.join(var_info[eachKey]), char_len)
                        var[:] = char_ary
                    else:
                        # 非字符串
                        var[:] = var_info[eachKey]
                else:
                    if is_number(var_info[eachKey]):
                        if '.' in var_info[eachKey]:
                            var.setncattr(eachKey, np.float32(var_info[eachKey]))
                        else:
                            var.setncattr(eachKey, np.short(var_info[eachKey]))
                    else:
                        var.setncattr(eachKey, var_info[eachKey])


    def write_Variables_Value(self):
        '''
        写数据集内容，这些内容是非固定不变的
        '''
        # central_wavelength
        wnc = self.conf['%s+%s' % (self.sat1, self.sen1)]['wnc']['wnc']
        wnc = [float(each) for each in wnc]

        c_w = np.divide([1.] * 4, wnc) * 0.01
#         c_w = ['%.2e' % each for each in c_w]
        self.rootgrp.variables['central_wavelength'][:] = c_w

        # date
        ymdhms = '%s%s' % (self.ymd, self.hms)
        d1 = time.strptime(ymdhms, '%Y%m%d%H%M%S')
        dt = calendar.timegm(d1)
        self.rootgrp.variables['date'][0] = [dt, float(ymdhms)]

        # validity_period
        date_1 = datetime.date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8])) + \
                datetime.timedelta(days=-7)
        d1 = time.strptime('%s%s' % (date_1.strftime('%Y%m%d'), self.hms), '%Y%m%d%H%M%S')
        v1 = calendar.timegm(d1)

        date_2 = datetime.date(int(self.ymd[0:4]), int(self.ymd[4:6]), int(self.ymd[6:8]))
        d2 = time.strptime('%s%s' % (date_2.strftime('%Y%m%d'), '235959'), '%Y%m%d%H%M%S')
        v2 = calendar.timegm(d2)
        self.rootgrp.variables['validity_period'][0] = [v1, v2]

        # slope
        self.rootgrp.variables['slope'][0] = self.slope
        # slope_se
        self.rootgrp.variables['slope_se'][0] = self.slope_se
        # offset
        self.rootgrp.variables['offset'][0] = self.offset
        # offset_se
        self.rootgrp.variables['offset_se'][0] = self.offset_se
        # covariance
        self.rootgrp.variables['covariance'][0] = self.covariance

        # std_scene_tb
        self.rootgrp.variables['std_scene_tb'][:] = self.std_scene_tb
        # std_scene_tb_bias
        self.rootgrp.variables['std_scene_tb_bias'][0] = self.Tb_bias
        # std_scene_tb_bias_se
        self.rootgrp.variables['std_scene_tb_bias_se'][0] = self.std_scene_tb_bias_se
        # number_of_collocations
        self.rootgrp.variables['number_of_collocations'][0] = self.number_of_collocations
        # cal_lut
        self.rootgrp.variables['CAL_LUT'][:] = self.cal_lut
        self.rootgrp.variables['CAL_slope'][0] = self.a_lut
        self.rootgrp.variables['CAL_offset'][0] = self.b_lut

    def write(self):
        self.write_Global_Attr()
        self.add_Dimensions()
        self.add_Variables()
        self.write_Variables_Value()

    def close(self):
        self.rootgrp.close()
######################### 程序全局入口 ##############################

# 获取程序参数接口
args = sys.argv[1:]
help_info = \
    u'''
    [参数样例1]：SAT1+SENSOR1_SAT2+SENSOR2  YYYYMMDD-YYYYMMDD
    [参数样例2]：不跟参数自动处理所有pair
    '''
if '-h' in args:
    print help_info
    sys.exit(-1)

# 获取程序所在位置，拼接配置文件
MainPath, MainFile = os.path.split(os.path.realpath(__file__))
ProjPath = os.path.dirname(MainPath)
cfgFile = os.path.join(ProjPath, 'cfg', 'global.cfg')
nrtcCfg = ConfigObj(os.path.join(MainPath, 'FY2X_NRTC.attr'))
# 配置不存在预警
if not os.path.isfile(cfgFile):
    print (u'配置文件不存在 %s' % cfgFile)
    sys.exit(-1)
# 载入配置文件
inCfg = ConfigObj(cfgFile)
PARAM_DIR = inCfg['PATH']['PARAM']
MATCH_DIR = inCfg['PATH']['MID']['MATCH_DATA']
LogPath = inCfg['PATH']['OUT']['LOG']
Log = LogServer(LogPath)

# 开启进程池
threadNum = int(inCfg['CROND']['threads'])
pool = Pool(processes=threadNum)

if len(args) == 2:
    Log.info(u'手动NRTC产品生成程序开始运行-----------------------------')
    satPair = args[0]
    str_time = args[1]
    date_s, date_e = pb_time.arg_str2date(str_time)

    while date_s <= date_e:
        ymd = date_s.strftime('%Y%m%d')
        if threadNum == 1:
            run(satPair, ymd)
        else:
            pool.apply_async(run, (satPair, ymd))
        date_s = date_s + relativedelta(days=1)
    pool.close()
    pool.join()

elif len(args) == 0:

    Log.info(u'自动NRTC产品生成程序开始运行 -----------------------------')
    rolldays = inCfg['CROND']['rolldays']
    pairLst = inCfg['PAIRS'].keys()
    for satPair in pairLst:
        for rdays in rolldays:
            ymd = (datetime.datetime.utcnow() - relativedelta(days=int(rdays))).strftime('%Y%m%d')
            pool.apply_async(run, (satPair, ymd))
    pool.close()
    pool.join()
else:
    print 'args nums 1 or 2'
    sys.exit(-1)
