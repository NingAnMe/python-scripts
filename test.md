背景不同卫星在固定点进行定标匹配，需要以固定点的经纬度为中心点，提取X*X范围大小的数据，降低数据量，对数据进行清理。复用率高，显著提高定标时对数据的使用效率。总体
	* 调度

		* 每次调度计算一个最小单元，做到进程间互不影响
		* 集群分布式调度
	* 读取：不同卫星传感器使用不同的数据读取类
	* 数据清理：

		* 统一填充值

			* 整型：小于16bit ：范围内最大正值，大于等于16bit，32767
			* 无符号整型：小于16bit范围内的最大值，大于等于16bit，65535
			* 浮点型：65535.0
		* 插值，统一数据集大小
	* 固定点数据处理：

		* 查找距离固定点最近的经纬度点： scipy.spatial.cKDTree
		* 读取固定点X*X范围大小的数据
		* 进行统计计算: mean std
	* 输出

		* 不同传感器的HDF创建类
		* 文件名：{sat}_{sensor}_{fix_name}_{lon:}_{lat}_{window}X{window}.HDF

读取类
	* 属性

		* shape  # 数据的shape
		* 分通道

			* DN
			* SV
			* REF
			* RAD
			* TBB
			* BB
		* 不分通道

			* Height
			* LandCover
			* LandSeaMask
			* Latitude
			* Longitude
			* SensorAzimuth
			* SensorZenith
			* SolarAzimuth
			* SolarZenith
			* RelativeAzimuth
			* Time
		* 不确定

			* coeff_k0
			* coeff_k1
			* coeff_k2


提取类
	*
属性

		*
error = boolean
		*
ymd = str
		*
hm = str
		*
latitude = []
		*
longitude = []



		*
data = {}
		*
result = {}
	*
方法

		*
extrat()
		*
load_data()
		*
write_hdf5()



难点
	*
不同卫星的数据处理之间差异很大，需要针对每个卫星的数据进行数据的范围纠正和排除无效值，并且规整为相同的格式。
	*
时效性要求很高，故使用集群进行处理。
	*
cKDTree 的时候，数据大小超过100W，需要分份计算，否则计算不出来
	*
优化，先取出固定点1°范围内的点，再进行 cKDTree 计算，比分块的计算要快



程序使用
	1.
继承 Extract 类实现传感器提取子类，实现子类的 load_data() 方法，

