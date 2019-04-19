import matplotlib.image as img

class PlotFigure(object):
    def __init__(self):
        pass

    @classmethod
    def add_ax(cls, fig, pos_x, pos_y, width, height):
        """
        添加子图ax
        :param fig: plt.figure
        :param pos_x: 左下角位置 百分比形式
        :param pos_y: 左下角位置 百分比形式
        :param width: 子图宽 百分比形式
        :param height: 子图高 百分比形式
        :return:
        """
        return fig.add_axes([pos_x, pos_y, width, height])

    @classmethod
    def add_image(cls, fig, imgsize, image_path, position='LB'):
        """
        :param fig: matplotlib.figure
        :param imgsize: (width, high)
        :param image_path:
        :param position: 'LB' or 'RB'
        :return:
        """
        img_width, img_high = imgsize
        if position == 'LB':
            rect = [0, 0, img_width, img_high]
        elif position == 'RB':
            rect = [1. - img_width, 0, img_width, img_high]
        else:
            raise KeyError
        image = img.imread(image_path)
        ax = fig.add_axes(rect, anchor='C')
        ax.axis('off')
        ax.imshow(image)
        return fig, ax

# ####################################### PLOT LOGO
LOGO_LEFT = os.path.join(get_gsics_lib_path(), 'logoL.jpg')  # 没有填None
LOGO_RIGHT = os.path.join(get_gsics_lib_path(), 'logoR.jpg')  # 没有填None

fig = plt.figure(figsize=figsize, dpi=dpi)

plot_fig = PlotFigure()
img_width = 0.1
img_high = float(figsize[0]) / float(figsize[1]) * img_width
img_size = (img_width, img_high)
if LOGO_LEFT:
	plot_fig.add_image(fig, img_size, LOGO_LEFT, position='LB')
if LOGO_RIGHT:
	plot_fig.add_image(fig, img_size, LOGO_RIGHT, position='RB')